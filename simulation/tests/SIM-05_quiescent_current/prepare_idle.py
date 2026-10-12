from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';D.mkdir(parents=True,exist_ok=True);manifest=[]
for mode in ['5V','33V']:
 p=R/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc';s=p.read_bytes().decode('cp1252');assert s.count('.param RLOADVAL=')==1
 import re
 s=re.sub(r'\.param RLOADVAL=[^\\\r\n]*','.param RLOADVAL=1Meg',s)
 s=s.replace('.tran 0 80m 0 2u','.tran 0 120m 0 2u');s+='\nTEXT -2424 2000 Left 2 !.save I(VBAT) I(V5) I(V10) I(V1) V(VDOBL)\n'
 q=R/f'simulation/ltspice/SIM-05_calibrated_idle_{mode}.asc';q.write_bytes(s.encode('cp1252'));manifest.append(dict(source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),test=q.name,test_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),source_V=8,temperature_C=27,external_load_ohm=1000000,duration_ms=120,max_step_us=2))
(D/'preparation.json').write_text(json.dumps(manifest,indent=2))
