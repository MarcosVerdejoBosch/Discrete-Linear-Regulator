"""Verify archived SIM-07 results without changing simulation data."""
from pathlib import Path
import ast, hashlib, json, re
import numpy as np
h=Path(__file__).resolve().parent; d=h/'results/calibrated'; root=h.parents[2]
tree=ast.parse((h.parent/'SIM-06_load_transient/analyze_transient.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'raw_helpers','exec'))
m=json.loads((d/'metrics.json').read_text())
for entry in m['manifest']:
 for folder in [d,root/'simulation/ltspice']:
  assert hashlib.sha256((folder/entry['file']).read_bytes()).hexdigest()==entry['sha256']
assert hashlib.sha256((d/'metrics.json').read_bytes()).hexdigest()==json.loads((d/'figure_manifest.json').read_text())['sha256']
stem=d/'SIM-07_calibrated_protection_5V';b=stem.with_suffix('.log').read_bytes()
assert 'Total elapsed time:' in b.decode('utf-16-le' if b[1]==0 else 'cp1252')
t,v=read(stem.with_suffix('.raw'));assert t[-1]>=.263999 and np.all(np.diff(t)>=0)
events={}
for key,node in {'uvlo':'V(1)','ovlo':'V(2)','delay':'V(ldo_2)','enable':'V(ttl)'}.items():
 y=v[node]-.5*v['V(vee)'];ix=np.flatnonzero((np.signbit(y[:-1])!=np.signbit(y[1:]))&(t[:-1]>=.07))
 assert len(ix)==len(m['events'][key])
 events[key]=[]
 for i,stored in zip(ix,m['events'][key]):
  tc=t[i]-y[i]*(t[i+1]-t[i])/(y[i+1]-y[i]);voltage=float(np.interp(tc,t,v['V(vee)']))
  assert abs(tc*1000-stored['time_ms'])<1e-8 and abs(voltage-stored['sensed_supply_V'])<1e-8
  events[key].append({'time_ms':float(tc*1000),'sensed_supply_V':voltage,'edge':stored['edge']})
for label,a,b in [('initial',.07,.08),('undervoltage_hold',.115,.122),('overvoltage_hold',.197,.204),('final',.254,.264)]:
 for node in ['V(out)','V(vee)','V(comp)','V(ttl)','I(Rload)']:
  assert abs(avg(t,v[node],a,b)-m['plateaus'][label][node])<1e-10
review={'date':'2026-09-20','method':'Archived RAW events and plateau means recalculated; no new LTspice run','end_time_s':float(t[-1]),'archive_and_active_hashes_match':True,'figure_metrics_hash_matches':True,'events':events,'user_validation':'pending','hardware_validation':'pending','scope':'5 V mode only, original protection settings, source slew 0.1 V/ms'}
(d/'review_verification.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print(json.dumps(review,indent=2))
