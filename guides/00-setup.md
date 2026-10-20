# 00. Setup: sandbox, interview, autonomy, tools

## Sandbox layout

One directory per conversion workspace, on the machine where you build (Derecho or Izumi).
Short-lived work goes under scratch, long-lived under home or work.

```
<sandbox>/
  kit.local.md          answers from the setup interview (see below)
  CAM/                  full clone, submodules checked out (bin/git-fleximod update)
  CAM-SIMA/             full clone, submodules checked out (bin/git-fleximod update; 15 min or
                        more on GLADE because of CTSM, run it in the background with nohup)
  <case dirs>           CIME case directories as siblings; bld/ and run/ land in $SCRATCH/<case>/
  notes/                scratch notes, dropsonde output, ncdump listings
```

Base branches: CAM uses `cam_development`, CAM-SIMA uses `development`, atmospheric_physics
uses `main`. The `main` branch of CAM and CAM-SIMA is empty on purpose.

### The two copies of atmospheric_physics

CAM carries atmospheric_physics at `CAM/src/atmos_phys`; CAM-SIMA carries it at
`CAM-SIMA/src/physics/ncar_ccpp`. Both are git submodules pinned to tags, and the two
models usually pin different tags. During a conversion both copies must hold the same code,
because dropsonde compares the two models running the same scheme source.

Default, git-honest flow. It stays on the local filesystem: the CAM-SIMA copy fetches from
the CAM copy's directory, and GitHub is not involved until the user decides to push.

1. In `CAM/src/atmos_phys`, create a branch from the pinned tag and commit the portable
   scheme there (phase 1 writes it directly under `schemes/<scheme>/`).
2. In `CAM-SIMA/src/physics/ncar_ccpp`, add the CAM copy as a remote and check out the same
   branch from it:

   ```
   git -C <sandbox>/CAM-SIMA/src/physics/ncar_ccpp remote add cam_copy <sandbox>/CAM/src/atmos_phys
   git -C <sandbox>/CAM-SIMA/src/physics/ncar_ccpp fetch cam_copy
   git -C <sandbox>/CAM-SIMA/src/physics/ncar_ccpp checkout -b <branch> cam_copy/<branch>
   ```

3. Every later change: commit in the CAM copy, then `git pull cam_copy <branch>` in the
   CAM-SIMA copy; it is a fast-forward because only one copy is edited. If a phase 3 edit is
   more natural in the CAM-SIMA copy, add the reverse remote the same way and pull in the CAM
   copy. Before any dropsonde run, confirm `git -C CAM/src/atmos_phys rev-parse HEAD` equals
   the same in CAM-SIMA.
4. The branch reaches the user's fork only when the user pushes it, or when `kit.local.md`
   says `github_write: yes`; usually at phase 6.

The superprojects will report the submodule as modified; that is expected until the PRs bump
the pins. Do not run `git-fleximod update` again in a sandbox with a checked-out branch; it
moves the submodule back to the pinned tag.

Opt-in shortcut for experienced users: replace one submodule directory with a symlink to the
other. One working tree, no pull between copies, but `git status` and fleximod get confused
and a `git-fleximod update` will destroy the link. Not for a first conversion.

## Setup interview

If `<sandbox>/kit.local.md` does not exist, ask these questions in one message and write the
file from `templates/kit.local.example.md`. Do not guess any of them.

1. Machine (Derecho or Izumi) and the project code to charge (`./xmlquery PROJECT` in any
   existing case shows one).
2. Absolute paths of the CAM and CAM-SIMA checkouts, and the scratch root where CIME puts
   `bld/` and `run/` (Derecho: `/glade/derecho/scratch/$USER`, not the stale `$SCRATCH`
   some login shells export).
3. Compiler for snapshot and test runs. GNU is required for the archived snapshot set.
4. Autonomy level (below).
5. Which parameterization, and the compset and grid that exercise it. If unknown, phase 1
   starts by finding out; `references/waccm-triage.md` has the answer for the WACCM sheet.
6. Whether you may write to GitHub: `git push` to the user's fork and opening pull requests.
   Default no. Tell the user plainly what no means: every commit stays on a branch in the
   local clones, the two atmospheric_physics copies sync through a local remote, and the
   user pushes and opens the PRs when ready. This is independent of the autonomy level and
   never extends to the ESCOMP remotes.

## Autonomy levels

| Level | Cluster commands that change state (create case, build, submit, dropsonde, tests) | Reading files, logs, ncdump, git | GitHub: push, pull request, any write to a fork |
|---|---|---|---|
| 0 | You write the exact command; the user runs it and pastes the output back | always allowed | never |
| 1 | You state the command and its purpose, wait for a yes, then run it | always allowed | never |
| 2 | You run it and report what happened, including failures verbatim | always allowed | never |

The autonomy level is about the cluster, not GitHub. Whatever the level, every commit lives
on a branch in the local clones and nothing is pushed anywhere, not even to the user's own
fork, unless `kit.local.md` says `github_write: yes`. The ESCOMP remotes are never a push
target, and pull requests are opened by the user. Local git is part of the work at every
level: feature branches, commits on them, and the fetch and pull between the two
atmospheric_physics copies. Never commit on a base branch, never rewrite history, and report
every commit.

At every level: never write outside the user's own home, scratch, or work directories; never
touch the shared snapshot baseline before phase 6; never `rm -rf` a case directory without
asking. State what you ran and what it produced, even at level 2.

## Machine notes

Derecho:

- Build on a compute node: `qcmd -A <project> -- ./case.build`. Non-interactive shells need
  `export PBS_ACCOUNT=<project>` for `qcmd`.
- Login shells differ (zsh, bash, tcsh). For a modern Python use `bash -lc '...'`.
- GLADE metadata is slow: never `find` across a model tree; `git status --ignore-submodules`.
- After a failed `case.build`, a second build can abort with "env_build HAS CHANGED". If only
  source changed, `./xmlchange BUILD_STATUS=0` and build again instead of `--clean-all`.
- Input data root: `/glade/campaign/cesm/cesmdata/inputdata`.

Izumi: tcsh login shell, old Python, use `qsub` with an explicit queue; gdb needs
`-gdwarf-4` with recent gcc. See the dropsonde README for the Intel specifics.

## Tools

Shared tools on Derecho: `/glade/campaign/cesm/community/amwg/sima_tools` (read its
`README.md` first). Each tool has a one-screen README; call it by full path, since a fresh
shell does not keep `PATH`:

- `suite-trace/bin/suite-trace --cam-sima <dir> --atmospheric-physics <dir> --suite <stem>`
  followed by `status | who <name> | trace <name> | consumers <name> | scheme <name> |
  schemes | search <regex> | read-before-write | audit`: does a suite resolve, who provides a
  standard name, who consumes it, dead inputs. A few seconds, no build. Under zsh, export
  `SUITE_TRACE_CAM_SIMA`, `SUITE_TRACE_ATMOSPHERIC_PHYSICS` and `SUITE_TRACE_SUITE` once
  instead of holding the whole command in a `$ST` variable (zsh does not word-split it).
  The pumas submodule must be populated for every suite, because the CAM-SIMA registry reads
  `micro_pumas_diags.meta`; in a bare atmospheric_physics worktree:
  `git -C <worktree> submodule update --init schemes/pumas/pumas` (about a second).
- `fortran-verify/bin/fbody`: proves a subroutine body survived a move or split (one
  IDENTICAL / DIFF n / NOT FOUND line per unit).
- `fortran-verify/bin/fsig`: interface drift between two revisions; positional call check.

Compile check without a model build (syntax and interfaces only): from a case that has
built once with the same compiler, source the case environment first, otherwise the login
shell's `gfortran` (12.x) is used instead of the case's (14.x):

```
cd <case> && source .env_mach_specific.sh
gfortran -fsyntax-only -ffree-line-length-none \
    -I$(./xmlquery --value EXEROOT)/atm/obj -J$TMPDIR <files>
```

`-J$TMPDIR` keeps the `.mod` output out of the case. An undeclared symbol or a changed
interface fails here in seconds. Host code that uses the shared libraries (PIO, csm_share)
usually also needs `-I$(./xmlquery --value EXEROOT)/lib/include`; when a module is still not
found, the case build is the check.

Everywhere: `cprnc` (`/glade/campaign/cesm/cesmdata/cprnc/cprnc` on Derecho; it is not a
case variable on current CIME), `ncdump`, `ncks`.
dropsonde is a separate repository: `git clone https://github.com/hplin-ucar/dropsonde`
in the sandbox or ask the author if it is already installed somewhere.

## Exit check

`kit.local.md` exists and is complete, `github_write` included; both model clones have
submodules populated; the atmospheric_physics branch is checked out in both copies at the
same commit, the CAM-SIMA copy tracking the CAM copy through the `cam_copy` remote.
