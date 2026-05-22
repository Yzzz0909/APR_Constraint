*REFF_amp1
****************************************
* Type     : hspice
* Tool     : AETHER-SE
* Date     : Mon Apr 24 10:51:16 2023
* User     : mujt
* Top Design : adc_lay_liuyx1/REFF_amp1/schematic
****************************************

****************************************
* Library : adc_lay_liuyx1
* Cell    : inv_33_x1
* View    : schematic
****************************************

.SUBCKT inv_33_x1 A Y avdd avss
XPM0 Y A avdd avdd pod33ll_ckt w=3u l=550n nf=1 as=510f ad=510f ps=6.34u pd=6.34u nrd=36.6667m nrs=36.6667m sa=170n sb=170n sd=0 sca=0.731058 scb=13.7308n scc=102.577a DCN=21 DPS=220n DPCS=80n DSTS=1u mr=1 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM0 Y A avss avss nod33ll_ckt w=1u l=550n nf=1 as=170f ad=170f ps=2.34u pd=2.34u nrd=0.11 nrs=0.11 sa=170n sb=170n sd=0 sca=0.895667 scb=18.0166n scc=134.363a DCN=7 DPS=220n DPCS=80n DSTS=1u mr=1 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
.ENDS inv_33_x1

****************************************
* Library : adc_lay_liuyx1
* Cell    : REFF_amp1
* View    : schematic
****************************************

**TopDesStart
XNM6 net11 bin1 avss avss nod33ll_ckt w=20u l=1u nf=1 as=3.4p ad=3.4p ps=40.34u pd=40.34u nrd=5.5m nrs=5.5m sa=170n sb=170n sd=0 sca=0.467639 scb=6.75079n scc=50.063a DCN=143 DPS=220n DPCS=80n DSTS=1u mr=12 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM5 net6 bin1 avss avss nod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=8 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM4 net10 inn net6 avss nod33ll_ckt w=6u l=2u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.462963 scb=4.28696n scc=31.7861a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=16 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM3 net8 inp net6 avss nod33ll_ckt w=6u l=2u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.462963 scb=4.28696n scc=31.7861a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=16 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM2 bin1 enb avss avss nod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=2 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM1 bin1 bin1 avss avss nod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=4 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XNM0 idcn end bin1 avss nod33ll_ckt w=6u l=600n nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.629155 scb=11.727n scc=87.4096a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=1 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM5 outn net10 avdd avdd pod33ll_ckt w=20u l=600n nf=1 as=3.4p ad=3.4p ps=40.34u pd=40.34u nrd=5.5m nrs=5.5m sa=170n sb=170n sd=0 sca=0.530951 scb=10.9768n scc=81.847a DCN=143 DPS=220n DPCS=80n DSTS=1u mr=20 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM4 net8 net8 avdd avdd pod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=8 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM3 net10 net8 avdd avdd pod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=8 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM2 net10 end avdd avdd pod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=2 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM1 net10 net10 net5 avdd pod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=1 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XPM0 net5 net5 avdd avdd pod33ll_ckt w=6u l=1u nf=1 as=1.02p ad=1.02p ps=12.34u pd=12.34u nrd=18.3333m nrs=18.3333m sa=170n sb=170n sd=0 sca=0.565844 scb=7.50101n scc=55.6256a DCN=43 DPS=220n DPCS=80n DSTS=1u mr=1 mismod=1 globalmod=1 prelayout=1 LPEMOD=1
XI1 enb end avdd avss inv_33_x1
XI0 en enb avdd avss inv_33_x1
xr0 outn net11 rpposab_2t_ckt w=8u l=2u mismod=1 flag_cc=1 mr=1
**TopDesEnd