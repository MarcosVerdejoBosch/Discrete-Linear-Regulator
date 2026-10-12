"""Prepare a full-circuit transient pilot without altering the SIM-01 baseline."""
from pathlib import Path
import hashlib, json, re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
source=ROOT/'simulation/ltspice/SIM-01_startup_shutdown_5V.asc'
text=source.read_bytes().decode('cp1252')
def value(instance, new):
    global text
    chunks=text.split('SYMBOL ')
    hits=0
    for i, chunk in enumerate(chunks):
        if re.search(r'^SYMATTR InstName '+re.escape(instance)+r'\s*$',chunk,re.M):
            chunks[i], count=re.subn(r'^SYMATTR Value [^\r\n]*', 'SYMATTR Value '+new,chunk, flags=re.M)
            assert count==1; hits+=1
    assert hits==1
    text='SYMBOL '.join(chunks)
value('VBAT','{VINTEST}')
value('V1','PWL(0 0 5m 0 5.001m 5)')
text=text.replace('.param RLOADVAL=50','.param RLOADVAL=5')
assert '.tran 0 140m 0 1u' in text
text=text.replace('.tran 0 140m 0 1u','.tran 0 80m 0 2u')
directives=[
 '.param VINTEST=8', '.temp 27',
 '.save V(VBAT) V(VCTRL) V(OUT) V(TTL) V(COMP) V(VREF) I(RLOAD)',
 '.meas tran VOUT_AVG AVG V(OUT) FROM 70m TO 80m',
 '.meas tran VOUT_MIN MIN V(OUT) FROM 70m TO 80m',
 '.meas tran VOUT_MAX MAX V(OUT) FROM 70m TO 80m',
 '.meas tran ENABLE_MIN MIN V(TTL) FROM 70m TO 80m',
 '.meas tran IOUT_AVG AVG I(RLOAD) FROM 70m TO 80m',
]
text+='\nTEXT -2424 1700 Left 2 !'+'\\n'.join(directives)+'\n'
target=ROOT/'simulation/ltspice/SIM-02_full_line_5V_pilot.asc'
target.write_bytes(text.encode('cp1252'))
sweep=ROOT/'simulation/ltspice/SIM-02_full_line_5V.asc'
sweep.write_bytes(text.replace('.param VINTEST=8','.step param VINTEST 6 11 1').encode('cp1252'))
(HERE/'results/full_circuit').mkdir(parents=True,exist_ok=True)
(HERE/'results/full_circuit/preparation.json').write_text(json.dumps({
 'baseline':source.relative_to(ROOT).as_posix(),
 'baseline_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'test':target.relative_to(ROOT).as_posix(),
 'test_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'changes':['Input parameter VINTEST=8 V', 'Load 5 ohm',
 'Switch connects at 5 ms and remains on', 'Transient 80 ms, maximum step 2 us',
 'Save selected signals; measure final 10 ms; temperature 27 C'],
 'status':'Pilot prepared; not yet validated. No topology or device-model changes.'
},indent=2)+'\n',encoding='utf-8')
print(target)
