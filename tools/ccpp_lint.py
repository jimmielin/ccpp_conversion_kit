#!/usr/bin/env python3
"""ccpp_lint.py -- static checks for atmospheric_physics code-review rules.

Implements the code-review rules Jesse commonly checks on CAM-SIMA / CCPP
physics (atmospheric_physics), limited to what a static linter can do
faithfully. This is deliberately separate from f90_house_style.py, which
enforces a personal formatting preference; nothing here reformats code.

Reliable rules (always on):
  module-save      no `save` at module scope (statement or attribute)
  end-keyword      `end do`/`end if`, not `enddo`/`endif`
  old-operator     modern relationals (`>` not `.gt.`, `==` not `.eq.`, ...)
  allocate-stat    every `allocate` passes `stat=`
  allocate-errmsg  every `allocate` passes `errmsg=`
  alloc-unchecked  the `stat=` variable is referenced (checked) after allocate
  char-len-star    character dummy args are `len=*` (unless allocatable/pointer)
  goto             no `goto` / `go to`
  meta-char-len    a character dummy arg's `len` matches its `.meta` `kind=len=`
  namelist-block   namelist XML has the standard leading comment block

Experimental heuristics (--experimental; noisy, meant to guide a human):
  use-scope        module `use ..., only:` whose symbols are used in one proc
  pure-candidate   procedure with no I/O, call, stop, or save -- maybe `pure`
  citation-doi     citation-looking comment with no DOI

Intentionally NOT implemented (needs semantics / NLP a static linter lacks):
  - full-sentence comment grammar (needs a grammar checker / LLM)
  - single-output subroutine -> function (invasive interface change; by hand)
  - the "non-zero stat sets ccpp_error_* and returns" wiring is only
    approximated by `alloc-unchecked` (stat never referenced again); the actual
    error-return code path still needs human eyes.

Usage:
  ccpp_lint.py [--experimental] [--fix] PATH [PATH ...]
  ccpp_lint.py --diff [REV] [--whole-file] [--experimental] [--fix] [PATH ...]
  ccpp_lint.py --list-rules
Paths may be files or directories (recursed for *.F90 and *namelist*.xml). A
*.meta path is linted through its partner *.F90, which is where the metadata
pairing rule reads the Fortran declarations from.

--fix rewrites files in place for the two mechanical rules, old-operator and
end-keyword. Both are within-line token substitutions on code only (string
literals, comments, and `#` preprocessor lines are left alone), so they cannot
change semantics. Combined with --diff, only the changed lines are rewritten,
which keeps a legacy file's untouched lines out of the diff. Every other rule
needs human judgement and is reported, never rewritten.

--diff REV lints only files changed vs REV (default: main) using PR/merge-base
semantics (REV...HEAD), and reports only findings on the added/changed lines --
so lightly editing a legacy file does not re-surface its pre-existing issues.
File-level checks (namelist-block, meta-char-len) still run for any touched
file, and a changed *.meta pulls in its partner *.F90 so a metadata-only edit
is still checked. Pass
--whole-file to report every finding in the changed files instead. An optional
PATH restricts --diff to that subtree (repo is inferred from PATH, else CWD).

Exit status is 1 if any finding is reported, else 0.
"""

import argparse
import os
import re
import subprocess
import sys

RULES = {
    'module-save': "no `save` at module scope",
    'end-keyword': "`end do`/`end if` not `enddo`/`endif`",
    'old-operator': "modern relational operators (`>` not `.gt.`)",
    'allocate-stat': "`allocate` must pass `stat=`",
    'allocate-errmsg': "`allocate` must pass `errmsg=`",
    'alloc-unchecked': "the `stat=` result must be checked",
    'char-len-star': "character dummy arguments must be `len=*`",
    'goto': "no `goto` / `go to`",
    'meta-char-len': "character `len` must match the paired `.meta`",
    'namelist-block': "namelist XML needs the standard comment block",
    'use-scope': "[exp] `use` should be at the lowest necessary scope",
    'pure-candidate': "[exp] procedure may qualify for `pure`",
    'citation-doi': "[exp] citation should carry a DOI",
}

RELATIONAL = {'gt': '>', 'lt': '<', 'ge': '>=', 'le': '<=', 'eq': '==', 'ne': '/='}

# `end <kw>` that closes a construct, not a program unit (so it must not pop the
# unit stack). `block` is here too, but `end block data` is handled specially.
CONSTRUCT_ENDS = {'do', 'if', 'select', 'where', 'associate', 'forall',
                  'critical', 'team', 'enum', 'block'}

NAMELIST_MARKER = 'Each namelist variable is defined'


# --------------------------------------------------------------------------
# Lexing helpers
# --------------------------------------------------------------------------

def blank_strings_and_comment(line):
    """Split a physical line into (code, comment, nostr).

    `comment` runs from the first out-of-string '!' to end (incl. '!'), or ''.
    `nostr` is `code` with the contents of string literals blanked to spaces
    (delimiters kept) so structural scans ignore quoted '!', '::', parens, '&'.
    len(nostr) == len(code).
    """
    in_str = None
    nostr = []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if in_str:
            if c == in_str:
                if i + 1 < n and line[i + 1] == in_str:  # doubled quote
                    nostr.append('  ')
                    i += 2
                    continue
                in_str = None
                nostr.append(c)
            else:
                nostr.append(' ')
        elif c in '\'"':
            in_str = c
            nostr.append(c)
        elif c == '!':
            return line[:i], line[i:], ''.join(nostr)
        else:
            nostr.append(c)
        i += 1
    return line, '', ''.join(nostr)


def match_paren(s, i):
    """Given s[i] == '(', return the index of the matching ')', or -1."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '(':
            depth += 1
        elif s[j] == ')':
            depth -= 1
            if depth == 0:
                return j
    return -1


def split_commas(s):
    """Split `s` on commas at paren depth 0."""
    out, depth, start = [], 0, 0
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == ',' and depth == 0:
            out.append(s[start:i])
            start = i + 1
    out.append(s[start:])
    return out


def find_top(s, token):
    """Index of the first `token` in `s` at paren depth 0, or -1."""
    depth = 0
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0 and s.startswith(token, i):
            return i
    return -1


def statements(lines):
    """Yield (lineno, code, nostr) logical statements.

    Continuation lines (trailing '&') are merged, interspersed comment/blank
    lines inside a continuation are dropped, and statements joined by ';' are
    split. `lineno` is the 1-based physical line where the statement starts.
    Preprocessor (`#`) lines are skipped. `code` has comments stripped;
    `nostr` is the string-blanked form of `code`.
    """
    pend_c, pend_n, start, expecting = '', '', None, False
    for idx, raw in enumerate(lines, 1):
        if raw.lstrip().startswith('#'):
            if pend_c.strip():
                yield from _split_semi(start, pend_c, pend_n)
            pend_c, pend_n, start, expecting = '', '', None, False
            continue
        code, _cmt, nostr = blank_strings_and_comment(raw)
        if expecting and not code.strip():
            continue                       # comment/blank within a continuation
        if not pend_c and not code.strip():
            continue                       # blank/comment between statements
        c, n = code, nostr
        if expecting:
            ls = c.lstrip()
            if ls.startswith('&'):
                off = len(c) - len(ls)
                c = c[:off] + ls[1:]
                n = n[:off] + n[off + 1:]
        if start is None:
            start = idx
        cr = c.rstrip()
        if cr.endswith('&'):
            c = c[:len(cr) - 1]
            n = n[:len(cr) - 1]
            expecting = True
        else:
            expecting = False
        pend_c += c
        pend_n += n
        if not expecting:
            yield from _split_semi(start, pend_c, pend_n)
            pend_c, pend_n, start = '', '', None
    if pend_c.strip():
        yield from _split_semi(start, pend_c, pend_n)


def _split_semi(start, code, nostr):
    depth, seg = 0, 0
    for i, ch in enumerate(nostr):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ';' and depth == 0:
            if code[seg:i].strip():
                yield (start, code[seg:i], nostr[seg:i])
            seg = i + 1
    if code[seg:].strip():
        yield (start, code[seg:], nostr[seg:])


# --------------------------------------------------------------------------
# Surface (per-line) rules: end-keyword, old-operator, goto
# --------------------------------------------------------------------------

def scan_surface(path, lines, findings):
    for lineno, raw in enumerate(lines, 1):
        if raw.lstrip().startswith('#'):
            continue                       # leave C-preprocessor #endif alone
        _code, _cmt, nostr = blank_strings_and_comment(raw)
        low = nostr.lower()
        for m in re.finditer(r'\bend(do|if)\b', low):
            kw = m.group(1)
            findings.append((path, lineno, 'end-keyword',
                             "use `end %s` instead of `end%s`" % (kw, kw)))
        for m in re.finditer(r'\.(gt|lt|ge|le|eq|ne)\.', low):
            op = m.group(1)
            findings.append((path, lineno, 'old-operator',
                             "use `%s` instead of `.%s.`" % (RELATIONAL[op], op)))
        for _m in re.finditer(r'\bgo\s*to\b', low):
            findings.append((path, lineno, 'goto',
                             "remove `go to` / `goto`"))


# --------------------------------------------------------------------------
# Autofix for the purely mechanical surface rules
# --------------------------------------------------------------------------

# Rules `--fix` can rewrite. Both are within-line, token-for-token edits that
# cannot change semantics, so line numbers never shift and no other rule's
# findings move. Everything else (goto, module-save, ...) needs human judgement.
FIXABLE_RULES = ('old-operator', 'end-keyword')


def _match_case(template, text):
    """Return `text` recased to follow `template` (all-upper or otherwise)."""
    return text.upper() if template.isupper() else text


def fix_line(raw):
    """Rewrite one physical line for the fixable rules; return (new, nfixed)."""
    if raw.lstrip().startswith('#'):
        return raw, 0                      # leave C-preprocessor #endif alone
    _code, _cmt, nostr = blank_strings_and_comment(raw)
    low = nostr.lower()
    edits = []                             # (start, end, replacement)
    for m in re.finditer(r'\bend(do|if)\b', low):
        edits.append((m.start(), m.end(),
                      _match_case(raw[m.start():m.end()],
                                  'end ' + m.group(1))))
    for m in re.finditer(r'\.(gt|lt|ge|le|eq|ne)\.', low):
        edits.append((m.start(), m.end(), RELATIONAL[m.group(1)]))
    if not edits:
        return raw, 0
    out = raw
    for start, end, repl in sorted(edits, reverse=True):   # right-to-left
        out = out[:start] + repl + out[end:]
    return out, len(edits)


def fix_file(path, allowed_lines):
    """Apply fixable-rule rewrites in place; return the number of fixes.

    `allowed_lines` restricts fixes to those line numbers (used by --diff);
    pass None to fix the whole file.
    """
    text = read_text(path)
    lines = text.splitlines(keepends=True)
    total = 0
    for i, raw in enumerate(lines):
        if allowed_lines is not None and (i + 1) not in allowed_lines:
            continue
        body = raw.rstrip('\r\n')
        new, n = fix_line(body)
        if n:
            lines[i] = new + raw[len(body):]
            total += n
    if total:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
    return total


# --------------------------------------------------------------------------
# Structural rules (need scope + logical statements)
# --------------------------------------------------------------------------

def parse_args(rest):
    """Dummy-argument names from the '(...)' following a procedure name."""
    i = rest.find('(')
    if i < 0:
        return set()
    j = match_paren(rest, i)
    inner = rest[i + 1:(j if j >= 0 else len(rest))]
    args = set()
    for part in split_commas(inner):
        mm = re.match(r'\s*(\w+)', part)
        if mm:
            args.add(mm.group(1))
    return args


def classify_opener(low):
    """Return (kind, name, dummies, is_pure) if `low` opens a program unit."""
    s = low.lstrip()
    m = re.match(r'module\s+(\w+)\s*$', s)
    if m and m.group(1) not in ('procedure', 'subroutine', 'function'):
        return ('module', m.group(1), set(), False)
    if re.match(r'submodule\s*\(', s):
        nm = re.search(r'\)\s*(\w+)', s)
        return ('submodule', nm.group(1) if nm else '', set(), False)
    m = re.match(r'program\s+(\w+)', s)
    if m:
        return ('program', m.group(1), set(), False)
    m = re.match(r'((?:(?:pure|impure|elemental|recursive|non_recursive|module)'
                 r'\s+)*)subroutine\s+(\w+)\b(.*)', s)
    if m:
        return ('subroutine', m.group(2), parse_args(m.group(3)),
                bool(re.search(r'\b(pure|elemental)\b', m.group(1))))
    if not s.startswith('end'):
        fm = re.search(r'\bfunction\s+(\w+)\s*\(', s)
        if fm and re.match(r'[\w\s()*:,=]*\bfunction\b', s):
            return ('function', fm.group(1), parse_args(s[fm.start():]),
                    bool(re.search(r'\b(pure|elemental)\b', s[:fm.start()])))
    if re.match(r'(abstract\s+)?interface\b', s):
        return ('interface', '', set(), False)
    if re.match(r'block\s*data\b', s):
        return ('blockdata', '', set(), False)
    if (re.match(r'type\b\s*(?:,|::|\s+[a-z])', s)
            and not re.match(r'type\s+is\b', s)
            and not re.match(r'type\s*\(', s)):
        return ('type', '', set(), False)
    return None


def is_closer(s):
    """True if statement `s` (lstripped, lowercased) closes a program unit."""
    if s == 'end':
        return True
    m = re.match(r'end\s+(\w+)', s)
    if m:
        kw = m.group(1)
        if kw == 'block' and re.match(r'end\s+block\s+data\b', s):
            return True
        return kw not in CONSTRUCT_ENDS
    if re.match(r'end(subroutine|function|module|submodule|program|interface|'
                r'type|procedure|blockdata)\b', s):
        return True
    return False


def parse_use(s, lineno):
    """Parse a `use ..., only: ...` statement into (lineno, module, [locals])."""
    m = re.match(r'use\b\s*(?:,\s*(?:non_)?intrinsic\s*)?(?:::\s*)?(\w+)(.*)', s)
    if not m:
        return None
    om = re.search(r'\bonly\s*:(.*)', m.group(2))
    if not om:
        return None                        # whole-module import: can't analyze
    syms = []
    for part in split_commas(om.group(1)):
        p = part.strip()
        if not p or p.startswith(('operator', 'assignment')):
            continue
        local = p.split('=>')[0].strip() if '=>' in p else p
        mm = re.match(r'(\w+)', local)
        if mm:
            syms.append(mm.group(1))
    return (lineno, m.group(1), syms)


def check_module_save(s):
    """Return a message if `s` is a module-scope `save` statement/attribute."""
    m = re.match(r'save\b\s*(.?)', s)
    if m and m.group(1) not in ('=', '('):
        return "`save` statement at module scope"
    if re.match(r'(integer|real|logical|character|complex|double\s*precision|'
                r'type\s*\(|class\s*\(|procedure\s*\()', s):
        dc = find_top(s, '::')
        if dc >= 0:
            attrs = [a.strip() for a in split_commas(s[:dc])[1:]]
            if any(re.fullmatch(r'save', a) for a in attrs):
                return "`save` attribute on a module-scope declaration"
    return None


def char_len_text(typespec):
    """The `len` of a `character` type-spec: '*', ':', or a length expression.

    A bare `character`, or one carrying only a `kind=`, has length 1.
    """
    m = re.match(r'character\s*\*\s*(.*)$', typespec)
    if m:
        return strip_parens(m.group(1).strip())
    m = re.match(r'character\s*\((.*)\)\s*$', typespec)
    if not m:
        return '1'                         # bare `character` -> len 1
    inner = m.group(1)
    lm = re.search(r'\blen\s*=\s*([^,]*)', inner)
    if lm:
        return lm.group(1).strip()
    for part in split_commas(inner):       # no `len=` kw: first positional is len
        p = part.strip()
        if '=' in p:
            continue
        return p
    return '1'                             # only `kind=` given -> len 1


def strip_parens(text):
    """`(x)` -> `x`; anything else unchanged."""
    m = re.match(r'\((.*)\)$', text)
    return m.group(1).strip() if m else text


def char_len_is_star(typespec):
    """True if a `character` type-spec has assumed (`*`) or deferred (`:`) len."""
    return char_len_text(typespec) in ('*', ':')


def split_typespec_noco(low):
    """Split a `::`-less character declaration into (typespec, entities)."""
    lstr = low.lstrip()
    rest = lstr[len('character'):]
    j = 0
    while j < len(rest) and rest[j] == ' ':
        j += 1
    if j < len(rest) and rest[j] == '(':
        end = match_paren(rest, j)
        if end < 0:
            return (None, None)
        return ('character' + rest[j:end + 1], rest[end + 1:].strip())
    if j < len(rest) and rest[j] == '*':
        m = re.match(r'\*\s*(\([^)]*\)|\w+)', rest[j:])
        if not m:
            return (None, None)
        return ('character*' + m.group(1), rest[j + m.end():].strip())
    return ('character', rest[j:].strip())


def split_char_decl(low):
    """Split a `character` declaration into (typespec, attrs, entities).

    Returns None if `low` does not declare a `character`.
    """
    if not re.match(r'character\b', low.lstrip()):
        return None
    dc = find_top(low, '::')
    if dc >= 0:
        parts = split_commas(low[:dc])
        return (parts[0].strip(), parts[1:], low[dc + 2:])
    typespec, entities = split_typespec_noco(low)
    if entities is None:
        return None
    return (typespec, [], entities)


def entity_lens(entities, typelen, dummies):
    """Yield (name, len) for each entity of `entities` that is a dummy arg.

    A per-entity length (`x*(*)`, `x*512`) overrides the type-spec length.
    """
    for ent in split_commas(entities):
        e = ent.strip()
        mm = re.match(r'(\w+)', e)
        if not mm or mm.group(1) not in dummies:
            continue
        em = re.match(r'\w+\s*\*\s*(\([^)]*\)|\w+)', e)
        yield (mm.group(1),
               strip_parens(em.group(1).strip()) if em else typelen)


def char_decl_lens(low, dummies):
    """Return [(name, len)] for the dummy args `low` declares as character."""
    parsed = split_char_decl(low)
    if parsed is None:
        return []
    typespec, _attrs, entities = parsed
    return list(entity_lens(entities, char_len_text(typespec), dummies))


def check_char_decl(low, dummies):
    """Return dummy-arg names declared as fixed-length character."""
    parsed = split_char_decl(low)
    if parsed is None:
        return []
    typespec, attrs, entities = parsed
    if any(re.search(r'\b(allocatable|pointer)\b', a) for a in attrs):
        return []
    return [nm for nm, ln in entity_lens(entities, char_len_text(typespec),
                                         dummies)
            if ln not in ('*', ':')]


def check_allocate(s):
    """(has_stat, has_errmsg, statvar) for an `allocate` statement, else None."""
    if not re.match(r'allocate\s*\(', s):
        return None
    i = s.find('(')
    j = match_paren(s, i)
    inner = s[i + 1:(j if j >= 0 else len(s))]
    has_stat = has_errmsg = False
    statvar = None
    for item in split_commas(inner):
        it = item.strip()
        m = re.match(r'stat\s*=\s*(\w+)', it)
        if m:
            has_stat, statvar = True, m.group(1)
        if re.match(r'errmsg\s*=', it):
            has_errmsg = True
    return (has_stat, has_errmsg, statvar)


def add_pure_disqualifiers(frame, s):
    if re.match(r'(write|print|read|open|close|inquire|rewind|flush|backspace|'
                r'endfile|namelist|format)\b', s):
        frame['dis'].add('io')
    if re.match(r'(stop|pause)\b', s) or re.match(r'error\s+stop\b', s):
        frame['dis'].add('stop')
    if re.match(r'call\b', s):
        frame['dis'].add('call')
    if re.match(r'common\b', s):
        frame['dis'].add('common')
    if re.match(r'save\b(?!\s*=)', s):
        frame['dis'].add('save')


def analyze_use_scope(frame, findings, path):
    spec_text = ' '.join(frame['body'])
    procs = frame.get('procs', [])
    for lineno, mod, syms in frame['uses']:
        syms = [x for x in syms if x]
        if not syms:
            continue
        pats = [re.compile(r'\b' + re.escape(x) + r'\b') for x in syms]
        if any(p.search(spec_text) for p in pats):
            continue                        # used in module spec -> keep here
        using = [name for name, txt in procs if any(p.search(txt) for p in pats)]
        if len(using) == 1:
            findings.append((path, lineno, 'use-scope',
                             "`use %s` (only: %s) is used only in `%s`; consider "
                             "moving it into that procedure"
                             % (mod, ', '.join(syms), using[0])))


def finalize_frame(frame, stack, findings, experimental, path, charmap):
    if frame['kind'] in ('subroutine', 'function'):
        if charmap is not None and frame['charlens']:
            charmap[frame['name']] = frame['charlens']
        body = frame['body']
        for idx, lineno, statvar in frame['allocs']:
            pat = re.compile(r'\b' + re.escape(statvar) + r'\b')
            if not any(pat.search(t) for t in body[idx + 1:]):
                findings.append((path, lineno, 'alloc-unchecked',
                                 "`stat=%s` from `allocate` is never checked "
                                 "afterwards" % statvar))
        if (experimental and not frame['is_pure'] and not frame['dis']
                and frame['dummies']):
            findings.append((path, frame['line'], 'pure-candidate',
                             "`%s` has no I/O, call, stop, or save; verify it can "
                             "be declared `pure`" % frame['name']))
        for f in reversed(stack):
            if f['kind'] in ('module', 'submodule'):
                f.setdefault('procs', []).append(
                    (frame['name'], ' '.join(frame['body'])))
                break
    if frame['kind'] in ('module', 'submodule') and experimental:
        analyze_use_scope(frame, findings, path)


def scan_fortran_structure(path, lines, findings, experimental, charmap=None):
    stack = []
    for lineno, _code, nostr in statements(lines):
        low = nostr.lower()
        s = low.lstrip()
        if is_closer(s):
            if stack:
                finalize_frame(stack.pop(), stack, findings, experimental, path,
                               charmap)
            continue
        opener = classify_opener(low)
        if opener:
            kind, name, dummies, is_pure = opener
            stack.append({'kind': kind, 'name': name, 'line': lineno,
                          'dummies': dummies, 'is_pure': is_pure,
                          'body': [], 'allocs': [], 'dis': set(), 'uses': [],
                          'charlens': {}})
            continue
        if not stack:
            continue
        frame = stack[-1]
        if frame['kind'] in ('module', 'submodule') and re.match(r'use\b', s):
            u = parse_use(s, lineno)
            if u:
                frame['uses'].append(u)
            continue
        idx = len(frame['body'])
        frame['body'].append(low)
        if frame['kind'] in ('module', 'submodule'):
            msg = check_module_save(s)
            if msg:
                findings.append((path, lineno, 'module-save', msg))
        if frame['kind'] in ('subroutine', 'function') and frame['dummies']:
            for nm in check_char_decl(low, frame['dummies']):
                findings.append((path, lineno, 'char-len-star',
                                 "character dummy argument `%s` should be `len=*`"
                                 % nm))
            frame['charlens'].update(char_decl_lens(low, frame['dummies']))
        res = check_allocate(s)
        if res is not None:
            has_stat, has_errmsg, statvar = res
            if not has_stat:
                findings.append((path, lineno, 'allocate-stat',
                                 "`allocate` should pass `stat=` and check it"))
            if not has_errmsg:
                findings.append((path, lineno, 'allocate-errmsg',
                                 "`allocate` should pass `errmsg=`"))
            if statvar and frame['kind'] in ('subroutine', 'function'):
                frame['allocs'].append((idx, lineno, statvar))
        if frame['kind'] in ('subroutine', 'function'):
            add_pure_disqualifiers(frame, s)
    while stack:
        finalize_frame(stack.pop(), stack, findings, experimental, path, charmap)


# --------------------------------------------------------------------------
# CCPP metadata pairing rule
# --------------------------------------------------------------------------

META_TABLE_HEADERS = ('ccpp-table-properties', 'ccpp-arg-table')


def meta_path_for(f90path):
    """The `.meta` file paired with a Fortran source, or None if absent."""
    meta = re.sub(r'\.[fF]90$', '.meta', f90path)
    return meta if meta != f90path and os.path.exists(meta) else None


def f90_path_for(metapath):
    """The Fortran source paired with a `.meta` file, or None if absent."""
    for ext in ('.F90', '.f90'):
        cand = metapath[:-len('.meta')] + ext
        if os.path.exists(cand):
            return cand
    return None


def parse_meta_vars(path):
    """Parse a `.meta` file into {arg-table name: {var: {'line', property...}}}.

    Names are lowercased. Only `[ccpp-arg-table]` sections contribute; the
    `[ccpp-table-properties]` preamble is skipped.
    """
    tables = {}
    section, table, var = None, None, None
    for lineno, raw in enumerate(read_text(path).splitlines(), 1):
        line = raw.split('#')[0].strip()
        if not line:
            continue
        m = re.match(r'\[(.*)\]$', line)
        if m:
            name = m.group(1).strip()
            if name.lower() in META_TABLE_HEADERS:
                section, table, var = name.lower(), None, None
            elif section == 'ccpp-arg-table' and table is not None:
                var = name.lower()
                tables[table].setdefault(var, {'line': lineno})
            else:
                var = None
            continue
        key, eq, val = line.partition('=')
        if not eq:
            continue
        key, val = key.strip().lower(), val.strip()
        if var is not None:
            tables[table][var][key] = val
        elif section == 'ccpp-arg-table' and key == 'name':
            table = val.lower()
            tables.setdefault(table, {})
    return tables


def meta_type_kind(var):
    """The (type, kind) a metadata variable block declares.

    `kind` may ride along on the type line (`type = character | kind = len=*`)
    or stand on its own (`kind = len=*`); both forms are legal metadata.
    """
    parts = [p.strip() for p in var['type'].split('|')]
    kind = var.get('kind')
    for p in parts[1:]:
        k, eq, v = p.partition('=')
        if eq and k.strip().lower() == 'kind':
            kind = v.strip()
    return parts[0].strip().lower(), kind


def meta_char_len(kind):
    """The `len` a metadata character `kind = len=N` declares (default 1)."""
    if not kind:
        return '1'
    m = re.match(r'len\s*=\s*(.*)$', kind.strip(), re.IGNORECASE)
    return m.group(1).strip() if m else '1'


def check_meta_pairing(f90path, charmap, findings):
    """Flag character dummy args whose `len` disagrees with the paired `.meta`.

    A metadata `kind = len=512` against a `len=*` dummy still compiles -- the
    cap just passes a longer actual -- so nothing downstream catches the drift.
    """
    metapath = meta_path_for(f90path)
    if metapath is None:
        return
    tables = parse_meta_vars(metapath)
    for proc, args in charmap.items():
        table = tables.get(proc)
        if table is None:
            continue                       # not a CCPP entry point
        for arg, flen in args.items():
            var = table.get(arg)
            if var is None or 'type' not in var:
                continue
            mtype, kind = meta_type_kind(var)
            if mtype != 'character':
                continue
            mlen = meta_char_len(kind)
            if mlen.lower() != flen.lower():
                findings.append((metapath, var['line'], 'meta-char-len',
                                 "`%s` is `len=%s` in the metadata but `len=%s` "
                                 "in %s:%s" % (arg, mlen, flen,
                                               os.path.basename(f90path), proc)))


# --------------------------------------------------------------------------
# Namelist XML rule
# --------------------------------------------------------------------------

def scan_namelist_xml(path, text, findings):
    if 'entry_id_pg' not in text and '<entry' not in text:
        return                             # not a namelist definition file
    first = re.search(r'<entry\b', text)
    head = text[:first.start()] if first else text
    if NAMELIST_MARKER not in head:
        findings.append((path, 1, 'namelist-block',
                         "missing the standard namelist definition comment block "
                         "at the top of the file"))


# --------------------------------------------------------------------------
# Experimental: citation-doi (comment scan)
# --------------------------------------------------------------------------

DOI_RE = re.compile(r'(doi\s*:|doi\.org|10\.\d{4,9}/)', re.IGNORECASE)
CITE_RE = re.compile(r'(et\s+al\.?|\((?:18|19|20)\d\d[a-z]?\))', re.IGNORECASE)


def scan_citations(path, lines, findings):
    for lineno, raw in enumerate(lines, 1):
        _code, comment, _nostr = blank_strings_and_comment(raw)
        if not comment:
            continue
        if CITE_RE.search(comment) and not DOI_RE.search(comment):
            findings.append((path, lineno, 'citation-doi',
                             "comment looks like a citation but has no DOI"))


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def read_text(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def lint_fortran(path, experimental, findings):
    lines = read_text(path).splitlines()
    charmap = {}
    scan_surface(path, lines, findings)
    scan_fortran_structure(path, lines, findings, experimental, charmap)
    check_meta_pairing(path, charmap, findings)
    if experimental:
        scan_citations(path, lines, findings)


def lint_xml(path, findings):
    scan_namelist_xml(path, read_text(path), findings)


def gather_paths(paths):
    fortran, xml = [], []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for fn in files:
                    full = os.path.join(root, fn)
                    if fn.endswith(('.F90', '.f90')):
                        fortran.append(full)
                    elif fn.endswith('.xml') and 'namelist' in fn:
                        xml.append(full)
        elif p.endswith(('.F90', '.f90')):
            fortran.append(p)
        elif p.endswith('.meta'):
            partner = f90_path_for(p)      # meta rules are driven from the F90
            if partner:
                fortran.append(partner)
        elif p.endswith('.xml'):
            xml.append(p)
        else:
            sys.stderr.write("skipping (unrecognized type): %s\n" % p)
    return sorted(set(fortran)), sorted(set(xml))


# --------------------------------------------------------------------------
# Git diff selection (--diff)
# --------------------------------------------------------------------------

# Rules reported at a fixed line (not tied to a specific edited line); these
# still run for any changed file under --diff, bypassing the changed-line filter.
FILE_LEVEL_RULES = {'namelist-block', 'meta-char-len'}


def _git(loc, gitargs):
    """Run `git -C loc GITARGS`; return stdout lines, or None on failure."""
    try:
        r = subprocess.run(['git', '-C', loc] + gitargs,
                           capture_output=True, text=True)
    except OSError as e:
        sys.stderr.write("error: cannot run git: %s\n" % e)
        return None
    if r.returncode != 0:
        sys.stderr.write("error: git %s failed: %s\n"
                         % (' '.join(gitargs), r.stderr.strip()))
        return None
    return r.stdout.splitlines()


def diff_spec(rev):
    """Diff spec for base revision REV: merge-base (PR) semantics, unless the
    caller already passed an explicit `..`/`...` range."""
    return rev if '..' in rev else '%s...HEAD' % rev


def diff_changed_files(root, spec):
    """Repo-relative *.F90/*namelist*.xml paths added/modified in `spec`."""
    out = _git(root, ['diff', '--name-only', '--diff-filter=ACMR', spec,
                      '--', '*.F90', '*.f90', '*.meta', '*namelist*.xml'])
    return out or []


def diff_changed_lines(root, spec, relpath):
    """New-side line numbers added/changed for `relpath` in `spec`."""
    out = _git(root, ['diff', '--unified=0', spec, '--', relpath])
    lines = set()
    for line in (out or []):
        if line.startswith('@@'):
            m = re.search(r'\+(\d+)(?:,(\d+))?', line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2)) if m.group(2) is not None else 1
                lines.update(range(start, start + count))
    return lines


def select_diff(paths, rev, whole_file):
    """Return (fortran, xml, changed_lines) for the files changed vs `rev`.

    `changed_lines` maps abspath -> set of changed line numbers (empty when
    --whole-file, in which case no line filtering is applied).
    """
    loc = paths[0] if paths else '.'
    if os.path.isfile(loc):
        loc = os.path.dirname(loc) or '.'
    top = _git(loc, ['rev-parse', '--show-toplevel'])
    if not top:
        return None
    root = top[0]
    spec = diff_spec(rev)
    rels = diff_changed_files(root, spec)
    selected = [(rel, os.path.join(root, rel)) for rel in rels]
    if paths:
        roots = [os.path.abspath(p) for p in paths]
        selected = [(rel, ap) for rel, ap in selected
                    if any(os.path.abspath(ap) == r
                           or os.path.abspath(ap).startswith(r + os.sep)
                           for r in roots)]
    f90s = set(ap for _rel, ap in selected if ap.endswith(('.F90', '.f90')))
    # A .meta-only edit still needs its partner .F90 linted, since meta-char-len
    # is driven from the Fortran declarations.
    for _rel, ap in selected:
        if ap.endswith('.meta'):
            partner = f90_path_for(ap)
            if partner:
                f90s.add(partner)
    fortran = sorted(f90s)
    xml = sorted(ap for _rel, ap in selected
                 if ap.endswith('.xml') and 'namelist' in os.path.basename(ap))
    keep = set(fortran) | set(xml)
    changed_lines = {}
    if not whole_file:
        for rel, ap in selected:
            if ap in keep:
                changed_lines[ap] = diff_changed_lines(root, spec, rel)
    return fortran, xml, changed_lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='*', metavar='PATH')
    ap.add_argument('--experimental', action='store_true',
                    help='enable noisy heuristics: use-scope, pure-candidate, '
                         'citation-doi')
    ap.add_argument('--diff', nargs='?', const='main', default=None, metavar='REV',
                    help='only lint files changed vs REV (default: main), using '
                         'PR/merge-base semantics (REV...HEAD); reports only '
                         'findings on changed lines unless --whole-file')
    ap.add_argument('--whole-file', action='store_true',
                    help='with --diff, report all findings in changed files, not '
                         'just findings on changed lines')
    ap.add_argument('--fix', action='store_true',
                    help='rewrite files in place for the mechanical rules (%s); '
                         'under --diff only the changed lines are touched'
                         % ', '.join(FIXABLE_RULES))
    ap.add_argument('--list-rules', action='store_true',
                    help='print the rule ids and exit')
    args = ap.parse_args()

    if args.list_rules:
        for rid, desc in RULES.items():
            print("%-16s %s" % (rid, desc))
        return 0

    changed_lines = {}
    if args.diff is not None:
        sel = select_diff(args.paths, args.diff, args.whole_file)
        if sel is None:
            return 2
        fortran, xml, changed_lines = sel
    else:
        if not args.paths:
            ap.error('no paths given (or use --diff)')
        fortran, xml = gather_paths(args.paths)

    if args.fix:
        nfixed = 0
        for path in fortran:
            nfixed += fix_file(path, changed_lines.get(path) if args.diff
                               is not None and not args.whole_file else None)
        sys.stderr.write("fixed %d occurrence(s) of: %s\n"
                         % (nfixed, ', '.join(FIXABLE_RULES)))

    findings = []
    for path in fortran:
        lint_fortran(path, args.experimental, findings)
    for path in xml:
        lint_xml(path, findings)

    if args.diff is not None and not args.whole_file:
        findings = [f for f in findings
                    if f[2] in FILE_LEVEL_RULES
                    or f[1] in changed_lines.get(f[0], ())]

    findings.sort(key=lambda f: (f[0], f[1], f[2]))
    for path, lineno, rule, msg in findings:
        print("%s:%d: [%s] %s" % (path, lineno, rule, msg))

    counts = {}
    for _p, _l, rule, _m in findings:
        counts[rule] = counts.get(rule, 0) + 1
    if findings:
        sys.stderr.write("\n%d finding(s): %s\n" % (
            len(findings),
            ', '.join("%s=%d" % (r, counts[r]) for r in sorted(counts))))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
