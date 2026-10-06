# WACCM and WACCM-X scheme sheet, keyed to what reaches each item at ne3pg3

The sheet below is the HAO/ACOM-reviewed list of WACCM schemes to CCPPize, annotated with
the configuration that activates each one at the smallest grid CAM-SIMA tests use
(`ne3pg3_ne3pg3_mg37`, SE dycore), the snapshot method from `guides/20-snapshots.md`, and the
host-side gaps found by reading the CAM source (cam_development, October 2026). Verify
activation against the init log of a real run before relying on a row.

## Routes

| Route | Configuration | Prep | What it activates |
|---|---|---|---|
| A | CAM7 mid-top with TS1 chemistry: `FHISTC_MTt1s` (L93). `-waccm_phys` was added to the mid-top chemistry compsets in cam6_4_149 to include chemical heating. ne3 IC and an izumi `SMS_D_Ln9` test exist. | none | radheat_tend on its WACCM path (gate `pref_mid(1) <= 5 Pa`) with waccm_hrates and nlte_lw; aoa_tracers; lunar_tides. NOT iondrag (needs `pref_mid(1) < 0.1 Pa`), no ions. |
| C | CAM6 specified-chemistry WACCM: `FWsc2000climo` (`-chem waccm_sc_mam4`, L70). No ne3 IC: make one with `tools/interpic_new` from the ne30pg3 L70 WACCM IC (see `examples/iondrag_calc_ghg/derecho-prep.md`). | one IC regrid | iondrag_calc_ghg and iondrag_timestep_init (no ions, so `do_waccm_ions` is false); radheat_tend with get_solar from the forcing file plus nlte_tend; aoa_tracers; lunar_tides. |
| B | Middle-atmosphere chemistry: `FWma2000climo` (CAM6, L70) with an interpic IC from f19 L70, or CAM7 `%WA` (`-model_top ht`, L135; no IC found in the namelist defaults). | IC regrid, longer runs, species present | everything with ions: charge_balance, iondrag_calc_ions with efield/exbdrift/heelis/mo_apex, aurora; radheat_tend with waccm_hrates. |

qbo is unreachable on all routes: its input `UZM` is a pbuf field that only the FV dycore
registers, and `build-namelist` enables qbo forcing only on coarse FV grids. It needs a
host-side zonal-mean provider in CAM-SIMA first.

## WACCM

| Item | CAM source | Regime | Route | Snapshot method | Dependencies and host gaps | Notes |
|---|---|---|---|---|---|---|
| charge_balance (charge_fix_vmr) | chemistry/mozart/charge_neutrality.F90 | chemistry-embedded (inside gas_phase_chemdr, before setinv and after imp_sol) | B | D interior capture of the vmr array | species indices by name, adv_mass | pairs with the MICM/chemistry port; electrons are an ordinary implicit species |
| charge_balance (charge_fix_mmr) | same file | physpkg (tphysac, before gw_tend; again after ionosphere) | B | C user_set | mbarv (air_composition exists in CAM-SIMA), short-lived species pbuf (no CAM-SIMA counterpart yet: design decision), adv_mass via constituent properties | about 90 lines; a good second-session scheme once Route B exists |
| qbo_relax | physics/waccm/qbo.F90 | physpkg (tphysac) | none | A named point exists | UZM zonal mean from FV dycore; current year, month, day (host time variables) | parked until a zonal-mean provider exists |
| iondrag_timestep_init | physics/waccm/iondrag.F90 | timestep_init | B, C | n/a | efield get_efield on the ions path; no-op on the ghg path | |
| iondrag_calc_ions | physics/waccm/iondrag.F90 | physpkg (tphysac) | B | A `iondrag_calc_section` | efield (1526 lines), exbdrift (439), heelis_mod (227), mo_apex (400) plus apex library, pbuf UI/VI/WI, TElec/TIon for WACCM-X | large; the geomagnetic coordinate provider is a host-service design question |
| iondrag_calc_ghg | physics/waccm/iondrag.F90 | physpkg (tphysac) | C | A `iondrag_calc_section` | lininterp from interpolate_data (vendor), `pref_mid`, latitude | DEMO OPENER; see `examples/iondrag_calc_ghg/` |
| radheat_tend | physics/waccm/radheat.F90 | inside radiation_tend | A, C | C user_set inside radiation.F90, or D for qrs_mlt/qrl_mlt | nlte_lw driver (447) over nlte_fomichev (already in to_be_ccppized/radiation_utils), waccm_forcing get_solar (288), waccm_hrates (chemistry heating, Route A only), tidal_diag, cpairv, gravit | claimed by a teammate; CAM-SIMA's calculate_net_heating is the non-WACCM counterpart to extend |
| aurora_timestep_init / aurora_hrate / aurora_prod | physics/waccm/mo_aurora.F90 | chemistry-embedded (mo_setext fills extfrc ion production; mo_waccm_hrates for heating) | B | D interior capture of the extfrc slices | mo_apex, heelis_mod, mag_parms, aurora_params, pbuf AurIPRateSum / QTeAur | later session; capture design first |
| pp_waccm_ma_mam5 | chemistry/pp_waccm_ma_mam5 | mechanism | n/a | n/a | MICM route under separate scoping | not a scheme conversion |

## WACCM-X increment

| Item | CAM source | Regime | Route | Snapshot method | Dependencies and host gaps | Notes |
|---|---|---|---|---|---|---|
| lunar tides | physics/cam/lunar_tides.F90 | physpkg (tphysac, after qbo) | A, C | C user_set | pi, rearth, zm, lat, lon; year, month, day, seconds, Julian day (host time variables); CALENDAR=GREGORIAN | 150 lines; the CAM-SIMA documentation walkthrough example; zero-prep fallback |
| electrodynamo | ionosphere/waccmx | host service | out of scope this cycle | | | |
| molecular diffusion | physics/cam vertical diffusion (`do_molec_diff`) | extension of the CCPPized vertical diffusion | B, C | existing vertical_diffusion_section bracket | needed by WACCM-MA, not only WACCM-X | |
| ion drag efield / exbdrift / heelis | physics/waccm | dependencies of iondrag_calc_ions and aurora | B | | see iondrag_calc_ions | |
| NLTE | to_be_ccppized/radiation_utils/nlte_fomichev.F90 (done); nlte_lw.F90 driver remains | inside radheat | A, C | with radheat | waccm_forcing for the specified-chemistry path | |
| UBC / MSIS / TGCM / SNOE | physics/cam ubc, msis library | host service applied in vertical diffusion | B | | needed by WACCM-MA | |
| ionosphere dycore | ionosphere/waccmx | out of scope this cycle | | | | |

## Not on the sheet, reachable, worth assigning

| Item | CAM source | Route | Snapshot method | Notes |
|---|---|---|---|---|
| aoa_tracers | physics/cam/aoa_tracers.F90 | A, C | A `aoa_tracers_timestep_tend` | on by default with waccm_phys; registers constituents; time_manager heavy; restart state; atmospheric_physics issue #24 has asked for a suite since 2021 |

## Host time variables

CAM-SIMA exposes `fractional_calendar_days_on_end_of_current_timestep`,
`timestep_for_physics`, `current_timestep_number`, `is_first_timestep`. Year, month, day,
seconds of day, and a Julian day do not exist yet; qbo, lunar tides, and aoa_tracers all need
some of them. Decision taken for the series: expose them host-side from `time_manager`
through host metadata (a registry variable set each step, as `calday` is, or a host `.meta`).
