** Generated for: hspiceD
** Generated on: May 23 14:44:20 2026
** Design library name: twoStageMiller
** Design cell name: twoStageMiller
** Design view name: schematic


.TEMP 25.0
.OPTION     ARTIST=2     INGOLD=2     PARHIER=LOCAL     PSF=2
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" BJT_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" DIO_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" RES_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" MIM_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/ms018_enhanced_v1p11.lib" VAR_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" RES_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" MIM_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" VAR_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" IND_RF_PSUB_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" IND_RF_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" 3TDIFF_PSUB_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" 3TDIFF_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" 2TDIFF_PSUB_TT
.LIB "/opt/PDK/smic18mserf_1833_oa_cds_v1.11_0/models/hspice/mse018_v1p11_rf.lib" 2TDIFF_TT

** Library name: smic18mmrf
** Cell name: rpposab
** View name: schematic
.subckt rpposab_pcell_0 minus plus
r2 n2 minus rpposab m=1 l=segl w=segw
r1 n1 n2 rpposab m=1 l=segl w=segw
r0 plus n1 rpposab m=1 l=segl w=segw
.ends rpposab_pcell_0
** End of subcircuit definition.

** Library name: twoStageMiller
** Cell name: twoStageMiller
** View name: schematic
mnm48 vout net0239 gnda gnda n18 m=4 w=12e-6 l=300e-9 nf=2 ad=3.24e-12 as=5.76e-12 pd=13.08e-6 ps=25.92e-6 nrd=22.5e-3 nrs=22.5e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mnm7 net0239 vbn gnda gnda n18 m=2 w=8e-6 l=2e-6 nf=2 ad=2.16e-12 as=3.84e-12 pd=9.08e-6 ps=17.92e-6 nrd=33.75e-3 nrs=33.75e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mnm6 vbn vbn gnda gnda n18 m=2 w=8e-6 l=2e-6 nf=2 ad=2.16e-12 as=3.84e-12 pd=9.08e-6 ps=17.92e-6 nrd=33.75e-3 nrs=33.75e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
xr1 net0239 net087 rpposab_pcell_0 m=1 segl=10e-6 segw=2e-6
c0 net087 vout mim w=15e-6 l=15e-6 m=34
mpm3 as_ibpd_1u as_ibpd_1u vdda vdda p18 m=1 w=1e-6 l=2e-6 nf=2 ad=270e-15 as=480e-15 pd=2.08e-6 ps=3.92e-6 nrd=270e-3 nrs=270e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mpm4 nwell_diff as_ibpd_1u vdda vdda p18 m=12 w=1e-6 l=2e-6 nf=2 ad=270e-15 as=480e-15 pd=2.08e-6 ps=3.92e-6 nrd=270e-3 nrs=270e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mpm1 net0239 vinp nwell_diff nwell_diff p18 m=8 w=8e-6 l=300e-9 nf=2 ad=2.16e-12 as=3.84e-12 pd=9.08e-6 ps=17.92e-6 nrd=33.75e-3 nrs=33.75e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mpm5 vout as_ibpd_1u vdda vdda p18 m=48 w=1e-6 l=2e-6 nf=2 ad=270e-15 as=480e-15 pd=2.08e-6 ps=3.92e-6 nrd=270e-3 nrs=270e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
mpm0 vbn vinn nwell_diff nwell_diff p18 m=8 w=8e-6 l=300e-9 nf=2 ad=2.16e-12 as=3.84e-12 pd=9.08e-6 ps=17.92e-6 nrd=33.75e-3 nrs=33.75e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
.END
