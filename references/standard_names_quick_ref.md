# Standard Names Quick Reference

Most commonly needed standard names for CCPP conversions.
The blessed sources, in order: the CAM-SIMA host registry (`src/data/registry.xml`),
the host-side metadata for constants and composition (`src/data/physconst.meta`,
`air_composition.meta`, `ref_pres.meta`, `cam_thermo.meta`), and recently converted
schemes in atmospheric_physics. The ESCOMP/CCPPStandardNames repository lags; use it for
naming rules (StandardNamesRules.rst), not as proof that a name exists.

Format: `CAM local name` -> `standard_name` [`units`]

## Dimensions & grid

- `lon` -> `longitude` [degrees east]
- `lev` -> `reference_pressure_in_atmosphere_layer` [hPa]
- `hyam` -> `sigma_pressure_hybrid_coordinate_a_coefficient` [1]
- `hybm` -> `sigma_pressure_hybrid_coordinate_b_coefficient` [1]
- `P0` -> `reference_pressure` [Pa]
- `ilev` -> `reference_pressure_in_atmosphere_layer_at_interfaces` [hPa]
- `hyai` -> `sigma_pressure_hybrid_coordinate_a_coefficient_at_interfaces` [1]
- `hybi` -> `sigma_pressure_hybrid_coordinate_b_coefficient_at_interfaces` [1]
- `cam_out_pbot` -> `air_pressure_at_bottom_layer_to_coupler` [Pa]
- `cam_out_psl` -> `air_pressure_at_sea_level_to_coupler` [Pa]
- `cam_out_thbot` -> `potential_temperature_wrt_surface_pressure_at_bottom_layer_to_coupler` [K]
- `cam_out_zbot` -> `geopotential_height_wrt_surface_at_bottom_layer_to_coupler` [m]
- `pbuf_PSL` -> `air_pressure_at_sea_level` [Pa]
- `pbuf_QRL` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_longwave_radiation_adjusted_by_air_pressure_thickness?` [K s-1]
- `pbuf_QRS` -> `tendency_of_dry_air_enthalpy_at_constant_pressure_due_to_shortwave_radiation_adjusted_by_air_pressure_thickness?` [K s-1]
- `state_exner` -> `inverse_exner_function_wrt_surface_pressure` [?]
- `state_lnpint` -> `ln_air_pressure_at_interfaces` [1]
- `state_lnpintdry` -> `ln_air_pressure_of_dry_air_at_interfaces` [1]
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
- `zi` -> `geopotential_height_wrt_surface_at_interfaces` [m]
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
- `thv` -> `virtual_potential_temperature_wrt_surface_pressure_at_bottom_layer` [K]
- `dpidz_sq` -> `square_of_derivative_of_air_pressure_with_respect_to_height_at_interfaces_for_vertical_diffusion` [kg2 m-4 s-4]
- `kvtt (kvt_gw)` -> `thermal_conductivity_coefficient_at_interfaces_divided_by_specific_heat_of_dry_air_at_constant_pressure` [K s]
- `eddy_max_bot_pressure` -> `air_pressure_threshold_for_maximum_turbulent_length_scale_application` [hPa]
- `cpair` -> `specific_heat_of_dry_air_at_constant_pressure` [J kg-1 K-1]
- `ncol` -> `horizontal_dimension (non-run phase) / horizontal_loop_extent (run phase)` [count]
- `ptop_ref` -> `air_pressure_at_top_of_atmosphere_model` [Pa]
- `clim_modal_aero_top_lev` -> `index_of_air_pressure_at_top_of_aerosol_model` [index]
- `pver` -> `vertical_layer_dimension` [count]
- `pverp` -> `vertical_interface_dimension` [count]
- `pmid_day` -> `air_pressure_for_daytime_points_for_RRTMGP` [?]
- `pint_day` -> `air_pressure_at_interface_for_daytime_points_for_RRTMGP` [?]
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
- `pbuf_RTPTHLP_nadv` -> `covariance_of_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air_and_liquid_water_potential_temperature_at_interfaces` [kg kg-1 K]
- `pbuf_RTPTHVP` -> `covariance_of_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air_and_virtual_potential_temperature_at_interfaces` [kg kg-1 K]
- `pbuf_UM` -> `eastward_wind` [m s-1]
- `pbuf_UP2_nadv` -> `advected_variance_of_eastward_wind_at_interfaces` [m2 s-2]
- `pbuf_UP3` -> `third_moment_of_eastward_wind` [m3 s-3]
- `pbuf_UPRCP` -> `covariance_of_eastward_wind_and_cloud_liquid_mixing_ratio_wrt_dry_air_at_interfaces` [m s-1 kg kg-1]
- `pbuf_UPWP` -> `covariance_of_eastward_wind_and_and_vertical_velocity_at_interfaces` [m2 s-2]
- `pbuf_VM` -> `northward_wind` [m s-1]
- `pbuf_VP2_nadv` -> `advected_variance_of_northward_wind_at_interfaces` [m2 s-2]
- `pbuf_VP3` -> `third_order_moment_of_northward_wind` [m3 s-3]
- `pbuf_VPRCP` -> `covariance_of_northward_wind_and_cloud_liquid_mixing_ratio_wrt_dry_air_at_interfaces` [m s-1 kg kg-1]
- `pbuf_VPWP` -> `covariance_of_northward_wind_and_vertical_velocity_at_interfaces` [m2 s-2]
- `pbuf_WP2UP2` -> `fourth_order_moment_of_variance_of_vertical_velocity_and_variance_of_eastward_wind_at_interfaces` [m4 s-4]
- `pbuf_WP2VP2` -> `fourth_order_moment_of_variance_of_vertical_velocity_and_variance_of_northward_wind_at_interfaces` [m4 s-4]
- `pbuf_WPUP2` -> `third_order_moment_of_vertical_velocity_and_variance_of_eastward_wind` [m3 s-3]
- `pbuf_WPVP2` -> `third_order_moment_of_vertical_velocity_and_variance_of_northward_wind` [m3 s-3]
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
- `dse_top` -> `dry_static_energy_at_top_of_atmosphere?` [J kg-1]
- `u (provisional after vdiff)` -> `eastward_wind_after_vertical_diffusion` [m s-1]
- `v (provisional after vdiff)` -> `northward_wind_after_vertical_diffusion` [m s-1]
- `dse (provisional after vdiff)` -> `dry_static_energy_after_vertical_diffusion` [J kg-1]
- `usteer` -> `eastward_wind_at_steering_level_due_to_moving_mountain_gravity_wave_drag?` [m s-1]
- `vsteer` -> `northward_wind_at_steering_level_due_to_moving_mountain_gravity_wave_drag?` [m s-1]
- `t_day` -> `air_temperature_for_daytime_points_for_RRTMGP` [?]
- `icwuu` -> `in_cloud_eastward_wind_in_updraft_due_to_deep_convection` [m s-1]
- `icwuv` -> `in_cloud_northward_wind_in_updraft_due_to_deep_convection` [m s-1]
- `icwdu` -> `in_cloud_eastward_wind_in_downdraft_due_to_deep_convection` [m s-1]
- `icwdv` -> `in_cloud_northward_wind_in_downdraft_due_to_deep_convection` [m s-1]

## Physical constants

- `pbuf_REI` -> `effective_radius_of_stratiform_cloud_ice_particle` [micron]
- `pbuf_REL` -> `effective_radius_of_stratiform_cloud_liquid_water_particle` [micron]
- `rairv` -> `composition_dependent_gas_constant_of_dry_air` [J kg-1 K-1]
- `isrootproc` -> `flag_for_mpi_root` [flag]
- `cmflq` -> `latent_heat_of_vaporization_times_sum_of_water_vapor_and_cloud_liquid_flux_due_to_shallow_convection` [W m-2]
- `rairi` -> `gas_constant_of_dry_air_at_interfaces_for_vertical_diffusion` [J K-1 kg-1]
- `latice` -> `latent_heat_of_fusion_of_water_at_0c` [J kg-1]
- `latvap` -> `latent_heat_of_vaporization_of_water_at_0c` [J kg-1]
- `pi` -> `pi_constant` [1]
- `gravit` -> `standard_gravitational_acceleration` [m s-2]
- `rearth` -> `radius_of_earth` [m]
- `rga` -> `reciprocal_of_gravitational_acceleration` [s2 m-1]
- `rearth_recip` -> `reciprocal_of_radius_of_earth` [m-1]
- `rair` -> `gas_constant_of_dry_air` [J kg-1 K-1]
- `cpvir` -> `ratio_of_specific_heat_of_water_vapor_to_specific_heat_of_dry_air` [1]
- `Cpd_on_Cpv` -> `ratio_of_specific_heat_of_dry_air_to_specific_heat_of_water_vapor` [1]

## Tendencies

- `pbuf_BERGSO` -> `mixing_ratio_wrt_to_moist_air_and_condensed_water_tendency_of_cloud_liquid_water_to_snow_due_to_vapor_deposition` [?]
- `pbuf_CC_T` -> `tendency_of_air_temperature_due_to_microphysics` [?]
- `pbuf_CC_ni` -> `tendency_of_cloud_ice_number_concentration_due_to_microphysics` [?]
- `pbuf_CC_nl` -> `tendency_of_cloud_liquid_water_number_concentration_due_to_microphysics` [?]
- `pbuf_CC_qi` -> `tendency_of_cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_microphysics` [?]
- `pbuf_CC_ql` -> `tendency_of_cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_microphysics` [?]
- `pbuf_CC_qlst` -> `tendency_of_incloud_cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_microphysics` [?]
- `pbuf_CC_qv` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_microphysics` [?]
- `pbuf_DQCORE` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_dynamics` [kg kg-1 s-1]
- `pbuf_DTCORE` -> `tendency_of_air_temperature_due_to_dynamics` [K s-1]
- `pbuf_DUCORE` -> `tendency_of_eastward_wind_due_to_dynamics` [m s-2]
- `pbuf_DVCORE` -> `tendency_of_northward_wind_due_to_dynamics` [m s-2]
- `pbuf_FRZCNT` -> `tendency_of_cloud_ice_number_concentration_due_to_contact_freezing` [cm-3]
- `pbuf_FRZDEP` -> `tendency_of_cloud_ice_number_concentration_due_to_deposition_nucleation` [cm-3]
- `pbuf_FRZIMM` -> `tendency_of_cloud_liquid_droplet_number_concentration_due_to_immersion_freezing` [cm-3]
- `pbuf_RLIQBC` -> `vertically_integrated_cloud_liquid_tendency_due_to_all_convection_before_surface_coupling_to_be_applied_later_in_time_loo` [kg m-2 s-1]
- `pbuf_TTEND_CLUBB` -> `tendency_of_air_temperature_due_to_clubb` [K s-1]
- `pbuf_TTEND_DP` -> `tendency_of_air_temperature_due_to_deep_convection` [K s-1]
- `tend_dtdt` -> `tendency_of_air_temperature_due_to_model_physics` [K s-1]
- `tend_dudt` -> `tendency_of_eastward_wind_due_to_model_physics` [?]
- `tend_dvdt` -> `tendency_of_northward_wind_due_to_model_physics` [?]
- `ptend_u` -> `tendency_of_eastward_wind` [m s-2]
- `ptend_v` -> `tendency_of_northward_wind` [m s-2]
- `tphysac_rliq` -> `vertically_integrated_cloud_liquid_water_tendency_due_to_all_convection_to_be_applied_later_in_time_loop` [m s-1]
- `tphysac_rliq2` -> `vertically_integrated_cloud_liquid_water_tendency_due_to_shallow_convection_to_be_applied_later_in_time_loop` [m s-1]
- `tphysbc_rice` -> `vertically_integrated_lwe_cloud_ice_tendency_due_to_all_convection_to_be_applied_later_in_time_loop` [kg m-2 s-1]
- `qtend` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water_not_due_to_microphysics` [kg kg-1 s-1]
- `ttend` -> `tendency_of_air_temperature_not_due_to_microphysics` [K s-1]
- `ice2pr` -> `tendency_of_cloud_ice_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_ice_to_snow_autoconversion` [kg kg-1 s-1]
- `liq2pr` -> `tendency_of_cloud_liquid_water_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_liquid_to_rain_autoconversion` [kg kg-1 s-1]
- `liq2snow` -> `tendency_of_cloud_liquid_water_mixing_ratio_wrt_to_moist_air_and_condensed_water_due_to_liquid_to_snow_autoconversion` [kg kg-1 s-1]
- `utgw` -> `tendency_of_eastward_wind_due_to_{type}_gravity_wave_drag` [m s-2]
- `vtgw` -> `tendency_of_northward_wind_due_to_{type}_gravity_wave_drag` [m s-2]
- `ttgw` -> `tendency_of_air_temperature_due_to_{type}_gravity_wave_drag` [K s-1]
- `dttdf` -> `tendency_of_air_temperature_due_to_diffusion_due_to_{type}_gravity_wave_drag` [J kg-1 s-1]
- `dttke` -> `tendency_of_air_temperature_due_to_kinetic_energy_dissipation_due_to_{type}_gravity_wave_drag` [J kg-1 s-1]
- `No CAM equivalent` -> `do_output_of_tendency_of_air_temperature_due_to_shortwave_heating_on_radiation_timestep_assuming_clear_sky` [?]
- `ptend%q(:,:,1)` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]
- `cme` -> `tendency_of_water_vapor_mixing_ratio_wrt_moist_air and_condensed_water_from_cloud_condensation_minus_precipitation_evaporation_due_to_deep_convection` [kg kg-1 s-1]

## Cloud & convection

- `cnst_CLDICE` -> `cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `cnst_CLDLIQ` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `cnst_NUMLIQ` -> `mass_number_concentration_of_cloud_liquid_wrt_moist_air_and_condensed_water` [kg-1]
- `pbuf_AIST` -> `stratiform_cloud_ice_area_fraction` [fraction]
- `pbuf_ALST` -> `stratiform_cloud_liquid_area_fraction` [fraction]
- `pbuf_CLDICEINI` -> `cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water_before_physics` [kg kg-1]
- `pbuf_CLDLIQINI` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_before_physics` [kg kg-1]
- `pbuf_DEI` -> `effective_diameter_of_stratiform_cloud_ice_particle_for_radiation` [micron]
- `pbuf_DIFZM` -> `detrainment_of_cloud_ice_wrt_moist_air_and_condensed_water_due_to_deep_convection` [kg kg-1 s-1]
- `pbuf_DLFZM` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_deep_convection` [kg kg-1 s-1]
- `pbuf_ICIWPST` -> `stratiform_in_cloud_ice_water_path_for_radiation` [kg m-2]
- `pbuf_ICLWPST` -> `stratiform_in_cloud_liquid_water_path_for_radiation` [kg m-2]
- `pbuf_QIST` -> `stratiform_cloud_ice_water_content` [kg kg-1]
- `pbuf_QLST` -> `stratiform_cloud_liquid_water_content` [kg kg-1]
- `pbuf_RTM` -> `sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air` [kg kg-1]
- `pbuf_RTP2_nadv` -> `advected_variance_of_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air_at_interfaces` [kg2 kg-2]
- `pbuf_RTP3` -> `third_moment_of_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air` [kg3 kg-3]
- `pbuf_SADICE` -> `cloud_ice_surface_area_density_for_microphysics` [cm2 cm-3]
- `pbuf_SH_CLDICE1` -> `cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_shallow_convection` [kg kg-1]
- `pbuf_SH_CLDLIQ1` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_due_to_shallow_convection` [kg kg-1]
- `pbuf_SNOW_SED` -> `stratiform_lwe_cloud_ice_surface_flux_due_to_sedimentation` [m s-1]
- `pbuf_SNOW_STR` -> `lwe_snow_and_cloud_ice_precipitation_rate_at_surface_due_to_microphysics` [m s-1]
- `pbuf_WP2RTP` -> `third_order_moment_of_variance_of_vertical_velocity_and_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air` [m2 s-2 kg kg-1]
- `pbuf_WPRTP_nadv` -> `advected_covariance_of_vertical_velocity_and_sum_of_water_vapor_and_cloud_liquid_mixing_ratio_wrt_dry_air_at_interfaces` [m s-1 kg kg-1]
- `tphysac_dlf` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_all_convection` [kg kg-1 s-1]
- `tphysac_dlf2` -> `detrainment_of_cloud_liquid_water_wrt_moist_air_and_condensed_water_due_to_shallow_convection` [kg kg-1 s-1]
- `pracwo` -> `accretion_of_cloud_liquid_water_by_rain` [kg kg-1 s-1]
- `psacwo` -> `accretion_of_cloud_liquid_water_by_snow` [kg kg-1 s-1]
- `psacio` -> `accretion_of_cloud_ice_by_snow` [kg kg-1 s-1]
- `cmeice` -> `rate_of_condensation_minus_evaporation_for_cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]
- `cmeliq` -> `rate_of_condensation_minus_evaporation_for_cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1 s-1]
- `icimr` -> `in_cloud_cloud_ice_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `icwmr` -> `in_cloud_cloud_liquid_mixing_ratio_wrt_moist_air_and_condensed_water` [kg kg-1]
- `fwaut` -> `relative_importance_of_cloud_liquid_water_autoconversion` [fraction]
- `fsaut` -> `relative_importance_of_cloud_ice_autoconversion` [fraction]
- `fracw` -> `relative_importance_of_rain_accreting_cloud_liquid_water` [fraction]
- `fsacw` -> `relative_importance_of_snow_accreting_cloud_liquid_water` [fraction]
- `fsaci` -> `relative_importance_of_snow_accreting_cloud_ice` [fraction]
- `qlfd` -> `cloud_liquid_water_mixing_ratio_wrt_moist_air_and_condensed_water_for_eddy_diffusion` [kg kg-1]
- `cld` -> `total_cloud_fraction (or cloud_area_fraction)` [?]
- `pbuf%ICLWP` -> `in_cloud_liquid_water_path_for_radiation` [?]
- `pbuf%ICIWP` -> `cloud_ice_water_path` [?]

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
- `do_diffusion_const` -> `flag_for_ccpp_constituent_vertical_diffusion?` [flag]
- `q (provisional after vdiff)` -> `ccpp_constituents_after_vertical_diffusion` [kg kg-1]
- `ubc_mmr` -> `upper_boundary_condition_of_ccpp_constituents` [none]
- `cnst_fixed_ubc` -> `use_fixed_upper_boundary_condition_of_ccpp_constituents?` [flag]
- `qtgw` -> `ccpp_constituent_tendencies_due_to_{type}_gravity_wave_drag` [kg kg-1 s-1]
- `dqdt` -> `ccpp_constituent_tendencies` [none]
- `delt` -> `half_timestep_for_physics` [s]

## Other commonly used

- `omega` -> `angular_velocity_of_earth_rotation` [rad s-1]
- `ncol` -> `number_of_columns_per_RRTMGP_SW_block` [?]

## Constructing New Standard Names

If a standard name is not in the spreadsheet, construct one following ESM rules:

```
[transformation] [component] base_name [in/of medium] [at level] [due_to process] [assuming condition]
```

Key rules:
- Fortran logicals: `flag_for_X`; other control variables: `control_for_X`
- Mixing ratios: specify `wrt_dry_air`, `wrt_moist_air`, or `wrt_moist_air_and_condensed_water`
- Tunable parameters: `tunable_parameter[s]_for_X`
- Append `_TBD` to names not yet discussed/approved
- Use chemical formulae for species (e.g., `co2`, `o3`), except `water`, `ozone`

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