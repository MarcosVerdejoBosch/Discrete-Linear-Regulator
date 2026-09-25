from pathlib import Path
import re,json,hashlib
H=Path(__file__).resolve().parent; R=H.parents[2]; D=H/'results/calibrated';D.mkdir(parents=True,exist_ok=True)
a=[]
for mode,n in [('5V',5),('33V',3.3)]:
 p=R/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc'; s=p.read_bytes().decode('cp1252');c=s.split('SYMBOL ')
 for i,b in enumerate(c):
  if re.search(r'^SYMATTR InstName RLOAD\s*$',b,re.M):
   c[i]=re.sub(r'^SYMATTR Value [^\r\n]*',f'SYMATTR Value R=1/table(time,0,{1/n},80m,{1/n},80.01m,{2/n},110m,{2/n},110.01m,{1/n},140m,{1/n},140.01m,20,170m,20,170.01m,{1/n},210m,{1/n})',b,flags=re.M)
 s='SYMBOL '.join(c).replace('.tran 0 80m 0 2u','.tran 0 210m 0 2u')
 s+='\nTEXT -2424 2000 Left 2 !.save V(VEE) V(N020) V(N060) V(N057) I(R25) Ic(Q26)\n'
 target=R/f'simulation/ltspice/SIM-08_calibrated_limit_{mode}.asc';target.write_bytes(s.encode('cp1252'))
 a.append(dict(mode=mode,source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),test=target.name,input_V=8,temp_C=27,load_ohm=[n,n/2,n,.05,n],edge_ms=[80,110,140,170],conductance_transition_us=10,max_step_us=2,duration_ms=210))
(D/'preparation.json').write_text(json.dumps(a,indent=2))
