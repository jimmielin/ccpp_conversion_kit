# Standard Names Quick Reference

Common CAM local names mapped to the standard names CAM-SIMA and atmospheric_physics use
today. Every entry exists in the code with the units shown: validated on 2026-10-19 against
CAM-SIMA `development` (e82653c7) and atmospheric_physics `main` (0e30d83a) with
`tools/check_quick_ref.py`; rerun it after pulling, because names drift:

```
python3 -I tools/check_quick_ref.py references/standard_names_quick_ref.md <CAM-SIMA> <atmospheric_physics>
```

Names that exist in CAM but have no standard name yet (CLUBB moments, the microphysics
process tendencies, the hybrid coefficients `hyam`/`hybm`/`hyai`/`hybi`, which are netCDF
names only) are deliberately absent; construct them by the rules at the end and tag `_TBD`.
The blessed sources, in order: the CAM-SIMA host registry (`src/data/registry.xml`),
the host-side metadata for constants and composition (`src/data/physconst.meta`,
`air_composition.meta`, `ref_pres.meta`, `cam_thermo.meta`), and recently converted
schemes in atmospheric_physics. The ESCOMP/CCPPStandardNames repository lags; use it for
naming rules (StandardNamesRules.rst), not as proof that a name exists.

Format: `CAM local name` -> `standard_name` [`units`]

## Dimensions & grid

- `lon` -> `longitude` [rad]
- `lon (degrees)` -> `longitude_degrees_east` [degrees]
- `lat` -> `latitude` [rad]
- `lat (degrees)` -> `latitude_degrees_north` [degrees]
- `lev / pref_mid` -> `reference_pressure_in_atmosphere_layer` [Pa]
- `P0 / psurf_ref` -> `surface_reference_pressure` [Pa]
- `ilev / pref_edge` -> `reference_pressure_at_interface` [Pa]
- `cam_out_pbot` -> `air_pressure_at_bottom_layer_to_coupler` [Pa]
- `cam_out_psl` -> `air_pressure_at_sea_level_to_coupler` [Pa]
- `cam_out_thbot` -> `potential_temperature_wrt_surface_pressure_at_bottom_layer_to_coupler` [K]
- `cam_out_zbot` -> `geopotential_height_wrt_surface_at_bottom_layer_to_coupler` [m]
- `pbuf_QRL` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_longwave_radiation_adjusted_by_air_pressure_thickness` [J Pa kg-1 s-1]
- `pbuf_QRS` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_shortwave_radiation_adjusted_by_air_pressure_thickness` [J Pa kg-1 s-1]
- `state_exner` -> `reciprocal_of_dimensionless_exner_function_wrt_surface_air_pressure` [1]
- `state_lnpint` -> `ln_air_pressure_at_interface` [1]
- `state_lnpintdry` -> `ln_air_pressure_of_dry_air_at_interface` [1]
- `state_lnpmid` -> `ln_air_pressure` [1]
- `state_lnpmiddry` -> `ln_air_pressure_of_dry_air` [1]
- `state_omega` -> `lagrangian_tendency_of_air_pressure` [Pa s-1]
- `state_pdel` -> `air_pressure_thickness` [Pa]
- `state_pdeldry` -> `air_pressure_thickness_of_dry_air` [Pa]
- `state_phis` -> `surface_geopotential` [m2 s-2]
- `state_pint` -> `air_pressure_at_interface` [Pa]
- `state_pintdry` -> `air_pressure_of_dry_air_at_interface` [Pa]
- `state_pmid` -> `air_pressure` [Pa]
- `state_pmiddry` -> `air_pressure_of_dry_air` [Pa]
- `state_ps` -> `surface_air_pressure` [Pa]
- `state_psdry` -> `surface_pressure_of_dry_air` [Pa]
- `state_rpdel` -> `reciprocal_of_air_pressure_thickness` [Pa-1]
- `state_rpdeldry` -> `reciprocal_of_air_pressure_thickness_of_dry_air` [Pa-1]
- `state_zi` -> `geopotential_height_wrt_surface_at_interface` [m]
- `state_zm` -> `geopotential_height_wrt_surface` [m]
- `state_z_ini` -> `geopotential_height_wrt_surface_at_start_of_physics_timestep` [m]
- `ptend_s` -> `tendency_of_dry_air_enthalpy_at_constant_pressure` [J kg-1 s-1]
- `cpairv` -> `composition_dependent_specific_heat_of_dry_air_at_constant_pressure` [J kg-1 K-1]
- `cappa/kappa` -> `composition_dependent_ratio_of_dry_air_gas_constant_to_specific_heat_of_dry_air_at_constant_pressure` [1]
- `tropP` -> `tropopause_air_pressure` [Pa]
- `tropZ` -> `tropopause_geopotential_height_wrt_surface` [m]
- `pvliq` -> `magnitude_of_vertical_pressure_velocity_of_cloud_liquid_water_due_to_sedimentation` [Pa s-1]
- `pvice` -> `magnitude_of_vertical_pressure_velocity_of_cloud_ice_due_to_sedimentation` [Pa s-1]
- `evapheat` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_evaporation_of_precipitation` [J kg-1 s-1]
- `prfzheat` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_freezing_of_precipitation` [J kg-1 s-1]
- `meltheat` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_snow_melt` [J kg-1 s-1]
- `repartht` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_cloud_ice_and_cloud_liquid_repartitioning` [J kg-1 s-1]
- `cmeheat` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_condensation_minus_evaporation` [J kg-1 s-1]
- `dpidz_sq` -> `square_of_derivative_of_air_pressure_with_respect_to_height_at_interfaces_for_vertical_diffusion` [kg2 m-4 s-4]
- `eddy_max_bot_pressure` -> `air_pressure_threshold_for_maximum_turbulent_length_scale_application` [hPa]
- `cpair` -> `specific_heat_of_dry_air_at_constant_pressure` [J kg-1 K-1]
- `ncol (init, timestep_init, final)` -> `horizontal_dimension` [count]
- `ncol (run)` -> `horizontal_loop_extent` [count]
- `ptop_ref` -> `air_pressure_at_top_of_atmosphere_model` [Pa]
- `pver` -> `vertical_layer_dimension` [count]
- `pverp` -> `vertical_interface_dimension` [count]
- `pmid_day` -> `air_pressure_for_daytime_columns_for_RRTMGP` [Pa]
- `pint_day` -> `air_pressure_at_interface_for_daytime_columns_for_RRTMGP` [Pa]
- `dpdry` -> `air_pressure_thickness_of_dry_air_for_deep_convection_for_gathered_convective_columns` [hPa]
- `tend_s_snwprd` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_frozen_precipitation_production_due_to_deep_convection` [J kg-1 s-1]
- `tend_s_snwevmlt` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_evaporation_and_melting_of_frozen_precipitation_due_to_deep_convection` [J kg-1 s-1]
- `pguallu` -> `tendency_of_eastward_wind_due_to_zhang_mcfarlane_deep_convective_updraft_pressure_gradient_term` [m s-2]
- `pguallv` -> `tendency_of_northward_wind_due_to_zhang_mcfarlane_deep_convective_updraft_pressure_gradient_term` [m s-2]
- `pgdallu` -> `tendency_of_eastward_wind_due_to_zhang_mcfarlane_deep_convective_downdraft_pressure_gradient_term` [m s-2]
- `pgdallv` -> `tendency_of_northward_wind_due_to_zhang_mcfarlane_deep_convective_downdraft_pressure_gradient_term` [m s-2]

## State variables

- `cam_in_qref` -> `water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_at_2m_from_coupler` [kg kg-1]
- `cam_in_ssq` -> `sea_surface_saturation_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_from_coupler` [kg kg-1]
- `cam_in_tref` -> `air_temperature_at_2m_from_coupler` [K]
- `cam_in_wsx` -> `surface_eastward_wind_stress_from_coupler` [N m-2]
- `cam_in_wsy` -> `surface_northward_wind_stress_from_coupler` [N m-2]
- `cam_out_tbot` -> `air_temperature_at_bottom_layer_to_coupler` [K]
- `cam_out_ubot` -> `eastward_wind_at_bottom_layer_to_coupler` [m s-1]
- `cam_out_vbot` -> `northward_wind_at_bottom_layer_to_coupler` [m s-1]
- `cnst_Q and state%q(:,:,1)` -> `water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `pbuf_ICWMRDP` -> `in_cloud_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_deep_convection` [kg kg-1]
- `pbuf_ICWMRSH` -> `in_cloud_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_shallow_convection` [kg kg-1]
- `pbuf_QINI` -> `water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_before_physics` [kg kg-1]
- `pbuf_UM` -> `eastward_wind` [m s-1]
- `pbuf_VM` -> `northward_wind` [m s-1]
- `pbuf_qpert` -> `convective_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_perturbation_due_to_pbl_eddies` [kg kg-1]
- `state_s` -> `dry_static_energy` [J kg-1]
- `state_t` -> `air_temperature` [K]
- `state_temp_ini` -> `air_temperature_at_start_of_physics_timestep` [K]
- `tropT` -> `tropopause_air_temperature` [K]
- `pbuf_QCWAT` -> `water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_on_previous_timestep` [kg kg-1]
- `pbuf_TCWAT` -> `air_temperature_on_previous_timestep` [K]
- `kqfs` -> `kinematic_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_flux_at_surface` [kg kg-1 m s-1]
- `tint` -> `air_temperature_at_interfaces_for_vertical_diffusion` [K]
- `t_toai` -> `air_temperature_at_interface_above_top_of_atmosphere_for_vertical_diffusion` [K]
- `dse_top` -> `dry_static_energy_at_top_of_atmosphere_tbd` [J kg-1]
- `u (provisional after vdiff)` -> `eastward_wind_after_vertical_diffusion` [m s-1]
- `v (provisional after vdiff)` -> `northward_wind_after_vertical_diffusion` [m s-1]
- `dse (provisional after vdiff)` -> `dry_static_energy_after_vertical_diffusion` [J kg-1]
- `usteer` -> `eastward_wind_at_steering_level_due_to_moving_mountain_gravity_wave_drag` [m s-1]
- `vsteer` -> `northward_wind_at_steering_level_due_to_moving_mountain_gravity_wave_drag` [m s-1]
- `t_day` -> `air_temperature_for_daytime_columns_for_RRTMGP` [K]
- `icwuu` -> `in_cloud_eastward_wind_in_updraft_due_to_deep_convection` [m s-1]
- `icwuv` -> `in_cloud_northward_wind_in_updraft_due_to_deep_convection` [m s-1]
- `icwdu` -> `in_cloud_eastward_wind_in_downdraft_due_to_deep_convection` [m s-1]
- `icwdv` -> `in_cloud_northward_wind_in_downdraft_due_to_deep_convection` [m s-1]

## Physical constants

- `pbuf_REI` -> `effective_radius_of_stratiform_cloud_ice_crystal` [um]
- `pbuf_REL` -> `effective_radius_of_stratiform_cloud_liquid_water_droplet` [um]
- `rairv` -> `composition_dependent_gas_constant_of_dry_air` [J kg-1 K-1]
- `isrootproc` -> `flag_for_mpi_root` [flag]
- `rairi` -> `gas_constant_of_dry_air_at_interfaces_for_vertical_diffusion` [J K-1 kg-1]
- `latice` -> `latent_heat_of_fusion_of_water_at_0c` [J kg-1]
- `latvap` -> `latent_heat_of_vaporization_of_water_at_0c` [J kg-1]
- `pi` -> `pi_constant` [1]
- `gravit` -> `standard_gravitational_acceleration` [m s-2]
- `rearth` -> `radius_of_earth` [m]
- `rga` -> `reciprocal_of_gravitational_acceleration` [s2 m-1]
- `rearth_recip` -> `reciprocal_of_radius_of_earth` [m-1]
- `rair` -> `gas_constant_of_dry_air` [J kg-1 K-1]
- `cpvir` -> `ratio_of_specific_heat_of_water_vapor_to_specific_heat_of_dry_air_minus_one` [1]
- `Cpd_on_Cpv` -> `ratio_of_specific_heat_of_dry_air_to_specific_heat_of_water_vapor` [1]

## Tendencies

- `pbuf_FRZCNT` -> `tendency_of_cloud_liquid_droplet_number_concentration_due_to_contact_freezing` [cm-3]
- `pbuf_FRZDEP` -> `tendency_of_cloud_ice_number_concentration_due_to_deposition_nucleation` [cm-3]
- `pbuf_FRZIMM` -> `tendency_of_cloud_liquid_droplet_number_concentration_due_to_immersion_freezing` [cm-3]
- `pbuf_TTEND_CLUBB` -> `tendency_of_air_temperature_due_to_clubb` [K s-1]
- `pbuf_TTEND_DP` -> `tendency_of_air_temperature_due_to_deep_convection` [K s-1]
- `tend_dtdt` -> `tendency_of_air_temperature_due_to_model_physics` [K s-1]
- `tend_dudt` -> `tendency_of_eastward_wind_due_to_model_physics` [m s-2]
- `tend_dvdt` -> `tendency_of_northward_wind_due_to_model_physics` [m s-2]
- `ptend_u` -> `tendency_of_eastward_wind` [m s-2]
- `ptend_v` -> `tendency_of_northward_wind` [m s-2]
- `tphysac_rliq` -> `vertically_integrated_cloud_liquid_water_tendency_due_to_all_convection_to_be_applied_later_in_time_loop` [m s-1]
- `tphysac_rliq2` -> `vertically_integrated_cloud_liquid_water_tendency_due_to_shallow_convection_to_be_applied_later_in_time_loop` [m s-1]
- `qtend` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_not_due_to_microphysics` [kg kg-1 s-1]
- `ttend` -> `tendency_of_air_temperature_not_due_to_microphysics` [K s-1]
- `ice2pr` -> `tendency_of_cloud_ice_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_ice_to_snow_autoconversion` [kg kg-1 s-1]
- `liq2pr` -> `tendency_of_cloud_liquid_water_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_liquid_to_rain_autoconversion` [kg kg-1 s-1]
- `liq2snow` -> `tendency_of_cloud_liquid_water_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_liquid_to_snow_autoconversion` [kg kg-1 s-1]
- `No CAM equivalent` -> `do_output_of_tendency_of_air_temperature_due_to_shortwave_heating_on_radiation_timestep_assuming_clear_sky` [flag]
- `ptend%q(:,:,1)` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]

## Cloud & convection

- `cnst_CLDICE` -> `cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `cnst_CLDLIQ` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `cnst_NUMLIQ` -> `mass_number_concentration_of_cloud_liquid_water_droplets_in_moist_air_and_condensed_water` [kg-1]
- `cnst_NUMICE` -> `mass_number_concentration_of_cloud_ice_water_crystals_in_moist_air_and_condensed_water` [kg-1]
- `pbuf_AIST` -> `stratiform_cloud_ice_area_fraction` [fraction]
- `pbuf_ALST` -> `stratiform_cloud_liquid_area_fraction` [fraction]
- `pbuf_DEI` -> `effective_diameter_of_stratiform_cloud_ice_crystal_for_radiation` [um]
- `pbuf_DLFZM` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_deep_convection` [kg kg-1 s-1]
- `pbuf_SNOW_SED` -> `stratiform_lwe_cloud_ice_surface_flux_due_to_sedimentation` [m s-1]
- `pbuf_SNOW_STR` -> `lwe_snow_and_cloud_ice_precipitation_rate_at_surface_due_to_microphysics` [m s-1]
- `tphysac_dlf` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_all_convection` [kg kg-1 s-1]
- `tphysac_dlf2` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_shallow_convection` [kg kg-1 s-1]
- `pracwo` -> `accretion_of_cloud_liquid_water_by_rain` [s-1]
- `psacwo` -> `accretion_of_cloud_liquid_water_by_snow` [s-1]
- `psacio` -> `accretion_of_cloud_ice_by_snow` [s-1]
- `cmeice` -> `rate_of_condensation_minus_evaporation_for_cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]
- `cmeliq` -> `rate_of_condensation_minus_evaporation_for_cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]
- `fwaut` -> `relative_importance_of_cloud_liquid_water_autoconversion` [fraction]
- `fsaut` -> `relative_importance_of_cloud_ice_autoconversion` [fraction]
- `fracw` -> `relative_importance_of_rain_accreting_cloud_liquid_water` [fraction]
- `fsacw` -> `relative_importance_of_snow_accreting_cloud_liquid_water` [fraction]
- `fsaci` -> `relative_importance_of_snow_accreting_cloud_ice` [fraction]
- `qlfd` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_for_eddy_diffusion` [kg kg-1]
- `cld` -> `cloud_area_fraction` [fraction]
- `pbuf%ICLWP` -> `in_cloud_liquid_water_path_for_radiation` [kg m-2]
- `pbuf%ICIWP` -> `in_cloud_ice_water_path` [kg m-2]

## Surface

- `cam_in_cflx` -> `surface_upward_ccpp_constituent_fluxes_from_coupler` [kg m-2 s-1]
- `cflx` -> `surface_upward_ccpp_constituent_fluxes_for_vertical_diffusion` [kg m-2 s-1]

## Framework

- `mdt` -> `timestep_for_physics` [s]
- `num_constituents` -> `number_of_ccpp_constituents` [count]
- `qprops` -> `ccpp_constituent_properties` [none]
- `qmin` -> `ccpp_constituent_minimum_values` [kg kg-1]
- `q` -> `ccpp_constituents` [none]
- `iulog` -> `log_output_unit` [1]
- `do_diffusion_const` -> `flag_for_ccpp_constituent_vertical_diffusion` [flag]
- `q (provisional after vdiff)` -> `ccpp_constituents_after_vertical_diffusion` [none]
- `ubc_mmr` -> `upper_boundary_condition_of_ccpp_constituents` [none]
- `cnst_fixed_ubc` -> `use_fixed_upper_boundary_condition_of_ccpp_constituents_tbd` [flag]
- `dqdt` -> `ccpp_constituent_tendencies` [none]

## Other commonly used

- `omega` -> `angular_velocity_of_earth_rotation` [rad s-1]
- `ncol (RRTMGP shortwave block)` -> `number_of_columns_per_shortwave_block_for_RRTMGP` [count]
- `ncol (RRTMGP longwave block)` -> `number_of_columns_per_longwave_block_for_RRTMGP` [count]

## Name families

Gravity-wave tendencies are one name per source rather than one generic name:
`tendency_of_eastward_wind_due_to_<source>_gravity_wave_drag` (also `northward_wind`,
`air_temperature`, and `ccpp_constituent_tendencies_due_to_<source>_gravity_wave_drag`),
with `<source>` one of `orographic`, `deep_convective`, `shallow_convective`,
`frontogenesis`, `frontogenesis_inertial`, `moving_mountain`. Grep for `_gravity_wave_drag`
in the metadata to see the current set.

## Constructing New Standard Names

If a standard name is not in the code, construct one following ESM rules:

```
[transformation] [component] base_name [in/of medium] [at level] [due_to process] [assuming condition]
```

Key rules:
- Fortran logicals: `flag_for_X`; other control variables: `control_for_X`
- Mixing ratios: specify `wrt_dry_air`, `wrt_moist_air`, or `wrt_moist_air_and_condensed_water`
- Tunable parameters: `tunable_parameter[s]_for_X`
- Append `_TBD` to names not yet discussed/approved
- Species: follow the spelling already in the code for that species and never introduce
  a second one. The CCPPStandardNames rules spell species out (`ozone`, `carbon_dioxide`)
  and so do the prescribed-data options (`filename_of_prescribed_ozone`), while the
  constituent and property names use formulae (`molecular_weight_of_o3`, `co2`); grep
  both before choosing

## Dimensionless Units

| Unit     | Use case                                      |
|:---------|:----------------------------------------------|
| count    | array dimensions/lengths                      |
| flag     | logicals (true/false)                         |
| index    | array indices                                 |
| kg kg-1  | mass mixing ratios                            |
| mol mol-1| molar/volume mixing ratios                    |
| fraction | fractions in [0,1]                            |
| percent  | fractions in [0,100]                          |
| none     | strings/characters                            |
| 1        | other dimensionless numbers (scaling, codes)  |
