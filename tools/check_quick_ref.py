#!/usr/bin/env python3
"""Check references/standard_names_quick_ref.md against the code.

Every `- `cam` -> `standard_name` [units]` entry must name a standard name that
exists in the CAM-SIMA registry or in a .meta file of CAM-SIMA or
atmospheric_physics, with the units the code declares. Exit 1 on any mismatch.

  python3 -I tools/check_quick_ref.py references/standard_names_quick_ref.md \
      /path/to/CAM-SIMA /path/to/atmospheric_physics
"""
import glob
import os
import re
import sys


def collect(cam_sima, atmos_phys):
    """standard name -> {units: {source file, ...}} from registry.xml and .meta files."""
    names = {}

    def add(name, units, src):
        names.setdefault(name, {}).setdefault(units.strip(), set()).add(src)

    reg = open(os.path.join(cam_sima, 'src', 'data', 'registry.xml')).read()
    for tag in re.finditer(r'<variable\b[^>]*>', reg, re.S):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag.group(0)))
        if 'standard_name' in attrs and 'units' in attrs:
            add(attrs['standard_name'], attrs['units'], 'registry.xml')
    metas = glob.glob(os.path.join(cam_sima, 'src', '**', '*.meta'), recursive=True)
    metas += glob.glob(os.path.join(atmos_phys, '**', '*.meta'), recursive=True)
    for path in metas:
        if os.sep + 'ncar_ccpp' + os.sep in path:
            continue  # the CAM-SIMA submodule copy; atmos_phys is read directly
        current = None
        for line in open(path, errors='replace'):
            m = re.match(r'\s*standard_name\s*=\s*(\S+)', line)
            if m:
                current = m.group(1)
                continue
            m = re.match(r'\s*units\s*=\s*(.*)$', line)
            if m and current:
                add(current, m.group(1), os.path.relpath(path, os.path.dirname(cam_sima)))
                current = None
    return names


def main(argv):
    if len(argv) != 4:
        sys.exit(__doc__)
    quick, cam_sima, atmos_phys = argv[1:]
    names = collect(cam_sima, atmos_phys)
    ok = bad = 0
    for lineno, line in enumerate(open(quick), 1):
        m = re.match(r'- `([^`]*)` -> `([^`]*)` \[([^\]]*)\]', line)
        if not m:
            continue
        cam, name, units = m.groups()
        if name not in names:
            bad += 1
            print(f'{quick}:{lineno}: MISSING  {cam} -> {name}')
        elif units not in names[name]:
            bad += 1
            print(f'{quick}:{lineno}: UNITS    {name}: quick ref [{units}], code {sorted(names[name])}')
        else:
            ok += 1
    print(f'{ok} entries match the code, {bad} do not')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
