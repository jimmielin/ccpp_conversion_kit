# CCPP Conversion Conventions Reference

## Coding Style

Follow these conventions exactly when generating Fortran code:

### Declarations
- Pretty-align whitespace in argument declarations:
```fortran
    integer,            intent(in)  :: ncol
    integer,            intent(in)  :: pver
    real(kind_phys),    intent(in)  :: zm(:, :)       ! geopotential height wrt surface [m] (layer centers)
    real(kind_phys),    intent(out) :: concld(:, :)   ! convective cloud cover [fraction]
    character(len=*),   intent(out) :: errmsg
    integer,            intent(out) :: errflg
```

- Align `intent(in)`, `intent(out)`, `intent(inout)` columns
- Annotate physical quantities with units in trailing comments: `! description [units]`
- Explicitly note layer centers vs interfaces when relevant
- Do NOT annotate trivial variables: `ncol`, `pver`, `errmsg`, `errflg`

### Module structure
```fortran
module scheme_name

  use ccpp_kinds, only: kind_phys

  implicit none
  private

  ! public CCPP-compliant subroutines
  public :: scheme_name_init
  public :: scheme_name_run

  ! Module-level variables (tuning parameters, etc.)
  real(kind_phys) :: param1  ! description [units]

contains

!> \section arg_table_scheme_name_init Argument Table
!! \htmlinclude scheme_name_init.html
  subroutine scheme_name_init(...)
    ...
  end subroutine scheme_name_init

!> \section arg_table_scheme_name_run Argument Table
!! \htmlinclude scheme_name_run.html
  subroutine scheme_name_run(...)
    ...
  end subroutine scheme_name_run

end module scheme_name
```

### Naming

Defaults. State them in the design round; change them only when the user says so. Precedents
are `beljaars_drag_cam.F90`, `rk_stratiform_cam.F90`, `dadadj_cam.F90` and
`rayleigh_friction_cam.F90` in CAM, and `schemes/dry_adiabatic_adjust/dadadj.F90` and
`schemes/rasch_kristjansson/rk_stratiform.F90` in atmospheric_physics.

| Item | Default | CAM module `qbo` |
|---|---|---|
| Scheme name | the CAM module name | `qbo` |
| Portable file and module | `schemes/<dir>/<module>.F90`, `module <module>` | `schemes/qbo/qbo.F90`, `module qbo` |
| Scheme directory | the module name; offer a descriptive name (`dry_adiabatic_adjust`, `rasch_kristjansson`) as the alternative when the module name is an abbreviation | `qbo` |
| Phase routines | `<module>_init`, `<module>_timestep_init`, `<module>_run`, `<module>_final` | `qbo_init`, `qbo_timestep_init`, `qbo_run` |
| CAM facade | `<module>_cam.F90`, `module <module>_cam`, in the original module's directory; omitted when it would only forward the call | `src/physics/waccm/qbo_cam.F90` |
| Facade routines | the original names, so call sites change only the `use` line; `<module>_cam_<phase>` when the original name collides with a scheme phase routine | `qbo_readnl`, `qbo_cam_init`, `qbo_cam_timestep_init`, `qbo_relax` |
| Partial split | the moved entry routine's name is the scheme name; the CAM module is edited in place, no facade | `iondrag_calc_ghg` |
| Interstitials | one `_run` per scheme; own file when standalone, `<scheme>_interstitials.F90` for several; a multi-scheme file cannot carry a `_namelist.xml` | `beljaars_drag_interstitials.F90` |
| Namelist XML | `<scheme>_namelist.xml` beside the scheme | `qbo_namelist.xml` |
| Diagnostics | `sima_diagnostics/<scheme>_diagnostics.F90` | `qbo_diagnostics.F90` |

### Error handling
Always add `errmsg, errflg` as the last two arguments. Initialize at routine top:
```fortran
    errmsg = ''
    errflg = 0
```

### Kind
- Always `use ccpp_kinds, only: kind_phys`
- Never `shr_kind_mod` or `r8`
- Literal constants: `1.0_kind_phys`, `0.0_kind_phys`

### Dummy argument dimensions
- Use `:` not named dimensions: `real(kind_phys), intent(in) :: T(:, :)` not `T(ncol, pver)`
- If a named dimension was the only reason for importing it, remove that import

## Metadata Format

### File structure
```
[ccpp-table-properties]
  name = scheme_name
  type = scheme
  dependencies = relative/path/to/dep1.F90,dep2.F90

[ccpp-arg-table]
  name  = scheme_name_init
  type  = scheme
[ var_name ]
  standard_name = standard_name_here
  units = Pa
  type = real | kind = kind_phys
  dimensions = (horizontal_dimension, vertical_layer_dimension)
  intent = in
```

### Key rules
- Do NOT include `long_name`
- `type = real | kind = kind_phys` on one line (pipe-separated)
- Character arguments, `errmsg` included: `type = character | kind = len=*`, matching the
  `len=*` Fortran dummy. The CCPP cap owns the actual string and its length.
- Scalar dimensions: `dimensions = ()`
- Error variables always at the end of each arg table

### Dimension mapping

| CAM dimension      | CCPP phase | Standard name                     |
|:-------------------|:-----------|:----------------------------------|
| pver               | all        | vertical_layer_dimension          |
| pverp (pver+1)     | all        | vertical_interface_dimension      |
| ncol or pcols      | non-run    | horizontal_dimension              |
| ncol or pcols      | run        | horizontal_loop_extent            |
| pcnst              | all        | number_of_ccpp_constituents       |

### Constituent metadata
If a variable traces back to `state%q` in CAM, add `advected = true` to its metadata.
Look the constituent index up by standard name at `_init`, never by position:
```fortran
    use ccpp_scheme_utils, only: ccpp_constituent_index
    call ccpp_constituent_index('water_vapor_mixing_ratio_wrt_moist_air_and_condensed_water', &
                                ixq, errflg, errmsg)
    if (errflg /= 0) return
```
`ccpp_scheme_utils` is framework-provided: no `dependencies` entry. The error code comes
before the message. (`ccpp_const_get_idx` from `ccpp_const_utils` is retired.)

### Dependencies
List relative paths in `dependencies` field of `[ccpp-table-properties]`:
```
  dependencies = scheme_common.F90,../utils/helper.F90
```

## Namelist XML Format

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl"?>
<entry_id_pg version="2.0">

  <entry id="variable_name">
    <type>real</type>
    <kind>kind_phys</kind>
    <category>scheme_category</category>
    <group>scheme_nl_group</group>
    <standard_name>ccpp_standard_name</standard_name>
    <units>units</units>
    <desc>
      Description of the namelist variable.
    </desc>
    <values>
      <value>default_value</value>
    </values>
  </entry>

</entry_id_pg>
```

- `kind` only needed for `real` type (set to `kind_phys`)
- `id` must be lowercase
- For multi-scheme parameterizations, create a dedicated `_options` scheme with only an
  `_init` phase for namelist reading

### File-path namelist option (input dataset)
```xml
  <entry id="scheme_data_file">
    <type>char*256</type>
    <category>scheme_category</category>
    <group>scheme_nl_group</group>
    <standard_name>filename_of_...</standard_name>
    <units>none</units>
    <desc>Full pathname of ...</desc>
    <values>
      <value>${DIN_LOC_ROOT}/atm/.../file.nc</value>
    </values>
  </entry>
```
The matching `_init` argument is `type = character | kind = len=*` in the metadata. A plain
`char*256` entry is the whole pattern (`solar_irradiance_data_namelist.xml`); no
`input_pathname` element.

## SDF Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="scheme_name" version="1.0">
   <group name="physics_before_coupler">
       <!-- pre-processing interstitials -->
       <scheme>wet_to_dry_water_vapor</scheme>
       <!-- core scheme -->
       <scheme>scheme_name</scheme>
       <!-- diagnostics: right after the scheme, before the appliers (suite_cam7 pattern) -->
       <scheme>scheme_name_diagnostics</scheme>
       <!-- post-processing / tendency application -->
       <scheme>dry_to_wet_water_vapor</scheme>
       <scheme>apply_heating_rate</scheme>
       <scheme>apply_tendency_of_eastward_wind</scheme>
   </group>
</suite>
```

| CAM physpkg routine | SDF Group                  |
|:--------------------|:---------------------------|
| tphysbc             | physics_before_coupler     |
| tphysac             | physics_after_coupler      |

## Registry Variable Patterns

### Standard variable (read from initial data file)
```xml
<variable local_name="var_name"
          standard_name="standard_name"
          units="units" type="real" kind="kind_phys"
          allocatable="allocatable">
  <dimensions>horizontal_dimension vertical_layer_dimension</dimensions>
  <ic_file_input_names>possible_name_1 possible_name_2</ic_file_input_names>
</variable>
```
- `ic_file_input_names` lists possible variable names on the snapshot/inputdata file
- `dimensions` is a space-separated list of dimension standard names (in order)

### Scalar not on file (initialized in code)
```xml
<variable local_name="calendar_type"
          standard_name="calendar_type"
          units="none" type="character" kind="len=32">
</variable>
```
Then in Fortran initialization code (host model CAM-SIMA side):
```fortran
use physics_types,        only: calendar_type
use phys_vars_init_check, only: mark_as_initialized

calendar_type = timemgr_get_calendar_cf()
call mark_as_initialized('calendar_type')
```

### Static scalar (protected, not read from file)
```xml
<variable local_name="static_param"
          standard_name="some_static_parameter"
          units="1" type="real" kind="kind_phys"
          access="protected">
</variable>
```
`access="protected"` prevents CAM-SIMA from attempting to read it from a file.

### Constituent declared by the registry
```xml
<variable local_name="CO2"
          standard_name="CO2"
          units="kg kg-1" type="real" constituent="true">
  <ic_file_input_names>CO2 cnst_CO2</ic_file_input_names>
</variable>
```
A registry `constituent="true"` entry DECLARES the standard name and its
ic_file_input_names mapping; it does NOT register the constituent (see
framework_gotchas.md #1). Some scheme must register it -- either a
register-phase scheme or `advected = true` on the consuming scheme's metadata
argument. A plain standard-name argument against an unregistered declaration
silently auto-creates an empty constituent that reads zeros.

### State/tendency variable (also add to relevant ddt)
```xml
<variable local_name="u"
          standard_name="eastward_wind"
          units="m s-1" type="real" kind="kind_phys"
          allocatable="allocatable">
  <dimensions>horizontal_dimension vertical_layer_dimension</dimensions>
  <ic_file_input_names>U</ic_file_input_names>
</variable>
```
If the variable is a state or tendency field, also add its standard name to the relevant
`<ddt>` section in the registry.

## Diagnostics Module Template

```fortran
! Diagnostic scheme for <parameterization>
module <parameterization>_diagnostics
   use ccpp_kinds, only: kind_phys

   implicit none
   private

   public :: <parameterization>_diagnostics_init
   public :: <parameterization>_diagnostics_run

CONTAINS

   !> \section arg_table_<parameterization>_diagnostics_init  Argument Table
   !! \htmlinclude <parameterization>_diagnostics_init.html
   subroutine <parameterization>_diagnostics_init(errmsg, errflg)
      use cam_history,         only: history_add_field
      use cam_history_support, only: horiz_only

      character(len=*),   intent(out) :: errmsg
      integer,            intent(out) :: errflg

      errmsg = ''
      errflg = 0

      ! 3D fields (layer centers)
      call history_add_field('field_3d', 'standard_name_3d', 'lev', 'inst', 'units')
      ! 3D fields (layer interfaces)
      call history_add_field('field_3d_i', 'standard_name_3d_i', 'ilev', 'inst', 'units')
      ! 2D fields (horizontal only)
      call history_add_field('field_2d', 'standard_name_2d', horiz_only, 'inst', 'units')

   end subroutine <parameterization>_diagnostics_init

   !> \section arg_table_<parameterization>_diagnostics_run  Argument Table
   !! \htmlinclude <parameterization>_diagnostics_run.html
   subroutine <parameterization>_diagnostics_run( &
      field_3d, field_3d_i, field_2d, &
      errmsg, errflg)

      use cam_history, only: history_out_field

      real(kind_phys),    intent(in)  :: field_3d(:, :)   ! description [units] (layer centers)
      real(kind_phys),    intent(in)  :: field_3d_i(:, :) ! description [units] (layer interfaces)
      real(kind_phys),    intent(in)  :: field_2d(:)      ! description [units]
      character(len=*),   intent(out) :: errmsg
      integer,            intent(out) :: errflg

      errmsg = ''
      errflg = 0

      call history_out_field('field_3d',   field_3d)
      call history_out_field('field_3d_i', field_3d_i)
      call history_out_field('field_2d',   field_2d)

   end subroutine <parameterization>_diagnostics_run

end module <parameterization>_diagnostics
```

The metadata `[ccpp-table-properties]` block has no `dependencies` line: `cam_history` and
`cam_history_support` are host-provided, and `sima_diagnostics` is the one place a scheme may
`use` them. No module-level `save` (the linter flags it); the repository template is
`schemes/sima_diagnostics/scheme_diagnostics_template.F90` (it still declares `errmsg` as
`len=512`; use `len=*` as above).

## Recurring Scheme Patterns

### Init-resolution module (resolve once, many consumers)
For index maps / lookup tables that several run-phase schemes need: an init-only scheme
resolves everything ONCE and exports it as `public, protected` module state; consumers
`use` it (and list the .F90 in their metadata `dependencies`). The SDF orders the
init-resolution scheme before its consumers. Log the resolved table on the root task -
it is free debugging information. Precedents: `mam_mode_metadata`, `chem_vmr_metadata`
(schemes/chemistry).

### Scheme-init file read (ccpp_io_reader)
```fortran
    use ccpp_io_reader, only: abstract_netcdf_reader_t, create_netcdf_reader_t
    class(abstract_netcdf_reader_t), allocatable :: reader
    real(kind_phys),  allocatable :: table(:,:)
    character(len=:), allocatable :: names(:)

    reader = create_netcdf_reader_t()
    call reader%open_file(file_path, errmsg, errflg)
    if (errflg /= 0) return
    call reader%get_var('var_name', table, errmsg, errflg)   ! generic: int/real/char, 0d-5d
    if (errflg /= 0) return
    call reader%close_file(errmsg, errflg)
```
`file_path` arrives as a namelist option (see the file-path entry pattern above).
Do NOT list `ccpp_io_reader` in metadata `dependencies` (host-provided).
Sanity-check table dimensions after the read and error out with a specific message.

### Deferred first-run init: legacy, do not copy
Older wrappers (`modal_aero_wateruptake_ccpp`, `modal_aero_setsox_ccpp`) resolve aerosol
objects inside `_run` behind a first-call guard because they predate the reorder that runs
`rad_aer_init_all` before `phys_init`. New schemes resolve host objects at `_init`; see
framework_gotchas.md #2.

## Available Utility Schemes

### State converters (state_converters.F90)
- `temp_to_potential_temp` / `potential_temp_to_temp`
- `calc_dry_air_ideal_gas_density`
- `calc_exner`
- `wet_to_dry_water_vapor` / `dry_to_wet_water_vapor`
- `wet_to_dry_cloud_liquid_water` / `dry_to_wet_cloud_liquid_water`
- `wet_to_dry_rain` / `dry_to_wet_rain`

### Other utilities
- `geopotential_temp` - compute geopotential height from temperature
- `update_dry_static_energy` - calculate dry static energy
- `qneg` - clamp negative constituent values (needs `scheme_name` output from prior scheme)

### Tendency updaters (physics_tendency_updaters.F90)
- `apply_tendency_of_eastward_wind`
- `apply_tendency_of_northward_wind`
- `apply_heating_rate`
- `apply_tendency_of_air_temperature`
- `apply_constituent_tendencies`
