"""Full-circuit 5 V protection cycle, without altering protection component values."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE/'results/calibrated';DEST.mkdir(parents=True,exist_ok=True)
source=ROOT/'simulation/ltspice/SIM-02_cal_02_5V.asc';s=source.read_bytes().decode('cp1252')
wave='PWL(0 8 80m 8 112m 4.8 122m 4.8 194m 12 204m 12 244m 8 264m 8)'
assert s.count('SYMATTR Value {VINTEST}')==1
s=s.replace('SYMATTR Value {VINTEST}','SYMATTR Value '+wave).replace('.tran 0 80m 0 2u','.tran 0 264m 0 2u')
old='.save V(VBAT) V(VCTRL) V(OUT) V(TTL) V(COMP) V(VREF) I(RLOAD)'
assert old in s
s=s.replace(old,old+' V(VEE) V(1) V(2) V(LDO_2) V(N086) V(N085) V(N034)')
target=ROOT/'simulation/ltspice/SIM-07_calibrated_protection_5V.asc';target.write_bytes(s.encode('cp1252'))
record={'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'test':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'mode_V':5,'load_ohm':5,'temperature_C':27,'source_waveform':wave,'ramp_V_per_ms':.1,'duration_ms':264,'max_step_us':2,'nodes':{'VEE':'Supply sensed by protection dividers, after input switch and reverse-polarity MOSFET','VBAT':'After input switch, before reverse-polarity MOSFET','N034':'Ideal source, terminal of VBAT source; verify netlist mapping','1':'UVLO permission, U15 output','2':'OVLO permission, U12 output','TTL':'Combined enable','LDO_2':'Time-delay permission','N086':'UVLO non-inverting input','N085':'OVLO inverting input','COMP':'Auxiliary protection reference'}}
(DEST/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
print(target)
