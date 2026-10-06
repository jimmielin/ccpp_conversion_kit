# kit.local.md

Answers from the setup interview. Edit by hand when something changes.

- machine: derecho
- project: P93300606
- cam: /glade/derecho/scratch/<user>/<sandbox>/CAM
- cam_sima: /glade/derecho/scratch/<user>/<sandbox>/CAM-SIMA
- scratch_root: /glade/derecho/scratch/<user>
- compiler: gnu
- autonomy: 1          # 0 = user runs cluster commands, 1 = confirm first, 2 = run and report
- atmospheric_physics_fork: git@github.com:<user>/atmospheric_physics.git
- atmospheric_physics_branch: <user>/<scheme>_ccpp
- scheme: iondrag_calc_ghg
- compset: FWsc2000climo
- grid: ne3pg3_ne3pg3_mg37
- notes: snapshots live in the CAM case run directory until the PR
