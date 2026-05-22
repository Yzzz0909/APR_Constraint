*cp_amp
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Thu Mar 23 13:50:43 2023
* User     : mujt
* Top Design : ChargePump/cp_amp/schematic
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
* Cell    : cp_amp
* View    : schematic
****************************************

**TopDesStart
MNM10 vss vdd vss vss n18 L=4u W=4u AD=2.08p AS=2.08p PD=6.3733333333u 
+PS=6.3733333333u M=3
MNM9 vss vdd vss vss n18 L=4u W=4u AD=2.08p AS=2.08p PD=6.3733333333u 
+PS=6.3733333333u M=3
MNM7 net310 ctn vss vss n18 L=180n W=2u AD=810f AS=1.5p PD=2.81u PS=5.5u M=2
MNM1 net5 inp net61 vss n18 L=600n W=4u AD=1.08p AS=1.5p PD=4.54u PS=6.75u M=4
MNM5 out vbias vss vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u PS=16.895u 
+M=8
MNM0 net61 vbias vss vss n18 L=2u W=13u AD=3.51p AS=4.875p PD=13.54u PS=20.25u 
+M=4
MNM2 net71 inn net61 vss n18 L=600n W=4u AD=1.08p AS=1.5p PD=4.54u PS=6.75u M=4
MNM6 net310 ct vbias vss n18 L=180n W=2u AD=810f AS=1.5p PD=2.81u PS=5.5u M=2
MNM3 net5 out net5 vss n18 L=4u W=4u AD=1.62p AS=1.965p PD=4.81u PS=5.9825u M=8
MNM8 out net310 vss vss n18 L=2u W=13u AD=3.51p AS=4.1925p PD=13.54u PS=16.895u 
+M=8
MNM4 out net5 out vss n18 L=4u W=4u AD=1.62p AS=1.965p PD=4.81u PS=5.9825u M=8
MPM3 vdd vdd vdd vdd p18 L=200n W=230n AD=199.4f AS=199.4f PD=1.88u PS=1.88u M=1
MPM0 net5 net71 vdd vdd p18 L=600n W=8u AD=2.16p AS=3p PD=8.54u PS=12.75u M=4
MPM2 out net5 vdd vdd p18 L=600n W=6u AD=1.62p AS=1.746p PD=6.54u PS=7.182u M=20
MPM1 net71 net71 vdd vdd p18 L=600n W=8u AD=2.16p AS=3p PD=8.54u PS=12.75u M=4
XI__1 ctn ct vdd vss cp_inv
XI__0 ctl ctn vdd vss cp_inv
**TopDesEnd