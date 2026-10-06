# 20. Phase 2: snapshots

A CAM snapshot run writes two instantaneous history tapes, one frame per timestep: a
"before" tape captured on entry to the scheme and an "after" tape captured after
`physics_update`. CAM-SIMA's FPHYStest compset (null dycore) then re-runs only your suite
from the "before" frames and compares its results with the "after" frames every step.

What a tape holds, automatically: every `state` field (`state_*`), every constituent
(`cnst_<name>`), `tend`, every pbuf field (`pbuf_<name>`; a units table in
`cam_snapshot_common.F90` only supplies units, unknown names just warn), `cam_in`/`cam_out`,
a few routine locals (`tphysac_fh2o`, `tphysac_surfric`, `tphysac_obklen`,
`tphysac_flx_heat`, or the tphysbc equivalents), the physics grid coordinates in radians
(`lat_rad`, `lon_rad`, since October 2026; the null dycore prefers them over the degrees
coordinates so latitude-dependent schemes see CAM's values bitwise), and, when before and
after name the same scheme, the scheme's `ptend` fields. Step 0 is skipped by design, so `STOP_N=N` gives N frames
(nstep 1 to N; verified with N=6); use 6, which is also the coupling minimum dropsonde needs.

## Choose the method

```
Does bld/namelist_files/namelist_definition.xml list your scheme in the
valid_values of cam_take_snapshot_before?
  yes -> A. use the named point
  no  -> is the scheme called directly from physpkg (tphysbc/tphysac)?
           yes, and the bracket is worth keeping for others -> B. add a named point
           yes, one-off -> C. user_set bracket
           no (called inside chemistry, radiation, or another scheme) -> D. interior capture
```

### A. Named point exists

Set `cam_take_snapshot_before` and `_after` to that name. Read the bracket in `physpkg.F90`
to see exactly what sits between the two captures; some sections contain more than one call
(the `iondrag_calc_section` bracket also covers the WACCM-X electron temperature call and the
`UTEND_IONDRG` diagnostics, for instance). Your suite must reproduce everything in the bracket.

### B. Add a named point

The canonical change touches five files (CAM commit f29793eea, which separated the Beljaars
and TMS form-drag section from vertical diffusion, is the model):

1. `src/physics/cam/physpkg.F90` and 2. `src/physics/cam7/physpkg.F90`: three blocks copied
   verbatim from a neighbouring bracket in the same routine (before capture; `ptend` capture
   guarded by before == after; after capture following `physics_update`).
3. `bld/namelist_files/namelist_definition.xml`: add the name to `valid_values` of both
   `cam_take_snapshot_before` and `cam_take_snapshot_after`.
4. `bld/build-namelist`: the same list appears there too (search for `qbo_relax`).
5. The CAM PR notes the new snapshot name.

### C. user_set bracket

Insert the same three blocks around your call with the name `"user_set"`. Copy the capture
call signature from the nearest existing bracket in the same routine; it differs between
`tphysbc` and `tphysac` and between the cam and cam7 physpkg files. Set both namelist
variables to `'user_set'`. Remove the blocks before the PR, or convert them to method B.

### D. Interior capture

For code that runs between two points inside one physics scheme (chemistry working arrays,
heating rates computed inside radiation), the physpkg brackets capture the wrong boundary.
The established pattern, from the MAM port:

- Register capture fields on both tapes at init with `snapshot_addfld` (per-species fields
  are one file variable per species, `<base>_<species>`), then `outfld` each field on one
  tape at its capture point. A dedicated dev switch, hardcoded, never a namelist option.
- One capture run feeds every suite: standalone suites mount the tape that holds their entry
  boundary; the assembled suite mounts before and after.
- The zero-bracket trap: a field registered on both tapes but written on one reads silent
  zeros from the other. "One input is inexplicably zero while met fields are fine" means the
  field is not on the tape you mounted.
- Constituent-dimensioned reads in CAM-SIMA resolve one base name for all constituents; a
  species captured under a different base is silently missed.

Design this with the user before writing code; it is a scoping task in its own right.

## Generate

1. Compset and grid: the lowest-resolution configuration that activates the scheme.
   `ne3pg3_ne3pg3_mg37` keeps files small and matches every existing CAM-SIMA test. Confirm
   activation in the init log of the baseline run from phase 1. For WACCM schemes see
   `references/waccm-triage.md`: the mid-top TS1 compsets activate radheat but not iondrag,
   SC-WACCM activates the ghg ion-drag path, MA chemistry is needed for anything with ions.
2. Case: `DEBUG=TRUE`, GNU, `STOP_OPTION=nsteps`, `STOP_N=6`, `ROF_NCPL` and `GLC_NCPL` equal
   to `ATM_NCPL`, `DOUT_S=FALSE`. If the same case will later feed dropsonde, also `NTASKS=1`
   and dechunk with `-pcols <total columns>` in `CAM_CONFIG_OPTS` (486 at ne3pg3).
3. `user_nl_cam` from `templates/user_nl_cam.snapshot`: tapes 6 and 7, `nhtfrq` 1 on both,
   `ndens` 1 (double precision) on both, the two snapshot names, plus whatever switch turns
   the scheme on. Avoid tape 1. After `./case.setup` and `./preview_namelists`, check
   `atm_in` for `fincl6` or `fincl7` from a use case; if present pick other tape numbers.
4. Build and run. Output: `<case>.cam.h5i.*.nc` (before) and `<case>.cam.h6i.*.nc` (after).

## Verify the files before leaving this phase

- `ncdump -h` each file: the time dimension has `STOP_N` frames; the fields your
  inventory table listed as inputs are present under their snapshot names (`pbuf_<NAME>`,
  `state_<name>`, `cnst_<NAME>`, `cam_in_<name>`). Write the mapping into the inventory.
- The after tape contains the `ptend` fields when before and after share a name. Grep for
  them by name (`grep -E 'double (ptend_[usv]\(|state_[uv]\()'`); the hundreds of `pbuf_*`
  and `ptend_cflx_*` lines come first alphabetically and hide them behind a `head`.
- The init log shows the scheme active (its own print or the absence of a "does not apply"
  message).
- Leave the files in the run directory. CAM-SIMA's `ncdata` and `ncdata_check` point there
  until phase 6. Nothing shared is written.

Snapshot files at ne3pg3 are tens of megabytes; mid-top or WACCM vertical grids and FV grids
grow fast. Keep `STOP_N` small.

## Exit check

Both tapes exist, cover at least 2 frames, carry every input and output of the scheme, and the
inventory table now names each one's snapshot field. If the bracket contains calls other than
your scheme, the list of what your suite must reproduce is written down.
