# Derecho prep for the iondrag_calc_ghg demo

Everything below runs on Derecho as the user (autonomy level 0 for the first pass: paste the
output of each numbered block back into the session). Replace `<project>` and `<sandbox>`.
Nothing here writes outside your own home or scratch.

```
export PROJ=<project>
export WS=<sandbox>                               # holds CAM/ and CAM-SIMA/
export DIN=/glade/campaign/cesm/cesmdata/inputdata
export SCR=/glade/derecho/scratch/$USER
export PBS_ACCOUNT=$PROJ
mkdir -p $WS/ic $WS/notes
```

Note (hplin) I used
```
export PROJ=P93300606
export WS=/glade/derecho/scratch/hplin/261006_conversion_demo
export DIN=/glade/campaign/cesm/cesmdata/inputdata
export SCR=/glade/derecho/scratch/$USER
export PBS_ACCOUNT=$PROJ
mkdir -p $WS/ic $WS/notes
```

## 1. Make the ne3np4 L70 initial condition

Source: the ne30pg3 L70 WACCM IC that `FW2000climo` uses on SE (`waccm_phys` attribute in the
namelist defaults). No ne3 IC exists for L70, so regrid horizontally with ESMF bilinear
weights between the SCRIP grids and `ncremap`. (`tools/interpic_new` cannot regrid SE to SE;
the first attempt used it and failed, dry-run item 1.)

```
module load nco
SRC=$DIN/atm/waccm/ic/FW2000.ne30pg3_ne30pg3_nlev70_c230906.nc
OUT=$WS/ic/FW2000_ne3np4_L70_from_ne30pg3_c$(date +%Y%m%d).nc

cd $WS/ic
# working copy: rename ncol_d->ncol, drop the ne30 area fields
ncks -O -x -v area_d,area_weight_gll $SRC FW2000_ne30np4_L70_ncolrenamed.nc
ncrename -d ncol_d,ncol -v lat_d,lat -v lon_d,lon FW2000_ne30np4_L70_ncolrenamed.nc
# bilinear weights between the ne30np4 and ne3np4 grids
/glade/u/apps/derecho/25.10/spack/opt/spack/esmf/8.9.1/intel-oneapi-compilers/2025.2.1/kcws/bin/ESMF_RegridWeightGen \
  -s $DIN/share/scripgrids/ne30np4_091226_pentagons.nc \
  -d $DIN/share/scripgrids/ne3_scrip_230714.nc \
  -w map_ne30np4_to_ne3np4_bilin.nc -m bilinear
ncremap -m map_ne30np4_to_ne3np4_bilin.nc -i FW2000_ne30np4_L70_ncolrenamed.nc -o $OUT
ncdump -h $OUT | grep -E 'ncol = |lev = |ilev = ' # expect ncol = 488, lev = 70, ilev = 71
ncdump -h $OUT | grep -c 'double'                 # a few hundred fields
```

The ESMF path above is the one installed with the Derecho 25.10 software stack; `module
load esmf` and `which ESMF_RegridWeightGen` finds the current one.

## 2. (retired) interpic

Kept only so the numbering of the dry-run log still reads: `tools/interpic_new` builds
(`make FC=ifx ... LDFLAGS="-L$NETCDF/lib -lnetcdff -lnetcdf"`) but cannot regrid SE to SE.

## 3. CAM snapshot case (also the dropsonde CAM case)

```
cd $WS/CAM/cime/scripts
./create_newcase --case $WS/cam_fwsc_iondrag --compset FWsc2000climo \
    --res ne3pg3_ne3pg3_mg37 --compiler gnu --project $PROJ --run-unsupported \
    --output-root $SCR      # not the stale /glade/scratch a login shell may export (dry-run item 13)
cd $WS/cam_fwsc_iondrag
./xmlchange DEBUG=TRUE,NTASKS=1,NTHRDS=1,STOP_OPTION=nsteps,STOP_N=6,DOUT_S=FALSE
./xmlchange ROF_NCPL=$(./xmlquery --value ATM_NCPL),GLC_NCPL=$(./xmlquery --value ATM_NCPL)
./xmlchange --append CAM_CONFIG_OPTS="-pcols 486"
./case.setup
cat >> user_nl_cam <<NL
ncdata = '$OUT'
cam_snapshot_before_num  = 6
cam_snapshot_after_num   = 7
cam_take_snapshot_before = 'iondrag_calc_section'
cam_take_snapshot_after  = 'iondrag_calc_section'
nhtfrq = 0,0,0,0,0,1,1
ndens  = 1,1,1,1,1,1,1
NL
./preview_namelists
grep -n -E 'fincl6|fincl7|ncdata|waccm_forcing_file|cam_take_snapshot|cam_snapshot' CaseDocs/atm_in
```

Output (hplin):
```
44: ncdata    = '/glade/derecho/scratch/hplin/261006_conversion_demo/ic/FW2000_ne3np4_L70_from_ne30pg3_c20261006.nc'
416: cam_snapshot_after_num   = 7
417: cam_snapshot_before_num    = 6
418: cam_take_snapshot_after    = 'iondrag_calc_section'
419: cam_take_snapshot_before   = 'iondrag_calc_section'
538: waccm_forcing_file   = 'SCWACCM_forcing_WACCM6_zm_5day_L70_1975-2014_c191121.nc'

$ ./xmlquery NTASKS,DOUT_S,CAM_CONFIG_OPTS

Results in group build_component_cam
  CAM_CONFIG_OPTS: -phys cam6 -chem waccm_sc_mam4 -pcols 486

Results in group mach_pes
  NTASKS: ['CPL:1', 'ATM:1', 'LND:1', 'ICE:1', 'OCN:1', 'ROF:1', 'GLC:1', 'WAV:1', 'ESP:1']

Results in group run_data_archive
  DOUT_S: FALSE
```

Expect no `fincl6`/`fincl7`, `ncdata` pointing at `$OUT`, and a `waccm_forcing_file`
resolved under `$DIN`. Then:

```
qcmd -A $PROJ -- ./case.build
./case.submit
```

Note (hplin): I changed ndens to 1 throughout for float64 so we can use that for more precise
diagnostic comparisons as well.

## 4. What to paste back after the run

```
RUN=$(./xmlquery --value RUNDIR)
LOG=$(ls -t $RUN/atm.log.* | head -1)
zgrep -n -E 'IONDRAG|NTOP_LEV|NBOT_LEV|Does not have waccm level|nstep, te' $LOG | head -20
ls -l $RUN/*.h5i.* $RUN/*.h6i.*
ncdump -h $RUN/*.h6i.* | grep -E 'time = |double (ptend_[usv]\(|state_[uv]\()'
ncdump -h $RUN/*.h5i.* | grep -E 'time = |double (ptend_[usv]\(|state_[uv]\()'
ncdump -h $RUN/*.h6i.* | grep -c 'double pbuf_'
```

Expected: `IONDRAG flag is T` with `NBOT_LEV` well above the surface, six frames on each
tape (`STOP_N=6`; step 0 is skipped), `ptend_u` and `ptend_v` on the after tape,
`state_u`/`state_v` on both.

Output:
```
3039: From IONDRAGI:
3040: NTOP_LEV  =         1
3041: NBOT_LEV  =        10
3042: IONDRAG flag is T
8676: nstep, te        0   0.26190243548485446E+10   0.26190243548485446E+10  -0.00000000000000000E+00   0.98515142251185083E+05   0.45004999726927503E-03
8727: nstep, te        1   0.26186813049135571E+10   0.26188278487011437E+10   0.81038706351747244E-02   0.98514778331050868E+05   0.45004999726927503E-03
8753: nstep, te        2   0.26188282650758905E+10   0.26188371681241579E+10   0.49233748085807019E-03   0.98514986152472484E+05   0.45004999726927503E-03
8764: nstep, te        3   0.26188531323124347E+10   0.26188465008042049E+10  -0.36672083121890069E-03   0.98515191186298063E+05   0.45004999726927503E-03
8775: nstep, te        4   0.26188327641566706E+10   0.26188469852497969E+10   0.78642217686687146E-03   0.98515303661585800E+05   0.45004999726927503E-03
8786: nstep, te        5   0.26188560171985416E+10   0.26188585333436751E+10   0.13914179873499176E-03   0.98515495620355956E+05   0.45004999726927503E-03
8797: nstep, te        6   0.26188830374053540E+10   0.26188716508134727E+10  -0.62967216386408654E-03   0.98515764552218490E+05   0.45004999726927503E-03
8855: nstep, te        7   0.26188955730612159E+10   0.26188881968153310E+10  -0.40790098412185144E-03   0.98516075786249930E+05   0.45004999726927503E-03
-rw-rw-r-- 1 hplin ncar 550793596 Oct  6 08:35 /glade/derecho/scratch/hplin/cam_fwsc_iondrag/run/cam_fwsc_iondrag.cam.h5i.0001-01-01-01800.nc
-rw-rw-r-- 1 hplin ncar 624799964 Oct  6 08:35 /glade/derecho/scratch/hplin/cam_fwsc_iondrag/run/cam_fwsc_iondrag.cam.h6i.0001-01-01-01800.nc
  time = UNLIMITED ; // (6 currently)
  pbuf_486 = 486 ;
  pbuf_4 = 4 ;
  pbuf_41 = 41 ;
  double pbuf_ACGCME(time, ncol) ;
    pbuf_ACGCME:units = "unset" ;
    pbuf_ACGCME:long_name = "pbuf_ACGCME" ;
    pbuf_ACGCME:cell_methods = "time: point" ;
  double pbuf_ACNUM(time, ncol) ;
    pbuf_ACNUM:units = "unset" ;
    pbuf_ACNUM:long_name = "pbuf_ACNUM" ;
    pbuf_ACNUM:cell_methods = "time: point" ;
  double pbuf_ACPRECL(time, ncol) ;
    pbuf_ACPRECL:units = "unset" ;
    pbuf_ACPRECL:long_name = "pbuf_ACPRECL" ;
    pbuf_ACPRECL:cell_methods = "time: point" ;
  double pbuf_CLDBOT(time, ncol) ;
    pbuf_CLDBOT:units = "1" ;
    pbuf_CLDBOT:long_name = "pbuf_CLDBOT" ;
    pbuf_CLDBOT:cell_methods = "time: point" ;
  double pbuf_CLDTOP(time, ncol) ;
    pbuf_CLDTOP:units = "1" ;
    pbuf_CLDTOP:long_name = "pbuf_CLDTOP" ;
    pbuf_CLDTOP:cell_methods = "time: point" ;
  double pbuf_FLNS(time, ncol) ;
    pbuf_FLNS:units = "W/m2" ;
    pbuf_FLNS:long_name = "pbuf_FLNS" ;
    pbuf_FLNS:cell_methods = "time: point" ;
  double pbuf_FLNT(time, ncol) ;
    pbuf_FLNT:units = "W/m2" ;
  double lat(ncol) ;
    lat:long_name = "latitude" ;
    lat:units = "degrees_north" ;
  double state_u(time, lev, ncol) ;
    state_u:mdims = 1 ;
    state_u:units = "m s-1" ;
    state_u:long_name = "state_u" ;
    state_u:cell_methods = "time: point" ;
  double state_v(time, lev, ncol) ;
    state_v:mdims = 1 ;
```

## If something fails

- Dynamics blows up within six steps: the SE namelist defaults for ne3 were tuned for L32
  to L93 tops. Set `se_nsplit`, `se_rsplit`, and the sponge settings from the ne16 WACCM
  defaults in `bld/namelist_files/namelist_defaults_cam.xml` in `user_nl_cam`.
- Missing constituents on the IC are initialized to their defaults with a warning; that is
  fine for a six-step snapshot.
- `IONDRAG flag is F`: the vertical grid did not come through; check `lev` on `$OUT`.
