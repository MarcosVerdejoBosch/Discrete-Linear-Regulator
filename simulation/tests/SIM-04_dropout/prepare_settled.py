"""Confirm the 5 V knee with fixed input holds, using the actual pot ranges."""
from pathlib import Path
import json, hashlib
H=Path(__file__).resolve().parent; R=H.parents[2]
D=H/'results/adjusted_settled'; D.mkdir(parents=True,exist_ok=True)
p=R/'simulation/ltspice/SIM-04_adjusted_5V.asc'
s=p.read_bytes().decode('cp1252')
old='PWL(0 8 80m 8 132m 2.8 142m 2.8)'
new='PWL(0 8 80m 8 100m 5.10 115m 5.10 116m 5.00 131m 5.00 132m 4.95 147m 4.95 148m 4.94 163m 4.94)'
assert s.count(old)==1
s=s.replace(old,new).replace('.tran 0 142m 0 2u','.tran 0 163m 0 2u')
q=R/'simulation/ltspice/SIM-04_adjusted_settled_5V.asc'
q.write_bytes(s.encode('cp1252'))
(D/'preparation.json').write_text(json.dumps({'source':p.name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scenario':q.name,'scenario_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'source_PWL':new,'hold_duration_ms':15,'average_final_ms':5,'load_ohm':50,'temperature_C':27,'max_step_us':2,'trtol':1,'solver':'Normal','changes':'Only source waveform and duration; RV10=100k, RV12=47k retained. No auxiliary source or bypass.'},indent=2))
print(q)
