"""Complete calibrated regulator, resistive load transitions and local time refinement."""
from pathlib import Path
import re,json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE/'results/calibrated';DEST.mkdir(parents=True,exist_ok=True)
manifest=[]
for mode,nom in [('5V',5),('33V',3.3)]:
    source=ROOT/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc';s=source.read_bytes().decode('cp1252');chunks=s.split('SYMBOL ');hits=0
    for i,c in enumerate(chunks):
        if re.search(r'^SYMATTR InstName RLOAD\s*$',c,re.M):
            chunks[i],n=re.subn(r'^SYMATTR Value [^\r\n]*',f'SYMATTR Value R={nom}/table(time,0,0.1,80m,0.1,80.001m,1,120m,1,120.001m,0.1,160m,0.1)',c,flags=re.M);assert n==1;hits+=1
    assert hits==1
    s='SYMBOL '.join(chunks).replace('.tran 0 80m 0 2u','.tran 0 160m 0 2u')
    # Isolated numerical monitor: no connection to regulator nodes.
    s+='\nTEXT -2424 1900 Left 2 !BRES SIM06_TIMESTEP 0 V=table(time,0,0,79.99m,0,80.2m,210,119.99m,210,120.2m,420,160m,420) tripdv=0.001 tripdt=20n\n'
    target=ROOT/f'simulation/ltspice/SIM-06_calibrated_transient_{mode}.asc';target.write_bytes(s.encode('cp1252'))
    manifest.append({'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'test':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_V':8,'temperature_C':27,'nominal_load_A':[.1,1,.1],'edge_times_ms':[80,120],'conductance_transition_us':1,'duration_ms':160,'global_max_step_us':2,'local_tripdt_ns':20,'refinement_windows_ms':[[79.99,80.2],[119.99,120.2]],'changes':['RLOAD is a time-dependent positive resistance; nominal conductance ramps in 1 us','Duration extended to 160 ms','Isolated BRES controls numerical resolution only, no electrical connection to regulator']})
(DEST/'preparation.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared both calibrated transient tests.')
