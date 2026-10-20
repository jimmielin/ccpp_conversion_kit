# kit.local.md

Answers from the setup interview. Edit by hand when something changes.

- machine: derecho
- project: <project>          # ./xmlquery PROJECT in any existing case shows one
- cam: /glade/derecho/scratch/<user>/<sandbox>/CAM
- cam_sima: /glade/derecho/scratch/<user>/<sandbox>/CAM-SIMA
- scratch_root: /glade/derecho/scratch/<user>
- compiler: gnu
- autonomy: 1          # 0 = user runs cluster commands, 1 = confirm first, 2 = run and report
- github_write: no     # no = all work stays in local branches, the user pushes and opens PRs
                       # yes = Claude may push to the fork below and open PRs (never to ESCOMP)
- atmospheric_physics_fork: git@github.com:<user>/atmospheric_physics.git   # used at phase 6
- atmospheric_physics_branch: <user>/<scheme>_ccpp
- scheme: iondrag_calc_ghg
- compset: FWsc2000climo
- grid: ne3pg3_ne3pg3_mg37
- notes: snapshots live in the CAM case run directory until the PR
