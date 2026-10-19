# 30. Phase 3: metadata, namelist, host variables, suite, case

The portable module already sits in `atmospheric_physics/schemes/<scheme>/` (phase 1). This
phase adds everything the framework needs to call it and builds the CAM-SIMA test case.
Conventions and templates are in `references/conventions.md`; the framework's timing rules in
`references/framework_gotchas.md`. Read both before writing a line.

## 3.1 Metadata

- Generate the skeleton: `CAM-SIMA/ccpp_framework/scripts/ccpp_fortran_to_metadata.py
  <scheme>.F90`, then fill in standard names, units, dimensions, and intents.
- Dimensions are standard names: `horizontal_loop_extent` in `_run`, `horizontal_dimension`
  in `_init`, `vertical_layer_dimension` / `vertical_interface_dimension`.
- Standard names: registry first (`CAM-SIMA/src/data/registry.xml`), then the host constant
  and composition `.meta` files beside it, then recently converted schemes. Construct missing
  ones by the rules and tag `_TBD`; keep the running list for the user's review.
- Constituents: `advected = true` on the argument when the scheme needs a tracer; look up
  indices at `_init` by standard name with `ccpp_constituent_index(standard_name, index,
  errcode, errmsg)` from the framework's `ccpp_scheme_utils` (host-provided, not a
  `dependencies` entry), never by position.
- `dependencies =` lists helper modules relative to the scheme directory. Host-provided
  modules (the IO reader, kinds) are not listed.
- Diagnostics are a separate `<scheme>_diagnostics` scheme under `sima_diagnostics/`
  (template in conventions.md); it comes in phase 6, but reserve the intermediate outputs now.

## 3.2 Namelist XML

- `<scheme>_namelist.xml` in the scheme directory, translated from CAM's
  `namelist_definition.xml` entries and defaults. Delete `readnl` from the Fortran; the
  framework generates the reader and resolves defaults at case setup.
- An entry with a `standard_name` becomes an `_init` argument. File paths are plain
  `char*256` entries with a `${DIN_LOC_ROOT}/...` default (`solar_irradiance_data`,
  `prescribed_ozone`); no `input_pathname` element, which no scheme namelist uses.
- No `--` inside XML comments; the parser rejects it.
- Verify effective values in the generated `atm_in` after `./preview_namelists`, never from
  the XML alone. CAM's `build-namelist` may have set the same variable differently; compare
  the CAM snapshot case's `atm_in` with the CAM-SIMA one for every variable the scheme reads.

## 3.3 Host variables

Anything the scheme needs that no scheme provides must come from the host:

- A field that exists in the snapshot (for example `pbuf_UZM`) becomes a registry variable
  whose `ic_file_input_names` matches the snapshot field name. The reader fills it from
  `ncdata` every step in FPHYStest.
- A quantity the host computes (time, grid geometry, reference pressures) is exposed through
  host-side metadata: a registry variable set in `cam_comp.F90` each step (as `calday` is), or
  a host module `.meta`. Calendar day exists; year, month, day, seconds of day, and Julian day
  do not yet. Propose the standard names, then ask the user which mechanism they want.
- `latitude` and `longitude` in radians come from the null dycore, which converts the
  snapshot's degrees coordinates; `deg = rad*180/pi` followed by `deg*pi/180` is not the
  identity, so a 1-ulp seed appears at a few dozen columns in any scheme that uses them
  (phase 5 pathology catalogue). The host fix (CAM writes `lat_rad`/`lon_rad` on the tapes and
  the null dycore prefers them) is pending on the `hplin/iondrag_demo` branches, CAM
  6fc7772fa and CAM-SIMA 89beb07f; until it reaches the base branches, exclude the affected
  `_due_to_model_physics` accumulator with a comment. Reference pressures (`ref_pres`) are
  computed from the snapshot's hybrid coefficients and matched CAM bitwise in the iondrag
  dry run.
- Registry constituent entries only declare the IC mapping; a scheme must register the
  constituent (metadata `advected = true`, or a register-phase scheme) or capgen silently
  creates an empty one keyed to the local name (log: `X not found, also looked for: [...]`).

## 3.4 Suite

- `atmospheric_physics/test/test_suites/suite_<scheme>.xml`, group `physics_before_coupler`
  or `physics_after_coupler` to match `tphysbc` or `tphysac`.
- Order: anything the bracket ran before the scheme, the scheme, its `_diagnostics` scheme,
  its tendency updaters (`physics_tendency_updaters`), anything else the bracket contained.
  Diagnostics sit right after the scheme that computes the quantities and before the
  appliers, as `suite_cam7.xml` does (`zm_convr`, `zm_convr_tendency_diagnostics`,
  `apply_heating_rate`). The suite must reproduce the whole snapshot bracket, not just the
  scheme.
- Check offline before any build: `suite-trace ... status` (does it resolve), `who <name>`
  (which host or scheme provides each input), `audit` (inputs nothing produces at run time).
  Syntax-only compile of the touched Fortran (Tools in `guides/00-setup.md`).

## 3.5 The CAM-SIMA case

```
cd CAM-SIMA/cime/scripts
./create_newcase --case <sandbox>/<name> --compset FPHYStest --res ne3pg3_ne3pg3_mg37 \
    --compiler gnu --project <project> --run-unsupported \
    --output-root /glade/derecho/scratch/$USER   # not the stale $SCRATCH a login shell may export
cd <sandbox>/<name>
./xmlchange CAM_CONFIG_OPTS="--dyn none --physics-suites <scheme>"
./xmlchange DEBUG=TRUE,STOP_OPTION=nsteps,STOP_N=<frames>,DOUT_S=FALSE
./xmlchange NTASKS=1          # required later for dropsonde; cheap at ne3
./case.setup
```

`user_nl_cam` (see `templates/testmod_fphystest/user_nl_cam`): `ncdata` is the CAM before
tape and `ncdata_check` the after tape, both still in the CAM run directory; `pver` equals the
snapshot's `lev`; `ncdata_check_err = .false.` while iterating so every step prints, `.true.`
for the committed test; `min_difference = 2e-15`; the scheme's own namelist switches with the
values the CAM run used; history fields for the diagnostics you want to see.

Write `user_nl_cam` from a local file (`ssh <host> 'cat > <case>/user_nl_cam' < file`)
rather than a heredoc nested inside a remote one-liner, which mangles quotes and newlines.
`./preview_namelists` runs the registry and capgen generators; metadata errors surface here,
before a build. Its success leaves `bld/atm/obj/ccpp/ccpp_<suite>_cap.F90` under the case
output root; `grep -A3 'call <scheme>_run'` there shows which host variable each argument
bound to, the fastest wiring check before any run. The CAM-SIMA documentation keeps a table
of capgen error messages and their fixes (escomp.github.io/CAM-SIMA-docs, conversion
section).

## Exit check

`suite-trace status` resolves every variable; `preview_namelists` succeeds; the case builds;
the proposed standard-name list and any host-variable proposals have been shown to the user.
