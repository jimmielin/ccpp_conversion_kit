# Example: iondrag_calc_ghg (demo opener)

The greenhouse-gas path of WACCM ion drag: a globally uniform ion-drag tensor applied to the
winds above about 90 km. Chosen as the first live conversion because it is on the WACCM
sheet, has a named snapshot point, no namelist on this path, about ninety lines of run code,
and just enough structure to exercise every step of the pipeline: init-time tables
interpolated onto the model's reference pressures, latitude-dependent geometry, vertical range
gating, module state, two history fields, and one dependency to triage.

Source: `CAM/src/physics/waccm/iondrag.F90` (cam_development, October 2026):
`iondrag_init` (activation and dispatch), `ghg_init` (tables and interpolation),
`iondrag_timestep_init` (no-op on this path), `iondrag_calc` (dispatcher),
`iondrag_calc_ghg` (the physics). The ions path (`ions_init`, `iondrag_calc_ions`) stays in
CAM for now; the dispatcher keeps calling it.

## Inventory (phase 1)

| Quantity | CAM source | Role | CAM-SIMA standard name | Snapshot field |
|---|---|---|---|---|
| u, v | `state%u`, `state%v` | in | `eastward_wind`, `northward_wind` | `state_u`, `state_v` |
| latitude | `get_rlat_all_p(lchnk, pcols, clat)` | in, radians | `latitude` (confirm units in the host meta) | host grid |
| reference pressure at midpoints | `pref_mid(pver)` at init | in (init) | `reference_pressure_in_atmosphere_layer` [Pa] | host |
| ion-drag tensor tables | `alamxx`, `alamxy` data statements over `plevtiod` TIME-GCM levels, `pshtiod` built from -17 in steps of 0.25 and shifted by `log(preftgcm/1e5)`, `preftgcm = 5e-5 Pa` | module parameters | n/a | n/a |
| interpolated tensors | `alamxxi(pver)`, `alamxyi(pver)` via `lininterp` onto `pshccm = log(1e5/pref_mid)` with the vertical index inverted and inverted back | module state set at init | n/a | n/a |
| activation | `nbot_lev` = last level with `log(1e5/pref_mid) > 14`; `ntop_lev = 1`; `doiodrg = nbot_lev > ntop_lev` | module state | n/a | init log prints `IONDRAG flag is` |
| tendencies | `ptend%u`, `ptend%v` (`lu`, `lv` true) | out | `tendency_of_eastward_wind`, `tendency_of_northward_wind` (first drafted as `..._due_to_ion_drag_TBD`; the generic names won at review, see the standard-name table below) | `ptend_u`, `ptend_v` on the after tape |
| diagnostics | `UIONTEND`, `VIONTEND` (`outfld` inside the scheme); `UTEND_IONDRG`, `VTEND_IONDRG` (`outfld` of ptend in physpkg) | history | `<scheme>_diagnostics` | compare via cprnc |

Dependency to triage: `lininterp` from `src/utils/interpolate_data.F90`. Three options were
weighed: (a) `use interpolate_data, only: lininterp` as a host-provided module, the precedent
set by `schemes/gravity_wave_drag/gw_common.F90` and `schemes/rrtmgp/utils/radiation_utils.F90`
(both CAM and CAM-SIMA ship `src/utils/interpolate_data.F90`; `fbody --walk` across the two
repos shows the lininterp family identical except one literal in the unused cyclic branch);
(b) vendor `lininterp_full1d`, `lininterp_init`, `lininterp1d`, `lininterp_finish` verbatim
into the scheme directory with `endrun` turned into `errmsg`/`errflg` (about 300 lines,
b4b by construction, duplicated for every later scheme that needs it); (c) promote the
lininterp family to `to_be_ccppized`, which needs an SE discussion. The dry run took (a) for
the demo, following the precedent; the user reviews this before the PR. Note that (a) is
outside the `AGENTS.md` portability list, so (c) is the likely long-term answer once a second
scheme (qbo, aurora) needs the same routine.

Regime: physpkg, `tphysac`, after the lunar tides call and before the WACCM-X electron
temperature call. The `iondrag_calc_section` bracket covers `iondrag_calc`, the WACCM-X call
(inactive here), the `UTEND_IONDRG`/`VTEND_IONDRG` outfld, and `physics_update`.

## Configuration (phase 2)

Route C: CAM6 SC-WACCM (`FWsc2000climo`, L70) at `ne3pg3_ne3pg3_mg37`. No ions, so
`do_waccm_ions` is false and the ghg path runs; the L70 top (pressures down to about
5e-4 Pa) satisfies the activation gate. No ne3 initial condition exists for L70, so one is
regridded from the ne30pg3 L70 WACCM IC with `ESMF_RegridWeightGen` and `ncremap`
(`tools/interpic_new` cannot regrid SE to SE). Commands, in order, in `derecho-prep.md`.

Snapshot point: `iondrag_calc_section` (method A). The CAM case is created dechunked with
one task so the same build serves dropsonde in phase 5.

## Suite (phase 3)

```
<group name="physics_after_coupler">
  <scheme>iondrag_ghg</scheme>
  <scheme>iondrag_ghg_diagnostics</scheme>
  <scheme>apply_tendency_of_eastward_wind</scheme>
  <scheme>apply_tendency_of_northward_wind</scheme>
</group>
```

Phases: `_init` (tables, interpolation, activation, from `pref_mid` and `pver`), `_run`
(tendencies; zero when inactive), `_timestep_init` not needed on this path.

## What this example should teach

1. The inventory table drives everything downstream; fill it before touching code.
2. Splice and prove with `fbody` before building anything.
3. A named snapshot point means phase 2 is a `user_nl_cam` edit, but the bracket defines what
   the suite must reproduce.
4. Dependency triage is a decision, not a reflex.
5. The first CAM-SIMA run is read from the top of `atm.log`: IC reads, init table, then the
   check blocks.

## Standard names used (user review before the PR)

| Argument | Phase | Standard name | Provider |
|---|---|---|---|
| `pver` | init | `vertical_layer_dimension` | host |
| `pref_mid` | init | `reference_pressure_in_atmosphere_layer` [Pa] | host `ref_pres::pref_mid` |
| `masterproc` | init | `flag_for_mpi_root` | host `spmd_utils` |
| `iulog` | init | `log_output_unit` | host `cam_logfile` |
| `ncol` | run | `horizontal_loop_extent` | host |
| `clat` | run | `latitude` [rad] | host `physics_grid::lat_rad` |
| `u`, `v` | run | `eastward_wind`, `northward_wind` | registry |
| `dudt`, `dvdt` | run, out | `tendency_of_eastward_wind`, `tendency_of_northward_wind` | this scheme; consumed by `iondrag_ghg_diagnostics` and `apply_tendency_of_*_wind` |

The generic tendency names follow `rayleigh_friction`. A per-process name
(`tendency_of_eastward_wind_due_to_ion_drag`) would need an interstitial to copy into the
generic tendency before the applier, as the gravity-wave schemes do; not worth it for a
single-source tendency. The diagnostics scheme writes `UIONTEND`/`VIONTEND` (CAM's
iondrag module names) and `UTEND_IONDRG`/`VTEND_IONDRG` (CAM's physpkg names) from the same
arrays.

## Status

October 2026 dry run, Claude driving, autonomy 2.

Phase 2 (done before phase 1 here, because the baseline run doubles as the b4b reference):
- CAM case `/glade/derecho/scratch/hplin/261006_conversion_demo/cam_fwsc_iondrag`, run
  directory `/glade/derecho/scratch/hplin/cam_fwsc_iondrag/run`, unsplit `cam_development`
  69663339b, `-phys cam6 -chem waccm_sc_mam4 -pcols 486`, DEBUG, NTASKS=1, STOP_N=6.
- IC `ic/FW2000_ne3np4_L70_from_ne30pg3_c20261006.nc` (ESMF bilinear from the ne30pg3 L70
  WACCM IC; interpic cannot do SE to SE).
- Init log: `NTOP_LEV = 1`, `NBOT_LEV = 10`, `IONDRAG flag is T`. Six `nstep, te` lines
  after step 0, no blow-up.
- Tapes: `cam_fwsc_iondrag.cam.h5i.0001-01-01-01800.nc` (before) and
  `cam_fwsc_iondrag.cam.h6i.0001-01-01-01800.nc` (after), 6 frames each, float64;
  `state_u`/`state_v` on both, `ptend_u`/`ptend_v`/`ptend_s` on the after tape.

Phase 1 (rung 0 passed locally):
- atmospheric_physics branch `hplin/iondrag_demo` (fork jimmielin): `schemes/iondrag/
  iondrag_ghg.{F90,meta}`, `schemes/sima_diagnostics/iondrag_ghg_diagnostics.{F90,meta}`,
  `test/test_suites/suite_iondrag_ghg.xml`.
- CAM branch `hplin/iondrag_demo`: `src/physics/waccm/iondrag.F90` edited in place (ghg data,
  `ghg_init`, and the body of `iondrag_calc_ghg` moved out; the dispatcher and the ions path
  stay), `bld/configure` lists `schemes/iondrag`.
- `fbody --walk`: eight untouched units IDENTICAL; `iondrag_init` DIFF 8 (new call),
  `ghg_init` to `iondrag_ghg_init` DIFF 31 (arguments, allocate, masterproc guard),
  `iondrag_calc_ghg` DIFF 38 (now the CAM interface). Both 97-value tables diff clean.
- Syntax-only compile ok; `suite-trace status` resolves everything; `audit` and `read-before-write`
  clean; CCPP lint clean.
- Rung 1 and 2 passed (2026-10-06): `cam_fwsc_iondrag_split` (create_clone of the baseline,
  built from CAM b29b70c28 with atmospheric_physics e4978517) gives identical `nstep, te`
  lines for all 8 printed steps, and cprnc reports the before tape (2969 fields) and the
  after tape (3779 fields) IDENTICAL against the baseline. The split run's init log matches
  (`NBOT_LEV = 10`, `IONDRAG flag is T`). Phase 1 exit check met.

Phase 3 (done the same day, overlapped with the phase 1 run):
- CAM-SIMA case `sima_iondrag_ghg` (FPHYStest, `--dyn none --physics-suites iondrag_ghg`,
  pver 70, DEBUG, NTASKS 1, STOP_N 6), `ncdata`/`ncdata_check` on the baseline tapes in the
  CAM run directory, `ncdata_check_err = .false.` while iterating. `preview_namelists`
  generated `ccpp_iondrag_ghg_cap.F90` binding `lat_rad`, `pref_mid`, `masterproc`, `iulog`;
  the build succeeded.

Phase 4 (2026-10-06): first run, every step clean for the state; four steps listed one to
three points of `tendency_of_northward_wind_due_to_model_physics` at 2e-15 to 1.3e-14
(relative). Init table and IC reads clean.

Phase 5 (2026-10-06): dropsonde report `dropsonde_report_1.txt` (4 minutes under qcmd).
First divergence: input `clat`, 44/486 columns differ by 1.1e-16; output `dvdt` 69/34020
points at 1.7e-18; `dudt` bitwise. Classification: harness. The null dycore converts the
snapshot's degrees latitude to radians, CAM hands the scheme native radians. The port is
bit-for-bit on identical inputs. Resolution in the dry run: exclude the northward
accumulator with a comment and rerun with `ncdata_check_err = .true.`: six steps clean,
exclusion printed every step. Decision (Haipeng, same day): host fix. CAM 6fc7772fa writes
`lat_rad`/`lon_rad` on the snapshot tapes (`cam_snapshot_common.F90`, registered from
`cam_snapshot_init`), CAM-SIMA 89beb07f makes the null dycore prefer them on unstructured
grids (`read_radians_coord` in `src/dynamics/none/dyn_grid.F90`). Each is a distinct commit
so it can be split out of the iondrag PRs and ride a misc tag. The split case was rerun to
produce tapes with the fields (`lat_rad`, `lon_rad`, radians, both tapes; cprnc against the
unsplit baseline still IDENTICAL on every common field) and the CAM-SIMA test switched to
those tapes without the exclusion (CAM-SIMA bcfc581c): hard check clean on all six steps,
the log prints `read_radians_coord: using lat_rad ...`. Second dropsonde run
(`dropsonde_report_2.txt`): no differences in any subroutine, 30 argument captures
byte-for-byte identical. Dry-run acceptance met.

Phase 6 (partly): CAM-SIMA testmod `outfrq_iondrag_ghg_derecho` and the `testlist_cam.xml`
entry are committed on `hplin/iondrag_demo` with the snapshot paths still in the split
case's run directory. Still to do before the PRs: style pass on the moved lines (`.gt.`,
`endif`), snapshots to `sima_baselines` with the
`cam<tag>_ne3pg3_fwsc_iondrag_ghg_snapshot_derecho_gnu_*` names (from a CAM build that
includes the `lat_rad` commit), `aux_cam` (rung 3) for the CAM PR, the three PRs in order,
with the two host commits (CAM 6fc7772fa, CAM-SIMA 89beb07f) split off to ride misc tags.

`dry-run-log.md` lists what the guides got wrong; all entries are folded.
