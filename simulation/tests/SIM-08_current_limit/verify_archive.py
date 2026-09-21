"""Recheck SIM-08 archived measurements without overwriting source results."""
from pathlib import Path
import ast,json,hashlib,re
import numpy as np
h=Path(__file__).resolve().parent;d=h/'results/calibrated';root=h.parents[2]
tree=ast.parse((h/'analyze_limit.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
metrics=json.loads((d/'metrics.json').read_text())
assert hashlib.sha256((d/'metrics.json').read_bytes()).hexdigest()==json.loads((d/'figure_manifest.json').read_text())['metrics_sha256']
review={'date':'2026-09-20','method':'Archived RAW reanalysis; no LTspice rerun','user_validation':'pending','hardware_validation':'pending','transient_peak_convergence':'not characterized','modes':{}}
for mode,stored in metrics.items():
 for entry in stored['manifest']:
  for folder in [d,root/'simulation/ltspice']:
   assert hashlib.sha256((folder/entry['file']).read_bytes()).hexdigest()==entry['sha256']
 stem=d/f'SIM-08_calibrated_limit_{mode}';b=stem.with_suffix('.log').read_bytes()
 assert 'Total elapsed time:' in b.decode('utf-16-le' if b[1]==0 else 'cp1252')
 t,v=read(stem.with_suffix('.raw'));assert t[-1]>=.209999 and np.all(np.diff(t)>=0)
 for label,p in stored['plateaus'].items():
  a,b=p['window_s'];mask=(t>=a)&(t<=b)
  for key,m in p.items():
   if key=='window_s':continue
   y=v[key];actual={'mean':avg(t,y,a,b),'min':float(y[mask].min()),'max':float(y[mask].max()),'half_window_drift':avg(t,y,(a+b)/2,b)-avg(t,y,a,(a+b)/2)}
   for k,z in actual.items():assert abs(z-m[k])<1e-10,(mode,label,key,k)
 for event,end in zip(stored['events'],[.11,.14,.17,.21]):
  start=event['edge_s'];sel=(t>=start)&(t<end)
  for key,val in {'load_peak_A':v['I(Rload)'][sel].max(),'sense_peak_A':(-v['I(R25)'][sel]).max(),'voltage_min':v['V(out)'][sel].min(),'voltage_max':v['V(out)'][sel].max()}.items():assert abs(val-event[key])<1e-10
 assert v['V(ttl)'][t>=.07].min()>7.09
 p=stored['plateaus'];recovery=(p['final']['V(out)']['mean']-p['initial']['V(out)']['mean'])*1e6;assert abs(recovery)<1
 review['modes'][mode]={'end_time_s':float(t[-1]),'archive_and_active_hashes_match':True,'overload_current_A':p['overload']['I(Rload)']['mean'],'short_current_A':p['short']['I(Rload)']['mean'],'short_output_V':p['short']['V(out)']['mean'],'final_output_V':p['final']['V(out)']['mean'],'return_difference_uV':recovery,'sampled_short_load_peak_A':stored['events'][2]['load_peak_A'],'sampled_short_sense_peak_A':stored['events'][2]['sense_peak_A']}
(d/'review_verification.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8');print(json.dumps(review,indent=2))
