************************************************************************
* auCdl Netlist:
*
* Library Name:  biasing_circuits
* Top Cell Name: pmos load
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
* Cell Name:    pmos load
* View Name:    schematic
************************************************************************

.SUBCKT DifferentialPair_pmos Voutn Voutp Vbiasn
MM0 Voutn Vbiasn vdd! gnd! pmos w=WA l=LA nfin=nA
MM1 Voutp Vbiasn vdd! gnd! pmos w=WA l=LA nfin=nA
.ENDS