# 10. Phase 1: work inside CAM and prove bit-for-bit

The scheme becomes CCPP-shaped while it still runs inside CAM, under CAM's own tests. Nothing
moves to CAM-SIMA until this phase's exit check passes.

## 1.1 Inventory the entry point

Find the driver subroutine and record, as a table, everything it touches:

- Call site: `src/physics/cam/physpkg.F90` and `src/physics/cam7/physpkg.F90` are separate
  files; most schemes are called from both. Note `tphysbc` (before the coupler) or `tphysac`
  (after). Note whether an existing snapshot bracket surrounds the call (phase 2 uses this).
- Regime: a physpkg scheme takes `state`, `ptend`, `pbuf`. A chemistry-embedded scheme is
  called from `gas_phase_chemdr`, `aero_model`, `mo_setext`, or `mo_waccm_hrates` and works on
  chemistry-local arrays. The regime decides the snapshot method and the working-array design.
- Inputs: every `state%X`, `pbuf_get_field`, `cam_in%X`, module `use` (physconst, ppgrid,
  time_manager, phys_grid, ref_pres, cam_history, constituents), namelist variable, and
  module-level saved state set at init or timestep_init.
- Outputs: `ptend%X` fields and their flags (`lu`, `lv`, `ls`, `lq(:)`), pbuf writes,
  `outfld` calls (field name, dimensions, units).
- Activation gates: flags computed at init from reference pressures, chemistry species
  present, namelist switches. Confirm the chosen compset actually activates the scheme by
  reading the init log of a baseline run, not by assumption.
- Phases the CCPP version will need: `_init` (tables, indices, weights), `_timestep_init`
  (time interpolation, per-step parameters), `_run`, `_final`. CAM-SIMA supports all four.

## 1.2 Splice: portable module plus CAM interface

Create two files from the original module. Every original line goes to exactly one of them.

- `CAM/src/atmos_phys/schemes/<scheme>/<scheme>.F90`: the portable science, on the
  atmospheric_physics branch. Written here so the later "move" is nothing but metadata.
  Rules: `use ccpp_kinds, only: kind_phys`; explicit arguments for everything that was
  `state%`, `ptend%`, `pbuf`, or a host module; assumed-shape `(:,:)` dummies; `errmsg,
  errflg` last; `_init`/`_run`/`_timestep_init` names; no `addfld`/`outfld` (intermediates
  that fed `outfld` become `intent(out)` arguments now, so the interface never churns later).
- `CAM/src/physics/<cam|waccm|...>/<scheme>_cam.F90`: the CAM interface. Keeps `readnl`,
  resolves pbuf and constituent indices, subsets `pcols` arrays to `1:ncol` at the call,
  zero-fills any `intent(out)` array that is sized `pcols` (mark with `!REMOVECAM` comments),
  initializes `ptend`, calls `outfld`, passes constants from `physconst`.
- Add the new scheme directory to the Filepath list in `CAM/bld/configure` (directories are not
  discovered automatically). `physpkg.F90` calls the `_cam` interface.

Partial split. When only one path of a dispatcher module moves (iondrag's ghg path moved,
its ions path stayed), there is no `<scheme>_cam.F90`: the CAM module is edited in place, its
entry routine for that path becomes the interface described above, and the other paths are
untouched. `fbody --walk` then lists the untouched routines as IDENTICAL, which is the proof
that nothing else moved.

Copy from `git show <base>:<path>`, never retype. Constants come in as arguments
(`gravit`, `pi`, `rearth`); derived constants are computed from the host value with the same
operation CAM used, not replaced by a literal. Real exponents stay real (`x**2._kind_phys`).

Dependency triage for every remaining `use`, in this order: look for a precedent first
(`grep -rn 'use <module>' atmospheric_physics/schemes`; `interpolate_data` for `lininterp` is
already used by `gw_common.F90` and `radiation_utils.F90` as a host-provided module that both
CAM and CAM-SIMA ship under `src/utils`), then absorb into the scheme (small, pure helpers),
pass as an argument (anything the host knows), or vendor a copy under the scheme directory
(a few dozen lines, no CAM types). Only genuinely shared host-flavoured code goes to
`to_be_ccppized`, and that is a decision for the user. A host-provided precedent still sits
outside the `AGENTS.md` portability list: verify the two host copies agree
(`fbody --walk <CAM>:HEAD:src/utils/<x>.F90 <CAM-SIMA>:HEAD:src/utils/<x>.F90`), record the
choice in the inventory, and flag it in the PR.

## 1.3 Rung 0: prove the splice before building

- `fbody --walk <base>:<orig>.F90 <scheme>.F90 <scheme>_cam.F90 --map r8=kind_phys
  --rename <old>_init=<scheme>_init --show` lists one IDENTICAL / DIFF n / NOT FOUND line per
  subroutine and prints the diff under each non-identical one. The target for a clean splice
  is a handful of normalized diff lines, each one explainable (a removed `use physconst`, an
  argument replacing a `pbuf_get_field`, `state%u` becoming `u`). Register every intentional
  diff in your notes. When the run body moved into a routine with a different name, a second
  call isolates the physics lines: `fbody --diff <base>:<orig>.F90 <old_run> <scheme>.F90
  <scheme>_run --map r8=kind_phys --map <old_local>=<new_arg>`.
- Syntax-only compile of the touched files against a built case's module directory (the
  `gfortran -fsyntax-only` recipe under Tools in `guides/00-setup.md`); seconds, no build.
- A review pass before the first build (the `cam-sima-reviewer` agent, or a colleague):
  b4b risks, metadata against the Fortran, suite order. Apply non-numeric fixes as follow-up
  commits; atmospheric_physics and CAM-SIMA squash-merge, so never amend and force-push a
  branch that is already on the fork or checked out on the cluster.
- Mechanical style rules: the repo linter configured in atmospheric_physics CI; read
  `AGENTS.md` and `doc/Code-style.md` there.

## 1.4 Rung 1 to 3: the bit-for-bit ladder

Build two CAM cases with identical configuration (compset, grid, `DEBUG=TRUE`, same
compiler, same `user_nl_cam`, at least 6 steps): one from the unsplit base, one from the
split branch. The base is the snapshot case of `guides/20-snapshots.md`, created with the
unsplit code at the start of this phase (its run is both the b4b reference and the snapshot
source); clone it rather than recreating it:

```
cd <sandbox>/CAM/cime/scripts
./create_clone --case <sandbox>/<case>_split --clone <sandbox>/<case>
cd <sandbox>/<case>_split && ./case.setup
# switch <sandbox>/CAM (and CAM/src/atmos_phys) to the split branch, then
qcmd -A <project> -- ./case.build && ./case.submit
```

`create_clone` copies the XML settings and `user_nl_cam` (snapshot settings included), so
the split run writes its own before and after tapes. Those tapes are the rung 2 comparison:
instantaneous, double precision, every state and pbuf field, written every step. Then climb
only as high as the moment requires:

| Rung | Check | Cost | Guarantee |
|---|---|---|---|
| 1 | `grep -h 'nstep, te' atm.log.*` from both runs, compare line by line | seconds | total energy identical to all printed digits every step: very likely b4b |
| 2 | `cprnc -m <after tape of A> <after tape of B>` (and the before tapes) reports the files IDENTICAL; with a monthly h0 nothing else is written in six steps | a minute | the two runs are b4b in everything written |
| 3 | `aux_cam` regression suite via `test/system/test_driver.sh` against the current baseline | hours, Izumi or Derecho, coordinated with the CAM gatekeepers | the whole CAM configuration space is b4b |

Iterate with rungs 0 and 1. Do rung 2 before declaring the phase done. Rung 3 is for the PR.

## Exit check

Rung 2 passes for the split branch. The inventory table is complete, every dependency has a
resolution, and the list of proposed standard names has been started. Both copies of
atmospheric_physics hold the same commit.
