# 50. Phase 5: dropsonde

dropsonde runs CAM and CAM-SIMA under gdb, breaks at every scheme `_run` in the suite,
dumps the arguments on entry and exit in both models, and diffs them. It tells you the first
argument of the first scheme where the two models disagree, so you fix the cause instead of
bisecting by hand. Repository: github.com/jimmielin/dropsonde; its README is authoritative
for options, and `docs/reading_dropsonde_output_guide.md` for interpretation.

## Preconditions

- CAM case: `DEBUG=TRUE`, `NTASKS=1`, `NTHRDS=1`, dechunked (`-pcols <total columns>` in
  `CAM_CONFIG_OPTS`, 486 at ne3pg3), calling the same CCPPized source as CAM-SIMA. The
  snapshot case from phase 2 qualifies if it was created that way; otherwise clone it.
- CAM-SIMA case: `DEBUG=TRUE`, single rank, same compiler as CAM.
- Both copies of atmospheric_physics at the same commit (`git rev-parse HEAD` in both).
- `./preview_namelists` run in both cases; `STOP_N` of at least 6 steps for CAM (coupling
  minimum); dropsonde kills each run as soon as it has what it needs.
- `gdb` on PATH (Derecho's default is fine).

## Run

On a compute node, not a login node. First copy the batch logs aside, because running
`cesm.exe` by hand truncates them in both run directories:

```
mkdir -p <sandbox>/notes/logs_before_dropsonde
cp -p /glade/derecho/scratch/$USER/<cam case>/run/*.log.* \
      /glade/derecho/scratch/$USER/<sima case>/run/*.log.* \
      <sandbox>/notes/logs_before_dropsonde/
```

The batch form avoids an interactive session:

```
qcmd -A <project> -l walltime=01:00:00 -- bash -lc '
  cd <sandbox>/dropsonde &&
  ./dropsonde --cam  /glade/derecho/scratch/$USER/<cam case>  \
              --sima /glade/derecho/scratch/$USER/<sima case> \
              --sdf  <atmospheric_physics>/test/test_suites/suite_<scheme>.xml \
              --out  <sandbox>/notes/dropsonde_<scheme>_<n>'
```

The case arguments are the directories that contain `bld/cesm.exe` and `run/`
(`/glade/derecho/scratch/$USER/<case>` on Derecho). `--steps 1` is the default and decisive
for snapshot runs; `--steps 2` also covers first-timestep logic. Output: `report.txt`,
`suite.json`, and raw dumps under `cam/` and `sima/`. `python3 differ.py <out>` regenerates
the report without rerunning. `--skip-cam` or `--skip-sima` reuses one side's capture when
only the other changed.

## Read the report, top to bottom

1. **Schemes compared.** SIMA-only interstitials are listed and skipped; that is expected.
2. **Constituent mapping.** Species counts must match and nothing may be unmatched. Two
   near-duplicate standard names for one quantity is a registry bug found here in seconds.
3. **Call alignment.** Hit counts per call site; CAM calling a utility many more times than
   SIMA is normal (CAM runs the whole model). Wildly different counts for the scheme itself
   mean chunking is on or a loop differs.
4. **Comparison.** A clean run prints `No differences found in any subroutines!` with the
   number of hit pairs and argument captures; that line is the exit check. Otherwise the
   `FIRST DIVERGENCE` box is the lead. `[INPUTS DIFFER]` means the models
   handed the scheme different data: the cause is upstream, in wiring, initialization, or an
   earlier scheme. `[OUTPUTS DIFFER]` with matching inputs means the cause is inside the
   scheme or the build. Everything below the first divergence is usually propagation.
5. **Per-scheme summary.** How many schemes are bit-for-bit.

Noise to note but not chase: `[note]` lines (often real but unrelated bugs, such as an array
sized one layer too big), tiny floor values differing (`1e-37` vs `0`), hit-count mismatches
on utility routines, by-design shape mismatches the report flags itself. `nan` on the CAM
side is uninitialized memory that the scheme never read if the outputs still match.

## Pathology catalogue

Match the fingerprint before theorizing.

| Fingerprint | Cause | Check |
|---|---|---|
| Every field that lives on only one tape reads zero on the SIMA side; met fields match | wrong tape mounted, or the field is written on the other tape | `ncdump -v <field>` on the mounted file |
| One input zero while its neighbours are fine; log says `X not found, also looked for: [<local name>, ,]` | constituent declared in the registry but not registered by any scheme; or a case mismatch between the scheme's lowercase standard name and the registry's authored case | grep the generated `phys_vars_init_check.F90` for both spellings |
| A constituent-dimensioned read misses exactly one species | the first `ic_file_input_names` entry (the shortname) differs from the name CAM used in the capture | the "not found for constituent" message prints the shortname |
| Near every cell of specific species differs by about 1 ulp at each unit touchpoint | g/mol to kg/mol to g/mol round trip, or `tendency*dt` where CAM stores a difference | compare the operation order, not the formula |
| Differences look like one-timestep deltas of the fields themselves | off-by-one frame or a stale tape | confirm the capture regenerated and the case mounts the new files |
| Everything differs from the first compared scheme | wrong snapshot or wrong step pairing; the report's `alignment check` verdict says which | |
| A small answer difference and the scheme's log shows it disabled itself | GNU on Derecho zeroes the hidden length of deferred-length module character arrays across use association | store fixed-length copies |
| `[INPUTS DIFFER]` on `latitude` (or `longitude`) only, about 1e-16 at a few dozen columns; outputs differ at 1e-18 in the fields that use it | the null dycore rebuilds radians from the snapshot's degrees coordinates, while CAM hands schemes its native radians. The host fix (CAM writes `lat_rad`/`lon_rad` on the tapes, the null dycore prefers them) is pending on the `hplin/iondrag_demo` branches, CAM 6fc7772fa and CAM-SIMA 89beb07f, not yet on the base branches | harness; exclude the affected `_due_to_model_physics` accumulator with a comment, or build both models from the fix branches and regenerate the snapshot |
| Integer vs real exponent, partial fill of an `intent(out)` array, a missing clamp that CAM applied in `physics_update` | genuine port differences | `references/framework_gotchas.md`, b4b discipline |

## The loop

Run, find the first divergence, classify it (wiring, harness, port), fix, rebuild the side
that changed (both if atmospheric_physics changed), rerun with `--skip-*` for the unchanged
side, until every compared scheme is bit-for-bit at step 1, then once more with `--steps 2`.
When the only remaining divergence is a documented harness seed (the latitude row above),
say so in the notes instead of running `--steps 2`; a second step reproduces it identically.

## Exit check

A dropsonde report with zero differing arguments on every compared scheme, archived under
`notes/`, and the CAM-SIMA check (phase 4) clean on all steps.
