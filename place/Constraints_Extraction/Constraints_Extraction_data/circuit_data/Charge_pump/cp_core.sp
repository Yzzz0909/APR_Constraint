*cp_core
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Thu Mar 23 13:50:21 2023
* User     : mujt
* Top Design : ChargePump/cp_core/schematic
****************************************

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

**TopDesStart
MPM9 net159 icpb<2> vdd vdd p18 L=180n W=2u AD=540f AS=592.5f PD=2.54u 
+PS=2.8425u M=16
MPM8 net155 icpb<1> vdd vdd p18 L=180n W=2u AD=540f AS=645f PD=2.54u PS=3.145u 
+M=8
MPM7 net153 icpb<0> vdd vdd p18 L=180n W=2u AD=540f AS=750f PD=2.54u PS=3.75u 
+M=4
MPM6 net165 enb vdd vdd p18 L=180n W=2u AD=540f AS=960f PD=2.54u PS=4.96u M=2
MPM5 Isource net72 net159 vdd p18 L=2u W=20u AD=5.4p AS=6.45p PD=20.54u 
+PS=25.645u M=8
MPM4 Isource net72 net155 vdd p18 L=2u W=20u AD=5.4p AS=7.5p PD=20.54u PS=30.75u
+M=4
MPM3 Isource net72 net153 vdd p18 L=2u W=20u AD=5.4p AS=9.6p PD=20.54u PS=40.96u
+M=2
MPM2 Isource net72 net165 vdd p18 L=2u W=20u AD=9.6p AS=9.6p PD=40.96u PS=40.96u
+M=1
MPM1 net104 enb vdd vdd p18 L=180n W=2u AD=540f AS=750f PD=2.54u PS=3.75u M=4
MPM0 net72 net72 net104 vdd p18 L=2u W=20u AD=5.4p AS=9.6p PD=20.54u PS=40.96u 
+M=2
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
MNM13 net122 icp<0> vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u 
+M=4
MNM10 net41 icp<2> vss vss n18 L=180n W=1.2u AD=324f AS=355.5f PD=1.74u 
+PS=1.9425u M=16
MNM9 net129 icp<1> vss vss n18 L=180n W=1.2u AD=324f AS=387f PD=1.74u PS=2.145u 
+M=8
MNM8 Isink vbias net41 vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u 
+PS=16.895u M=8
MNM7 Isink vbias net129 vss n18 L=2u W=13u AD=3.51p AS=4.875p PD=13.54u 
+PS=20.25u M=4
MNM6 Isink vbias net122 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u PS=26.96u
+M=2
MNM5 Isink vbias net115 vss n18 L=2u W=13u AD=6.24p AS=6.24p PD=26.96u PS=26.96u
+M=1
MNM4 net91 en vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM3 net86 en vss vss n18 L=180n W=1.2u AD=324f AS=450f PD=1.74u PS=2.55u M=4
MNM2 net72 vbias net86 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u PS=26.96u 
+M=2
MNM1 vss vbias vss vss n18 L=4u W=4u AD=1.08p AS=1.22p PD=4.54u PS=5.2766666667u
+M=12
MNM0 Ibias50u Ibias50u net91 vss n18 L=2u W=13u AD=3.51p AS=6.24p PD=13.54u 
+PS=26.96u M=2
**TopDesEnd