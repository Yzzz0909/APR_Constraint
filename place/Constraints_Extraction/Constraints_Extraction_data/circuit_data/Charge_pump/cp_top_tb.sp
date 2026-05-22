*cp_top_tb
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Wed Mar 22 11:38:33 2023
* User     : mujt
* Top Design : ChargePump/cp_top_tb/schematic
****************************************

.GLOBAL

****************************************
* Library : ChargePump
* Cell    : cp_inv
* View    : schematic
****************************************

.SUBCKT cp_inv A Y vdd vss
MPM0 Y A vdd vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MNM0 Y A vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
.ENDS cp_inv
****************************************
* Library : ChargePump
* Cell    : cp_core
* View    : schematic
****************************************

.SUBCKT cp_core en_cp Ibias50u icp_tune<2> icp_tune<1> icp_tune<0> vbias Isink Isource vdd vss
MPM9 net159 icpb<2> vdd vdd p18 L=180n W=2u AD=540f AS=592.5f PD=2.54u PS=2.8425u M=16
MPM8 net155 icpb<1> vdd vdd p18 L=180n W=2u AD=540f AS=645f PD=2.54u PS=3.145u M=8
MPM7 net153 icpb<0> vdd vdd p18 L=180n W=2u AD=540f AS=750f PD=2.54u PS=3.75u M=4
MPM6 net165 enb vdd vdd p18 L=180n W=2u AD=540f AS=960f PD=2.54u PS=4.96u M=2
MPM5 Isource net72 net159 vdd p18 L=2u W=20u AD=5.4p AS=6.45p PD=20.54u PS=25.645u M=8
MPM4 Isource net72 net155 vdd p18 L=2u W=20u AD=5.4p AS=7.5p PD=20.54u PS=30.75u M=4
MPM3 Isource net72 net153 vdd p18 L=2u W=20u AD=5.4p AS=9.6p PD=20.54u PS=40.96u M=2
MPM2 Isource net72 net165 vdd p18 L=2u W=20u AD=9.6p AS=9.6p PD=40.96u PS=40.96u M=1
MPM1 net104 enb vdd vdd p18 L=180n W=2u AD=540f AS=750f PD=2.54u PS=3.75u M=4
MPM0 net72 net72 net104 vdd p18 L=2u W=20u AD=5.4p AS=9.6p PD=20.54u PS=40.96u M=2
RR1 Ibias50u vbias rpdif 2.83613K M=1
XIinv<3> en_cp enb vdd vss cp_inv
XIinv<2> icp_tune<2> icpb<2> vdd vss cp_inv
XIinv<1> icp_tune<1> icpb<1> vdd vss cp_inv
XIinv<0> icp_tune<0> icpb<0> vdd vss cp_inv
XIinv1<3> enb en vdd vss cp_inv
XIinv1<2> icpb<2> icp<2> vdd vss cp_inv
XIinv1<1> icpb<1> icp<1> vdd vss cp_inv
XIinv1<0> icpb<0> icp<0> vdd vss cp_inv
MNM11 vbias enb vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM14 net115 en vss vss n18 L=180n W=1.2u AD=324f AS=576f PD=1.74u PS=3.36u M=2
MNM13 net122 icp<0> vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM10 net41 icp<2> vss vss n18 L=180n W=1.2u AD=324f AS=355.5f PD=1.74u PS=1.9425u M=16
MNM9 net129 icp<1> vss vss n18 L=180n W=1.2u AD=324f AS=387f PD=1.74u PS=2.145u M=8
MNM8 Isink vbias net41 vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u PS=16.895u M=8
MNM7 Isink vbias net129 vss n18 L=2u W=13u AD=3.51p AS=4.875p PD=13.54u PS=20.25u M=4
MNM6 Isink vbias net122 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u PS=26.96u M=2
MNM5 Isink vbias net115 vss n18 L=2u W=13u AD=6.24p AS=6.24p PD=26.96u PS=26.96u M=1
MNM4 net91 en vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM3 net86 en vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM2 net72 vbias net86 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u PS=26.96u M=2
MNM1 vss vbias vss vss n18 L=4u W=4u AD=1.08p AS=1.22p PD=4.54u PS=5.2766666667u M=12
MNM0 Ibias50u Ibias50u net91 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u PS=26.96u M=2
.ENDS cp_core

****************************************
* Library : ChargePump
* Cell    : cp_amp
* View    : schematic
****************************************

.SUBCKT cp_amp ctl inn inp vbias out vdd vss
MNM10 vss vdd vss vss n18 L=4u W=4u AD=2.08p AS=2.08p PD=6.3733333333u PS=6.3733333333u M=3
MNM9 vss vdd vss vss n18 L=4u W=4u AD=2.08p AS=2.08p PD=6.3733333333u PS=6.3733333333u M=3
MNM7 net310 ctn vss vss n18 L=180n W=2u AD=810f AS=1.5p PD=2.81u PS=5.5u M=2
MNM1 net5 inp net61 vss n18 L=600n W=4u AD=1.08p AS=1.5p PD=4.54u PS=6.75u M=4
MNM5 out vbias vss vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u PS=16.895u M=8
MNM0 net61 vbias vss vss n18 L=2u W=13u AD=3.51p AS=4.875p PD=13.54u PS=20.25u M=4
MNM2 net71 inn net61 vss n18 L=600n W=4u AD=1.08p AS=1.5p PD=4.54u PS=6.75u M=4
MNM6 net310 ct vbias vss n18 L=180n W=2u AD=810f AS=1.5p PD=2.81u PS=5.5u M=2
MNM3 net5 out net5 vss n18 L=4u W=4u AD=1.62p AS=1.965p PD=4.81u PS=5.9825u M=8
MNM8 out net310 vss vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u PS=16.895u M=8
MNM4 out net5 out vss n18 L=4u W=4u AD=1.62p AS=1.965p PD=4.81u PS=5.9825u M=8
MPM3 vdd vdd vdd vdd p18 L=200n W=230n AD=199.4f AS=199.4f PD=1.88u PS=1.88u M=1
MPM0 net5 net71 vdd vdd p18 L=600n W=8u AD=2.16p AS=3p PD=8.54u PS=12.75u M=4
MPM2 out net5 vdd vdd p18 L=600n W=6u AD=1.62p AS=1.746p PD=6.54u PS=7.182u M=20
MPM1 net71 net71 vdd vdd p18 L=600n W=8u AD=2.16p AS=3p PD=8.54u PS=12.75u M=4
XI__1 ctn ct vdd vss cp_inv
XI__0 ctl ctn vdd vss cp_inv
.ENDS cp_amp

****************************************
* Library : ChargePump
* Cell    : cp_Tgate
* View    : schematic
****************************************
.SUBCKT cp_Tgate ctl ctl_n A B vdd vss
MNM0 B ctl A vss n18 L=180n W=1.2u AD=324f AS=355.5f PD=1.74u PS=1.9425u M=16
MPM0 B ctl_n A vdd p18 L=180n W=2u AD=540f AS=592.5f PD=2.54u PS=2.8425u M=16
.ENDS cp_Tgate

****************************************
* Library : ChargePump
* Cell    : cp_or
* View    : schematic
****************************************

.SUBCKT cp_or A B Y vdd vss
MPM2 Y net353 vdd vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MPM1 net353 B net337 vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MPM0 net337 A vdd vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MNM2 Y net353 vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
MNM1 net353 B vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
MNM0 net353 A vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
.ENDS cp_or

****************************************
* Library : ChargePump
* Cell    : cp_top
* View    : schematic
****************************************

.SUBCKT cp_top dw dwb en Ibias_skin_50u Icp_tune<2> Icp_tune<1> Icp_tune<0> up upb cp_out vdd vss
XI__0 en Ibias_skin_50u Icp_tune<2> Icp_tune<1> Icp_tune<0> net229 net221 net3 vdd vss cp_core
XI__1 net356 net227 cp_out net229 net227 vdd vss cp_amp
XI__11 dwb_ctln dwb_ctl vdd vss cp_inv
XI__10 dw_ctln dw_ctl vdd vss cp_inv
XI__9 upb_ctln upb_ctl vdd vss cp_inv
XI__8 up_ctln up_ctl vdd vss cp_inv
XI__7 dwb dwb_ctln vdd vss cp_inv
XI__6 dw dw_ctln vdd vss cp_inv
XI__5 upb upb_ctln vdd vss cp_inv
XI__4 up up_ctln vdd vss cp_inv
XI__13 dw_ctl dw_ctln net221 cp_out vdd vss cp_Tgate
XI__12 up_ctl up_ctln cp_out net3 vdd vss cp_Tgate
XI__3 upb_ctl upb_ctln net227 net3 vdd vss cp_Tgate
XI__2 dwb_ctl dwb_ctln net221 net227 vdd vss cp_Tgate
XI__22 Icp_tune<1> Icp_tune<2> net356 vdd vss cp_or
.ENDS cp_top

****************************************
* Library : ChargePump
* Cell    : cp_top_tb
* View    : schematic
****************************************

**TopDesStart
XI__0 net9 net2 vdd net394 itune<2> itune<1> itune<0> net3 net1 net411 vdd 0 cp_top
VV5 net411 0 DC vcp_out
VV4 itune<2> 0 DC itune2
VV3 itune<1> 0 DC itune1
VV2 itune<0> 0 DC itune0
VV0 vdd 0 DC 1.8
II9 vdd net394 DC 50u
VV9 net2 0 0 PULSE(0 1.8 0 1n 1n 500n 1u)
VV8 net9 0 1.8 PULSE(1.8 0 0 1n 1n 500n 1u)
VV7 net1 0 0 PULSE(0 1.8 100n 1n 1n 500n 1u)
VV6 net3 0 1.8 PULSE(1.8 0 100n 1n 1n 500n 1u)
**TopDesEnd