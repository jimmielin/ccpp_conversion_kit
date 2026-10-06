# Framework Gotchas and b4b Numerics Discipline

Two classes of knowledge that cost the most debugging time, distilled from the
MAM port (2026). Facts here can drift with framework versions - when in doubt,
verify against the code paths cited.

## Init timing and visibility rules

1. **Registry constituents DECLARE, schemes REGISTER (empirically confirmed
   2026-07-05, setsox CO2 incident).** A `registry.xml` entry with
   `constituent="true"` only declares the standard name -> ic_file_input_names
   mapping; it does NOT register a constituent. A constituent exists at run
   time only if some scheme registers it: a register-phase scheme
   (mam_constituents / sulfur_chemistry_stub / initialize_constituents), or
   the consuming scheme's own metadata with `advected = true` on the argument
   (a capgen constituent request). A plain run-phase argument by standard
   name does NOT bind to an unregistered registry declaration -- capgen
   silently auto-creates a NEW constituent keyed to the scheme argument,
   whose ic name falls back to the LOCAL variable name (atm.log signature:
   `co2 not found, also looked for: [co2mmr, ,]`), so it reads nothing and
   the scheme gets zeros. `ccpp_constituent_index` at `_init` sees only
   registered constituents (registry declarations are invisible to it for
   the same reason). RESOLVED (2026-07-05, generated-code
   inspection): the registry ic mapping DOES apply to a meta-registered
   constituent, but only after CAM-SIMA's case-sensitivity fix (CAM-SIMA
   commit "To cherry-pick: case-insensitive standard-name matching") -
   capgen lowercases scheme-side standard names ('CO2' -> 'co2') while
   registry declarations keep authored case, and both write_init_files.py's
   registry-constituent membership test and physics_data's runtime name
   compares were case-sensitive, generating AND matching a phantom
   phys-var row ('co2' -> [<local_name>]) next to the real one
   ('CO2' -> [CO2, cnst_CO2, ...]). Register-phase `instantiate` preserves
   case, which is why rrtmgp_constituents never hit this.

2. **Aerosol instances (props AND states) are now created BEFORE phys_init**
   (CAM-SIMA `cam_comp.F90:283-285`: `rad_aer_init_all` - `rad_aer_init` ->
   `aerosol_instances_init` -> `aerosol_instances_init_states` - runs before
   `phys_init`; reordered by hplin 2026-04-20 for the microp_aero BAM unit).
   Consequences (UPDATED 2026-07-15; the old "deferred first-run init"
   guidance is obsolete for new schemes):
   - `aero_props` objects CAN be resolved and index maps built at CCPP
     `_init`. Precedents: `nucleate_ice_ccpp`, `droplet_activation_ccpp`,
     `contact_freezing_modal`.
   - `aero_state` is still resolved per RUN call
     (`aerosol_instances_get_state`) since it wraps evolving host data.
   - Older wrappers (`modal_aero_wateruptake_ccpp`, `modal_aero_setsox_ccpp`)
     predate the reorder and carry a first-run-guard deferred init; it still
     works, but do not copy that shape into new schemes.
   - Phase-1 `radiative_aerosol` info (mode metadata via `rad_aer_get_info*`)
     is likewise available at scheme init.

3. **Constituent-dimensioned ic reads resolve ONE base name for all
   constituents** (`physics_data.F90`,
   `read_constituent_dimensioned_field_3d`): the reader picks the first base
   name from `ic_file_input_names` that matches ANY constituent on the file,
   then uses that single base for every constituent
   (`<base>_<constituent_diag_name>`). There is NO per-constituent fallback
   across the name list. If a snapshot-injected variable must cover species
   captured under a different name, the capture must also write them under
   the variable's own base name.

4. **FPHYStest re-reads ic inputs each timestep at frame = get_nstep()**.
   Empirically verified end-to-end; never apply a +1 frame "fix". `ncdata`
   provides inputs (re-read per step), `ncdata_check` provides per-step
   comparison targets - different roles, often the same file.

5. **Namelist auto-wiring**: an `<entry>` in `<scheme>_namelist.xml` with a
   `standard_name` becomes an `_init`-phase argument with that standard name.
   File-path options: `char*256`, `input_pathname="abs"`,
   `${DIN_LOC_ROOT}/...` default value.

6. **Scheme-level file reads** use `ccpp_io_reader`
   (`abstract_netcdf_reader_t`, `create_netcdf_reader_t`) at `_init`:
   `open_file` / generic `get_var` (int/real/char, 0d-5d, allocatable
   outputs; char arrays supported) / `close_file`. Do NOT list
   `ccpp_io_reader` in metadata `dependencies` (host-provided).

7. **Module-level saved state in schemes** is per-instance-safe under CAM
   multi-instance (disjoint rank sets), and the first-run-guard init pattern
   is accepted where framework phases cannot host a dependency.

8. **XML comments must not contain `--`** (suite/namelist XML files fail to
   parse). Use single dashes or commas in prose.

## b4b numerics discipline

Bit-for-bit is identity of floating-point EXPRESSIONS on identical inputs,
not "the same physics". When the goal is b4b against CAM:

1. **Round trips are never free.** mmr<->vmr, g/mol->kg/mol->g/mol, any
   write-converted/read-converted snapshot field - each is a ~1 ulp seed on
   a value-dependent fraction of cells. Register constituent molar masses
   through `chem_molar_mass_kgmol` (to_be_ccppized/ccpp_chem_utils), which
   nudges the kg/mol value so consumers' `*1.0e3` reproduces the g/mol
   `adv_mass` bitwise (naive `*1.e-3` is 1 ulp off for e.g. so4 115.107340,
   dust 135.064039, H2SO4 98.0784). For validation, prefer injecting raw
   values in the units the scheme consumes (skip the round trip entirely).

2. **Reproduce stores, not formulas.** If CAM stores a before/after
   difference, store the difference - `tendency*dt` is a different float.
   If CAM applies `fl((x+d*dt)*a)`, then `fl(x*a)+fl(dt*fl(d*a))` differs by
   construction. Match the operation ORDER, not just the math.

3. **Host constants as arguments.** Take rair, mwdry, gravit, pi,
   r_universal, boltz, avogad as `_init`/`_run` args from the host
   (standard names live in CAM-SIMA `physconst.meta`); never hardcode
   SHR_CONST values in portable code - physconst can be runtime-overridden.
   If CAM derives a constant (`rgas*1.e-3`), perform the SAME operation on
   the SAME host value in the wrapper rather than importing a different
   literal.

4. **Real exponents where CAM has real exponents**
   (`dgnum**3._kind_phys`, not `dgnum**3`) - integer vs real exponentiation
   has been a real divergence root cause.

5. **`intent(out)` vs `intent(inout)`**: an `intent(out)` array the scheme
   only partially fills leaves garbage in the rest (CAM baselines may have
   relied on previously-initialized memory). If CAM partially fills, either
   fully initialize first or use `intent(inout)` deliberately - and document
   which.

6. **When a run diverges, decompose before editing**: (a) wiring - a
   standard name resolved to the wrong host variable (grep the generated
   cap code / registry); (b) harness - capture code, ic/check frame or
   naming, unit conversion on write; (c) the port itself. Under the
   "verify-b4b-inside-CAM-first" workflow, (c) has historically been the
   LEAST likely - but prove it with first-divergence bisection rather than
   assuming.

7. **Design validation gates in pairs from one capture**: a state gate
   (working array vs post-process capture) and a derived gate (computed
   tendency/diagnostic vs its capture). Each catches errors the other can
   mask. Extend one capture bracket to feed all suites; avoid multiplying
   capture runs.

## Signal discipline (design-level)

Never encode a workflow property in a physical property. Case study: cluster
membership was once inferred from "has a registered molar mass" - which broke
the moment prescribed oxidants needed to be species WITH a molecular weight
but WITHOUT mmr<->vmr conversion, and the tempting fix was to withhold the true
molar mass. If you find yourself lying to a mechanism to get behavior, the
mechanism keys on the wrong signal: make the property explicit (an
init-resolved, logged membership table - `chem_vmr_metadata`), assert the
physical property where genuinely required (hard error on omission, never
silent exclusion), and let physical properties stay true everywhere.
