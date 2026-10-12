from pathlib import Path
import re,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';D.mkdir(parents=True,exist_ok=True)
p=R/'simulation/ltspice/SIM-02_cal_02_33V.asc';s=p.read_bytes().decode('cp1252');wave='PWL(0 8 80m 8 112m 4.8 122m 4.8)';s=s.replace('SYMATTR Value {VINTEST}','SYMATTR Value '+wave).replace('.tran 0 80m 0 2u','.tran 0 122m 0 2u');old='.save V(VBAT) V(VCTRL) V(OUT) V(TTL) V(COMP) V(VREF) I(RLOAD)';assert old in s;s=s.replace(old,old+' V(VEE) V(1) V(2) V(LDO_2) V(N034)')
target=R/'simulation/ltspice/SIM-04_calibrated_input_33V.asc';target.write_bytes(s.encode('cp1252'))
(D/'preparation.json').write_text(json.dumps(dict(source=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),test=target.name,test_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),reused_5V='SIM-07_calibrated_protection_5V: falling-input segment 80-112ms and hold to122ms',source_waveform=wave,load_ohm=3.3,max_step_us=2,temperature_C=27,protection='All circuitry active, no bypass'),indent=2))
