************************************************************************
* auCdl Netlist:
*
* Library Name:  biasing_circuits
* Top Cell Name: nmos current mirror
* View Name:     schematic
* Netlisted on:  Mar 31 15:07:06 2019
************************************************************************

*.BIPOLAR
*.RESI = 2000
*.RESVAL
*.CAPVAL
*.DIOPERI
*.DIOAREA
*.EQUATION
*.SCALE METER
*.MEGA
.PARAM

*.GLOBAL vdd!
*+        gnd!

*.PIN vdd!
*+    gnd!

************************************************************************
* Library Name: biasing_circuits
* Cell Name:    nmos current mirror
* View Name:    schematic
************************************************************************

.SUBCKT CurrentMirror Vbiasn
MM0 Vbiasn Vbiasn gnd! gnd! nmos w=WA l=LA nfin=nA
MM1 vdd! Vbiasn gnd! gnd! nmos w=WA l=LA nfin=nA
.ENDS