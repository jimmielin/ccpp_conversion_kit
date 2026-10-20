# 60. Phase 6: diagnostics, test, shared snapshots, PRs

## 6.1 Diagnostics scheme

All `addfld`/`outfld` of the original module become `sima_diagnostics/<scheme>_diagnostics.F90`
with its `.meta` (template in `references/conventions.md`): `_init` registers fields with
`history_add_field`, `_run` writes them with `history_out_field`, every input `intent(in)`.
Place it right after the scheme in the SDF. Field names stay identical to CAM's so the two
models' history can be compared directly.

Check it the same way the state is checked: in the CAM snapshot case, add the fields to an
instantaneous tape (`fincl` on a tape with `nhtfrq = 1`, `ndens = 1`); in the CAM-SIMA case,
`hist_add_inst_fields;h1: <fields>`, `hist_output_frequency;h1: 1*nsteps`,
`hist_precision;h1: REAL64`; then `cprnc` the two files for the shared fields. Writing the
diagnostics scheme early also helps dropsonde triage, since intermediates become visible.

## 6.2 Regression test in CAM-SIMA

- `cime_config/testdefs/testmods_dirs/cam/outfrq_<scheme>_derecho/` with `shell_commands`
  and `user_nl_cam` from `templates/testmod_fphystest/`. `ncdata_check_err = .true.`,
  `min_difference = 2e-15`, and any `ncdata_check_exclude` rows with a comment explaining each.
- Add the test to `cime_config/testdefs/testlist_cam.xml`: `FPHYStest`, `ne3pg3_ne3pg3_mg37`,
  `SMS_Ln2`, machine derecho, compiler gnu, category `aux_sima`, a ten-minute wallclock, and a
  comment naming the scheme. Copy a neighbouring entry.
- The suite file may move from `test/test_suites/` into the production suite the scheme
  belongs to; ask the user.

## 6.3 Snapshots to the shared baseline

This is the only write to a shared location in the whole workflow, and it happens right
before the PR opens, never earlier.

- Destination on Derecho:
  `/glade/campaign/cesm/community/amwg/sima_baselines/cam_sima_test_snapshots/`
- Names: `cam<tag>_<res>_<compset>_<parameterization>_snapshot_derecho_<compiler>_before_cYYYYMMDD.nc`
  and the same with `after`, for example
  `cam6_4_201_ne3pg3_fwsc_iondrag_ghg_snapshot_derecho_gnu_before_c20261020.nc`. The CAM tag
  is the one the snapshot case was built from (older files in the directory omit it:
  `cam_ne3pg3_fhist_beljaars_...`; use the tagged form).
- `chmod 644` both files. Then switch the testmod's `ncdata` and `ncdata_check` from the run
  directory to these paths and rerun the test once.
- Izumi copies go under `/project/amp02/cam_snapshot_files/<parameterization>/`.

## 6.4 Pull requests

Order: atmospheric_physics first (it must be tagged before either model can pin it), then CAM
and CAM-SIMA together, each bumping the atmospheric_physics pin to the new tag. Do not let
much time pass between the atmospheric_physics merge and the CAM-SIMA merge; standard names
drift.

- atmospheric_physics PR: the scheme, metadata, namelist XML, suite, diagnostics. Follow its
  `AGENTS.md` for the PR template and style checks.
- CAM PR: the `_cam` interface, the `bld/configure` Filepath entry, the snapshot bracket if
  method B was used, the pin bump. State the answer impact explicitly: bit-for-bit, with the
  `aux_cam` evidence (rung 3). Disclose AI assistance as the CAM `AGENTS.md` requires.
- CAM-SIMA PR: registry or host changes, testmod, testlist entry, pin bump. If the registry
  changed, regenerate and commit the `write_init_files` reference samples under
  `test/unit/python/sample_files/` that `test/unit/python/test_write_init_files.py` compares
  against (CAM-SIMA's `AGENTS.md`, pending on `hplin/agents_md`, describes the workflow).

The user pushes the branches and opens the PRs. You draft each PR description and the
commit messages, list the files each PR carries, and hand over the exact `git push` commands
for the user's forks. Push yourself only if `kit.local.md` says `github_write: yes`, and then
to the user's fork only; the ESCOMP remotes are never a push target. Remove `user_set`
brackets and any hardcoded capture switches before the CAM PR unless they were promoted to a
named point.

## Exit check

Three PRs drafted, then pushed and opened by the user in order with the pin bumps; the
CAM-SIMA test passes against the shared snapshots; the proposed standard names were reviewed
by the user and any `_TBD` resolved.
