*sub_0_9.2.2
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Wed Jan  7 19:40:57 2026
* User     : u23_yangzhe
* Top Design : lib/9.2.2/schematic
****************************************

****************************************
* Library : lib
* Cell    : 9.2.2
* View    : schematic
****************************************

**TopDesStart
MNM2 vout net1 gnda gnda n18 L=1.5u W=100u AD=27p AS=28.05p PD=100.54u PS=105.561u M=40
MNM1 net1 net0 gnda gnda n18 L=1u W=50u AD=15.6p AS=15.6p PD=60.624u PS=60.624u M=5
MNM0 net0 net0 gnda gnda n18 L=1u W=50u AD=15.6p AS=15.6p PD=60.624u PS=60.624u M=5
MPM4 lb_100u lb_100u Vdda Vdda p18 L=1u W=360n AD=124.2f AS=125.964f PD=1.04u PS=1.0568u M=100
MPM3 vout lb_100u Vdda Vdda p18 L=4u W=80u AD=21.6p AS=21.936p PD=80.54u PS=82.1484u M=100
MPM2 net17 lb_100u Vdda Vdda p18 L=6.5u W=12u AD=3.24p AS=3.2904p PD=12.54u PS=12.7884u M=100
MPM1 net1 Vinp net17 Vdda p18 L=1.5u W=6u AD=1.62p AS=1.6452p PD=6.54u PS=6.6684u M=100
MPM0 net0 Vinn net17 Vdda p18 L=1.5u W=6u AD=1.62p AS=1.6452p PD=6.54u PS=6.6684u M=100
CC0 net2 vout 10p
RR0 net1 net2 250
**TopDesEnd
