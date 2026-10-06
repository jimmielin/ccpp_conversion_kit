# 40. Phase 4: run on Derecho and read the check

## The loop

```
edit scheme / meta / suite in atmospheric_physics  ->  commit, push, pull into the other copy
  -> qcmd -A <project> -- ./case.build        (incremental; only atm rebuilds)
  -> ./case.submit
  -> read atm.log: IC reads, then the per-step check blocks
  -> all steps clean? phase 6.  Differences? classify, then phase 5 if not obvious.
```

Apply the autonomy level from `kit.local.md` to every state-changing command.

## Commands

| Need | Command |
|---|---|
| Build | `qcmd -A <project> -- ./case.build` (set `PBS_ACCOUNT` in non-interactive shells); from a remote one-liner, `nohup qcmd -A <project> -- ./case.build > <sandbox>/notes/build_<case>.log 2>&1 < /dev/null &` and poll the log for `MODEL BUILD HAS FINISHED` or `BUILD FAIL` |
| Submit | `./case.submit`; `qstat -u $USER` to watch |
| Where things are | `./xmlquery RUNDIR`, `./xmlquery EXEROOT` |
| Newest log | `ls -t $(./xmlquery --value RUNDIR)/atm.log.* \| head -1` (may be `.gz`; `zless`) |
| Effective namelist | `$(./xmlquery --value RUNDIR)/atm_in` or `CaseDocs/atm_in` |
| Failed build then "env_build HAS CHANGED" | `./xmlchange BUILD_STATUS=0` when only source changed |
| Modern Python in a remote one-liner | `bash -lc '...'` |

CAM-SIMA regenerates caps and the registry on `case.build` when metadata changed; CAM needs
the scheme directory in `bld/configure`'s Filepath list (phase 1).

## Reading atm.log

1. IC reads first. Every snapshot-fed variable prints a reading line. Search for `not found`:
   a required input that could not be read means the registry `ic_file_input_names` does not
   match the snapshot field name, or a constituent was declared but never registered (the
   message then lists the scheme's local variable name as the fallback). Fix these before
   looking at any difference.
2. The init table of your scheme (indices, levels, activation flags) should match the CAM
   snapshot run's init log line for line.
3. Then the check: one `Physics Check Data Results` block per step. A clean step ends with
   `No differences found!`; a step with differences prints a table (`Variable`, `# Diffs`,
   `Max Diff`, location) above the list of clean variables. `Max Diff` is relative for values
   above `min_relative_value` (default 1e-5) and absolute below it, so a 1-ulp seed in a large
   field is invisible in the state but surfaces in the `_due_to_model_physics` accumulators,
   where cancellation amplifies it. A green state check is therefore not a bitwise proof;
   dropsonde (phase 5) is. A difference at the first compared step in a variable the scheme
   never touches is wiring or snapshot, not physics.
4. An end-of-tape message about a time level exceeding the file limit at the last step is
   benign.

Expected-noise rows (comparison artifacts you have explained and documented) can be removed
with `ncdata_check_exclude` (gitignore-style patterns) so `ncdata_check_err = .true.` gives a
hard pass/fail. Excluded rows are still listed; never exclude to hide a difference you do not
understand.

## Classify before editing

- Wiring: a standard name resolved to the wrong host variable, a unit mismatch, a dimension
  mismatch (`vertical_layer_dimension` vs `vertical_interface_dimension`), latitude in degrees
  vs radians. Grep the generated cap in `bld/atm/obj/ccpp/` for the variable.
- Harness: wrong tape mounted, wrong frame, a field missing from the tape, namelist value
  differing from the CAM run's `atm_in`, a calendar or timestep setting.
- Port: the scheme itself. Historically the least likely under this workflow, because phase 1
  proved it inside CAM; prove it with dropsonde rather than assuming.

If the first differing variable is not obvious from the log, go to phase 5.

## Derecho etiquette

Write only under your home, scratch, and work. Do not `find` across model trees. `git status
--ignore-submodules`. Running `cesm.exe` by hand (dropsonde does) truncates the component logs
of the previous batch job in that run directory; copy logs you want to keep first.

## Exit check

Every step reports no differences above threshold for every compared variable, with no
exclusions you cannot explain in one sentence each.
