"""Separate low-current dropout exploration, retaining all auxiliary circuits."""
from pathlib import Path
import re,json,hashlib
H=Path(__file__).resolve().parent; R=H.parents[2]; D=H/'results/adjusted';D.mkdir(parents=True,exist_ok=True)
manifest=[]
for mode,load,nom in [('5V',50,5),('33V',33,3.3)]:
 p=R/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc';s=p.read_bytes().decode('cp1252')
 for ref,old,new in [('R65','15k','47k'),('R70','75k','100k')]:
  pattern=f'SYMATTR InstName {ref}\nSYMATTR Value {old}';assert s.count(pattern)==1
  s=s.replace(pattern,f'SYMATTR InstName {ref}\nSYMATTR Value {new}')
 s=s.replace('SYMATTR Value {VINTEST}','SYMATTR Value PWL(0 8 80m 8 132m 2.8 142m 2.8)')
 s=s.replace('.tran 0 80m 0 2u','.tran 0 142m 0 2u')
 s=re.sub(r'\.param RLOADVAL=[^\\\r\n]*',f'.param RLOADVAL={load}',s)
 s=s.replace('SYMATTR InstName RLOAD\nSYMATTR Value {RLOADVAL}',f'SYMATTR InstName RLOAD\nSYMATTR Value R={nom}/table(time,0,0.1,142m,0.1)')
 s=re.sub(r'\\n\.meas[^\\\r\n]*','',s)
 s+='\nTEXT -2400 2200 Left 2 !.options trtol=1\\n.save V(N034) V(VEE) V(1) V(2) V(LDO_2) V(N008) V(N009) V(N036) V(N037) V(N038) V(N040) V(N088) V(N086) V(N089) V(N084) V(N025) V(N026) V(VDOBL) Ib(Q26) Ic(Q26) I(R25) I(R24) I(R72)\n'
 q=R/f'simulation/ltspice/SIM-04_adjusted_{mode}.asc';q.write_bytes(s.encode('cp1252'))
 manifest.append(dict(mode=mode,load_ohm=load,nominal_A=.1,source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),file=q.name,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),adjustments={'LTspice R65 / KiCad RV12':{'original_ohm':15000,'test_ohm':47000},'LTspice R70 / KiCad RV10':{'original_ohm':75000,'test_ohm':100000}},hardware_pot_ranges={'RV10_max_ohm':100000,'RV12_max_ohm':50000,'confirmed_by_user':True},source_ramp_V_per_ms=-.1,solver='Normal',trtol=1,max_step_us=2))
(D/'preparation.json').write_text(json.dumps(manifest,indent=2))
print('Prepared two adjusted scenarios; originals preserved.')
