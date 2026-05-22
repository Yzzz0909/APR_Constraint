*ota
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Thu Jan 29 10:39:52 2026
* User     : lijialun
* Top Design : sdadc/ota/schematic
****************************************

****************************************
* Library : sdadc
* Cell    : ota
* View    : schematic
****************************************

**TopDesStart
XM1 net15 net15 AVDD AVDD p33_ckt mr=2 w=700n l=350n nf=1 as=336f ad=336f ps=2.36u pd=2.36u nrs=0.385714 nrd=0.385714 sa=480n sb=480n sd=0 sca=0 scb=0 scc=0 mismod=1
XM0 VOUT net15 AVDD AVDD p33_ckt mr=2 w=700n l=350n nf=1 as=336f ad=336f ps=2.36u pd=2.36u nrs=0.385714 nrd=0.385714 sa=480n sb=480n sd=0 sca=0 scb=0 scc=0 mismod=1
XM4 net14 VB AVSS AVSS n33_ckt mr=5 w=1.75u l=350n nf=1 as=840f ad=840f ps=4.46u pd=4.46u nrs=0.154286 nrd=0.154286 sa=480n sb=480n sd=0 sca=0 scb=0 scc=0 mismod=1
XM3 VOUT VINN net14 AVSS n33_ckt mr=5 w=1.75u l=350n nf=1 as=840f ad=840f ps=4.46u pd=4.46u nrs=0.154286 nrd=0.154286 sa=480n sb=480n sd=0 sca=0 scb=0 scc=0 mismod=1
XM2 net15 VINP net14 AVSS n33_ckt mr=5 w=1.75u l=350n nf=1 as=840f ad=840f ps=4.46u pd=4.46u nrs=0.154286 nrd=0.154286 sa=480n sb=480n sd=0 sca=0 scb=0 scc=0 mismod=1
**TopDesEnd