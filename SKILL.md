---
name: ccpp-kit
description: >
  End-to-end conversion of CAM physics parameterizations into CCPP-compliant schemes for
  CAM-SIMA, from the first read of the CAM source to a bit-for-bit snapshot test and the PRs.
  Use whenever the user mentions CCPP, CCPPization, CAM-SIMA, porting or converting a physics
  scheme, atmospheric_physics, metadata (.meta) files, suite definition files (SDF), standard
  names, namelist XML, interstitials, snapshots, registry variables, physpkg, pbuf, state%q,
  ptend, outfld/addfld, dropsonde, FPHYStest, or answer differences between CAM and CAM-SIMA.
  Trigger even for a sub-step ("write the metadata for this", "why does ncdata_check differ").
---

# CCPP conversion kit

You are helping convert a CAM physics parameterization into a CCPP scheme that runs
bit-for-bit (b4b) in CAM-SIMA. The process, not the conventions, is what this kit teaches:
repository conventions live in `AGENTS.md` in CAM and atmospheric_physics; read those when you
work in a repo and do not restate them here. CAM-SIMA's `AGENTS.md` and `PORTING.md` are
pending on its `hplin/agents_md` branch; until they merge, the CAM-SIMA documentation
(escomp.github.io/CAM-SIMA-docs) is the reference for host-side conventions.

## Before anything else

1. Look for `kit.local.md` in the sandbox root (the directory holding `CAM/` and `CAM-SIMA/`).
   If it is missing, run the setup interview in `guides/00-setup.md` and write it. It records
   the Derecho project code, checkout paths, scratch root, compiler, and the user's autonomy
   level. Never guess these.
2. Read `references/conventions.md` (style, metadata, namelist XML, registry, SDF patterns),
   `references/standard_names_quick_ref.md`, and `references/framework_gotchas.md`.
3. Read the guide for the phase you are in (below). Guides are self-contained; each ends with
   an exit check that must pass before moving on.

## The pipeline

| Phase | Guide | Exit check |
|---|---|---|
| 1. Work inside CAM: splice the module into a portable layer and a CAM interface, build, prove b4b | `guides/10-cam-phase.md` | CAM run with the split code is b4b against the unsplit run (ladder rung 2 or better) |
| 2. Generate CAM snapshots around the scheme | `guides/20-snapshots.md` | before/after files exist, cover the `STOP_N` frames (6 by default), and contain every input the scheme reads |
| 3. Move to atmospheric_physics and CAM-SIMA: metadata, namelist XML, host variables, SDF, FPHYStest case | `guides/30-cam-sima-phase.md` | capgen resolves the suite; the case builds |
| 4. Run on Derecho and read the check | `guides/40-derecho-loop.md` | `ncdata_check` reports no differences above threshold every step |
| 5. When answers differ: dropsonde | `guides/50-dropsonde.md` | first divergence found, classified (wiring, harness, port), fixed; back to phase 4 |
| 6. Wrap up: diagnostics scheme, regression test, snapshots to the shared baseline, PRs | `guides/60-wrapup.md` | three PRs open in order; CAM-SIMA test added |

Phase 1 comes first on purpose. Code moves to atmospheric_physics only after it is provably
CCPP-shaped and b4b inside CAM, under CAM's own tests. Any later CAM-SIMA divergence is then
wiring or harness, never science, and there is no separate "bring it back to CAM" step.
The baseline CAM case that phase 2 snapshots from is created at the start of phase 1 with the
unsplit code (recipe in `guides/20-snapshots.md`), because that one run is both the b4b
reference for the ladder and the snapshot source; phase 2 is then the `user_nl_cam` settings
and the verification of the tapes.

## Non-negotiables

- **Bit-for-bit is the acceptance gate.** Never reorder floating-point arithmetic, change
  parenthesization, or "simplify" expressions while porting. If CAM stores a difference, store
  the difference; match the operation order, not just the math.
- **Splice, do not rewrite.** Every line of the original module goes to exactly one side of the
  split. Copy from `git show <base>:<path>`, never retype from memory. Prove it with `fbody`.
- **Portability.** Schemes take host quantities as arguments by standard name. No `physconst`,
  `ppgrid`, `cam_history`, `time_manager`, `pbuf`, `state`, `ptend`, `r8`, or constituent index
  assumptions inside a scheme. Unavoidable host dependencies go to `to_be_ccppized` and are
  flagged to the user.
- **Standard names: draft freely, the user reviews.** Look in the registry and recent schemes
  first; otherwise construct a name by the rules and tag it `_TBD`. Keep a running list.
- **Nothing shared is written before the PR.** Snapshots stay in the CAM case run directory and
  `ncdata`/`ncdata_check` point there. Copy to the shared baseline directory only in phase 6.
- **Respect the autonomy level** in `kit.local.md`. Level 0: you prepare every cluster command
  and the user runs it and pastes the output. Level 1: you run builds and submissions after
  stating what you are about to do and getting a yes. Level 2: you run everything, including
  dropsonde under `qcmd`, and report. Reading logs and files is always allowed.
- **Disclose AI assistance** in commit messages and PR descriptions, per the CAM `AGENTS.md`.
  The human submitter must be able to defend every line.

## Working style

- Ask before deciding design questions (new host variable or scheme-side computation, where a
  dependency lives, interstitial boundaries). Collect questions and present them together.
- Present two to four options with trade-offs for anything structural. Let the user narrow.
- Prefer small, inspectable steps with a check after each (a syntax-only compile, fbody,
  suite-trace, a build).
- When something diverges, decompose before editing: wiring, harness, port. The port itself is
  historically the least likely culprit under this workflow, but prove it.
- Thread diagnostics early. Intermediate quantities that feed `outfld` become arguments during
  the splice so the portable interface never churns later, and the same arguments feed the
  `_diagnostics` scheme and dropsonde triage.
- Commit on top, never amend and force-push once a branch is on the fork or checked out on
  the cluster. atmospheric_physics and CAM-SIMA squash-merge, so branch history does not
  matter and a rewritten branch breaks the other checkout's `git pull`.

## Two regimes

The guides assume a *physpkg scheme*: called from `tphysbc` or `tphysac` with `state`,
`ptend`, `pbuf`. *Chemistry-embedded schemes* (called inside `gas_phase_chemdr`,
`aero_model`, `mo_setext`) work on chemistry-local arrays with their own index spaces and
have no `ptend`. They need the interior-capture snapshot method (`guides/20-snapshots.md`,
method D) and a vmr-style working-array design. Identify the regime in phase 1 before planning.

## Reference material

- `references/conventions.md`: style, `.meta` format, dimensions table, namelist XML, registry
  entries, SDF layout, the diagnostics module template, recurring scheme shapes, utility schemes.
- `references/standard_names_quick_ref.md`: common CAM name to standard name mappings.
- `references/framework_gotchas.md`: init timing and visibility rules, b4b numerics discipline.
- `references/waccm-triage.md`: the WACCM and WACCM-X scheme sheet keyed to the configuration
  that reaches each item at ne3pg3.
- `agents/cam-sima-reviewer.md`: the review agent for phase 1 rung 0 (install per `README.md`);
  `tools/`: the CCPP linter it runs and the quick-reference checker.
- `examples/`: worked conversions, starting with `iondrag_calc_ghg`.
- `templates/`: `kit.local.md`, snapshot `user_nl_cam`, CAM-SIMA testmod.
