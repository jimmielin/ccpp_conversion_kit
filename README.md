# conversion_kit

A Claude Code skill plus guides for converting CAM physics parameterizations into
CCPP-compliant schemes for CAM-SIMA, end to end: splice inside CAM, prove bit-for-bit,
snapshot, move to atmospheric_physics, run the CAM-SIMA snapshot test, localize answer
differences with dropsonde, open the PRs.

It complements, and does not replace, the repository guidance in `AGENTS.md` (CAM and
atmospheric_physics; CAM-SIMA's `AGENTS.md` and `PORTING.md` are pending on its
`hplin/agents_md` branch). Those own conventions; this kit owns process.

## Install

The repository root is the skill. Clone it and symlink it into your Claude Code skills
directory under the name `ccpp-kit`:

```
git clone https://github.com/jimmielin/ccpp_conversion_kit.git ~/conversion_kit
mkdir -p ~/.claude/skills ~/.claude/agents
ln -s ~/conversion_kit ~/.claude/skills/ccpp-kit
ln -s ~/conversion_kit/agents/cam-sima-reviewer.md ~/.claude/agents/cam-sima-reviewer.md
```

The second link installs the review agent that phase 1 uses before the first build.

I also recommend installing `dropsonde` (https://github.com/hplin-ucar/dropsonde) in your scratch directory.

## Getting started

1. Install the conversion kit.
2. Create a sandbox anywhere you would like and check out the latest CAM tag in `CAM/`, and the latest CAM-SIMA in `CAM-SIMA/`.
3. Start Claude Code. Invoke the `/ccpp-kit` skill, and you will be interviewed to start the process.
4. Claude will work with you to get everything converted!

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
agents/
  cam-sima-reviewer.md   Claude Code agent: boundary, metadata and b4b review of a scheme
tools/
  ccpp_lint.py           mechanical style check for atmospheric_physics Fortran and XML
  check_quick_ref.py     validates references/standard_names_quick_ref.md against the code
```

## Conventions for this repository

- Guides are self-contained and end with an exit check.
- Promote a one-off recipe into a guide only after it has been needed twice.
- Relay any feedback to Haipeng Lin.
