# conversion_kit

A Claude Code skill plus guides for converting CAM physics parameterizations into
CCPP-compliant schemes for CAM-SIMA, end to end: splice inside CAM, prove bit-for-bit,
snapshot, move to atmospheric_physics, run the CAM-SIMA snapshot test, localize answer
differences with dropsonde, open the PRs.

It complements, and does not replace, the repository guidance in `AGENTS.md` (CAM, CAM-SIMA,
atmospheric_physics) and `PORTING.md` (CAM-SIMA). Those own conventions; this kit owns process.

## Install

The repository root is the skill. Clone it and symlink it into your Claude Code skills
directory under the name `ccpp-kit`:

```
git clone <url> ~/conversion_kit
mkdir -p ~/.claude/skills
ln -s ~/conversion_kit ~/.claude/skills/ccpp-kit
```

Start Claude Code anywhere inside your sandbox (the directory that holds `CAM/` and
`CAM-SIMA/`) and say what you want to convert. The skill triggers on CCPP vocabulary. On first
use it interviews you and writes `kit.local.md` in the sandbox root; see `guides/00-setup.md`.

## Layout

```
SKILL.md                 the skill: pipeline, non-negotiables, pointers
guides/
  00-setup.md            sandbox layout, setup interview, autonomy levels, tools on Derecho
  10-cam-phase.md        splice, portable layer, CAM interface, the bit-for-bit ladder
  20-snapshots.md        which snapshot method, how to generate, what to verify in the files
  30-cam-sima-phase.md   atmospheric_physics move, metadata, namelist XML, host variables, SDF, FPHYStest case
  40-derecho-loop.md     case, build, submit, logs, reading ncdata_check, Derecho gotchas
  50-dropsonde.md        pairing the two models, running under qcmd, reading the report, pathology catalogue
  60-wrapup.md           diagnostics scheme, regression test, shared snapshots, PRs
references/
  conventions.md         style, .meta, namelist XML, registry, SDF, diagnostics template, scheme shapes
  standard_names_quick_ref.md
  framework_gotchas.md   init timing rules and b4b numerics discipline
  waccm-triage.md        WACCM / WACCM-X scheme sheet keyed to the configuration that reaches each item
examples/
  iondrag_calc_ghg/      the demo conversion: plan, Derecho prep commands, notes
templates/
  kit.local.example.md
  user_nl_cam.snapshot
  testmod_fphystest/     shell_commands + user_nl_cam for a CAM-SIMA snapshot test
```

## Conventions for this repository

- Plain ASCII prose; no em dashes (some ESCOMP tooling chokes on them).
- Guides are self-contained and end with an exit check.
- Promote a one-off recipe into a guide only after it has been needed twice.
