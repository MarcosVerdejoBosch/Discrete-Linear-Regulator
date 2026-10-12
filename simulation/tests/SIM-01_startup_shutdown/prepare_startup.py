from pathlib import Path
import re,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';D.mkdir(parents=True,exist_ok=True)
records=[]
for mode,load,nom in [('5V',50,5),('33V',33,3.3)]:
 p=R/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc';s=p.read_bytes().decode('cp1252')
 assert s.count('PWL(0 0 5m 0 5.001m 5)')==1
 s=s.replace('PWL(0 0 5m 0 5.001m 5)','PWL(0 0 5m 0 5.001m 5 55m 5 55.001m 0 85m 0 85.001m 5)')
 s=s.replace('.tran 0 80m 0 2u','.tran 0 140m 0 2u')
 s=s.replace('SYMATTR InstName RLOAD\nSYMATTR Value {RLOADVAL}',f'SYMATTR InstName RLOAD\nSYMATTR Value R={nom}/table(time,0,0.1,140m,0.1)')
 s=re.sub(r'\.param RLOADVAL=[^\\\r\n]*',f'.param RLOADVAL={load}',s)
 # Remove old measurements: their 70--80 ms window is now powered off.
 s=re.sub(r'\\n\.meas[^\\\r\n]*','',s)
 s+='\nTEXT -2424 2100 Left 2 !.options plotwinsize=0\\n.save V(VEE) V(N034) I(VBAT)\n'
 q=R/f'simulation/ltspice/SIM-01_calibrated_startup_{mode}.asc';q.write_bytes(s.encode('cp1252'))
 fine=s.replace('.tran 0 140m 0 2u','.tran 0 140m 0 1u')+'\nTEXT -160 3400 Left 2 !.options trtol=1\n'
 (q.parent/f'SIM-01_check_step_{mode}.asc').write_bytes(fine.encode('cp1252'))
 records.append(dict(mode=mode,load_ohm=load,source_V=8,temperature_C=27,calibration='R33=14846.5 ohm; RFB2=28759.8 ohm',events_ms=[5,55,85],stop_ms=140,max_step_us=2,integration='default',solver='Normal (-norm command line)',load_representation='Behavioral resistance constant in time; electrically 50/33 ohm',source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scenario=q.name,scenario_sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
(D/'preparation.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
