*cp_or
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Thu Mar 23 13:49:48 2023
* User     : mujt
* Top Design : ChargePump/cp_or/schematic
****************************************

****************************************
* Library : ChargePump
* Cell    : cp_or
* View    : schematic
****************************************

**TopDesStart
MPM2 Y net353 vdd vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MPM1 net353 B net337 vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MPM0 net337 A vdd vdd p18 L=180n W=1u AD=480f AS=480f PD=2.96u PS=2.96u M=1
MNM2 Y net353 vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
MNM1 net353 B vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
MNM0 net353 A vss vss n18 L=180n W=600n AD=288f AS=288f PD=2.16u PS=2.16u M=1
**TopDesEnd