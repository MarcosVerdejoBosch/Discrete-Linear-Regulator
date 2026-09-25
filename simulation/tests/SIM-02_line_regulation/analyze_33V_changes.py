"""Check the high-input points obtained after startup at 8 V."""
from pathlib import Path
import re,json,shutil,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
stem=ROOT/'simulation/ltspice/SIM-02_full_line_33V_changes'
lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
if 'Total elapsed time:' not in log:raise SystemExit('Line-change run not complete')
b=stem.with_suffix('.raw').read_bytes();m='Binary:\n'.encode('utf-16-le');pos=b.find(m)
if pos<0:m='Binary:\r\n'.encode('utf-16-le');pos=b.find(m)
assert pos>=0
h=b[:pos].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1])
names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
d=np.frombuffer(b[pos+len(m):],dtype=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]))
t=d['t'];v=dict(zip(names[1:],d['v'].astype(float).T))
assert t[-1]>=.31999 and np.all(np.diff(t)>=0)
def avg(y,a,b):
 mask=(t>a)&(t<b);x=np.r_[a,t[mask],b]
 return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
rows=[]
for vin,a,end in [(8,.07,.08),(6,.11,.12),(7,.15,.16),(8,.19,.20),(9,.23,.24),(10,.27,.28),(11,.31,.32)]:
 mask=(t>=a)&(t<=end); out=v['V(out)']
 rows.append({'source_V':vin,'vout_avg_V':avg(out,a,end),
 'drift_mV':1000*(avg(out,a,end)-avg(out,a-.01,a)),
 'vout_pp_mV':float(np.ptp(out[mask])*1000),
 'enable_min_V':float(v['V(ttl)'][mask].min()),
 'input_after_switch_V':avg(v['V(vbat)'],a,end)})
dest=HERE/'results/full_circuit_33V';result={'all_steps_completed':True,'results':rows}
(dest/'line_change_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
manifest=[]
for ext in ['asc','net','log','raw']:
 p=stem.with_suffix('.'+ext);dst=dest/p.name;shutil.copy2(p,dst)
 manifest.append({'file':dst.name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(dest/'line_change_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
