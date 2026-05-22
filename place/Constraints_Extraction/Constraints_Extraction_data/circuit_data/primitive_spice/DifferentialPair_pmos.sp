************************************************************************
* auCdl Netlist:
*
* Library Name:  biasing_circuits
* Top Cell Name: pmos differential pair
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
* Cell Name:    pmos differential pair
* View Name:    schematic
************************************************************************

.SUBCKT DifferentialPair_pmos Voutn Voutp Vinp Vinn
MM0 Voutn Vinp gnd! gnd! pmos w=WA l=LA nfin=nA
MM1 Voutp Vinn gnd! gnd! pmos w=WA l=LA nfin=nA
.ENDS