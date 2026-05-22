** Generated for: hspiceD
** Generated on: Feb  6 11:08:40 2026
** Design library name: sdadc
** Design cell name: comparator_A
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

** Library name: sdadc
** Cell name: Nand_A
** View name: schematic
.subckt Nand_A a b gnd out vdd
m1 out b vdd vdd p33 m=1 w=2.485e-6 l=300e-9 nf=1 ad=1.1928e-12 as=1.1928e-12 pd=5.93e-6 ps=5.93e-6 nrd=108.652e-3 nrs=108.652e-3 sa=480e-9 sb=480e-9 sd=0 sca=0 scb=0 scc=0
m0 out a vdd vdd p33 m=1 w=2.485e-6 l=300e-9 nf=1 ad=1.1928e-12 as=1.1928e-12 pd=5.93e-6 ps=5.93e-6 nrd=108.652e-3 nrs=108.652e-3 sa=480e-9 sb=480e-9 sd=0 sca=0 scb=0 scc=0
m3 net1 b gnd gnd n33 m=1 w=1.235e-6 l=350e-9 nf=1 ad=592.8e-15 as=592.8e-15 pd=3.43e-6 ps=3.43e-6 nrd=218.623e-3 nrs=218.623e-3 sa=480e-9 sb=480e-9 sd=0 sca=0 scb=0 scc=0
m2 out a net1 gnd n33 m=1 w=1.235e-6 l=350e-9 nf=1 ad=592.8e-15 as=592.8e-15 pd=3.43e-6 ps=3.43e-6 nrd=218.623e-3 nrs=218.623e-3 sa=480e-9 sb=480e-9 sd=0 sca=0 scb=0 scc=0
.ends Nand_A
** End of subcircuit definition.

** Library name: sdadc
** Cell name: SR_latch_nand_A
** View name: schematic
.subckt SR_latch_nand_A gnd q q_ r_ s_ vdd
xi2 s_ q_ gnd q vdd Nand_A
xi3 q r_ gnd q_ vdd Nand_A
.ends SR_latch_nand_A
** End of subcircuit definition.

** Library name: sdadc
** Cell name: comparator_A
** View name: schematic
m10 net9 clk vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m9 r_ clk vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m8 net19 clk vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m4 s_ clk vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m1 s_ r_ vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m0 r_ s_ vdd vdd p33 m=1 w=5e-6 l=300e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m5 net13 clk gnd gnd n33 m=1 w=5e-6 l=500e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m6 net19 _net2 net13 gnd n33 m=1 w=5e-6 l=500e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m7 net9 _net3 net13 gnd n33 m=1 w=5e-6 l=500e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m3 s_ r_ net19 gnd n33 m=1 w=5e-6 l=350e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
m2 r_ s_ net9 gnd n33 m=1 w=5e-6 l=350e-9 nf=2 ad=1.35e-12 as=2.4e-12 pd=6.08e-6 ps=11.92e-6 nrd=54e-3 nrs=54e-3 sa=480e-9 sb=480e-9 sd=540e-9 sca=0 scb=0 scc=0
xi1 gnd _net0 _net1 r_ s_ vdd SR_latch_nand_A
.END