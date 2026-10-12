from pathlib import Path
import runpy,sys,json,hashlib,shutil
import numpy as np
H=Path(__file__).resolve().parent;sys.argv=['analyze_startup.py','progress'];ns=runpy.run_path(str(H/'analyze_startup.py'));read=ns['read'];avg=ns['avg'];cross=ns['cross'];R=ns['R'];D=H/'results/calibrated';results={}
for mode,nom in [('5V',5),('33V',3.3)]:
 pairs=[];manifest=[]
 for prefix in ['calibrated_startup','check_step']:
  stem=R/f'simulation/ltspice/SIM-01_{prefix}_{mode}';t,v=read(stem.with_suffix('.raw'));b=stem.with_suffix('.log').read_bytes();log=b.decode('utf-16-le' if b[1]==0 else 'cp1252');assert t[-1]>=.068, 'The first-cycle comparison needs at least 68 ms'
  complete=bool('Total elapsed time:' in log and t[-1]>=.139999)
  assert complete, 'A full-cycle refinement check requires a completed 140 ms run'
  met={'mean_V':avg(t,v['V(out)'],.045,.055),'restart_mean_V':avg(t,v['V(out)'],.13,.14)}
  for origin,end,name in [(.005,.055,'first'),(.085,.14,'restart')]:
   e=cross(t,v['V(ttl)'],3.5,origin,end);q=cross(t,v['V(out)'],nom*.98,e,end);m=(t>=origin)&(t<e);met[name+'_enable_ms']=(e-origin)*1000;met[name+'_98pct_ms']=(q-origin)*1000;met[name+'_pulse_V']=float(v['V(out)'][m].max())
  for key,name in [('V(out)','out'),('V(vctrl)','vctrl')]:
   q=cross(t,v[key],.05,.055,.068,False);met[name+'_50mV_ms']=None if q is None else (q-.055)*1000
  pairs.append(met)
  if prefix=='check_step':
   for ext in ['asc','net','log','raw']:
    f=stem.with_suffix('.'+ext);shutil.copy2(f,D/f.name);manifest.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 delta={k:(None if pairs[0][k] is None or pairs[1][k] is None else pairs[1][k]-pairs[0][k]) for k in pairs[0]};results[mode]={'two_us':pairs[0],'one_us':pairs[1],'difference_one_minus_two':delta,'manifest':manifest,'comparison_scope_s':[0,.14],'fine_run_complete':complete,'refinement':'Normal solver, maximum step 1 us, explicit trtol=1. Both timestep and transient error control differ from nominal.'}
(D/'step_check.json').write_text(json.dumps(results,indent=2));print(json.dumps({m:x['difference_one_minus_two'] for m,x in results.items()},indent=2))
