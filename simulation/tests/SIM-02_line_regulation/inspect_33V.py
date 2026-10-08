"""Verify completion and time-weighted selector-off pilot measurements."""
from pathlib import Path
import re, json, hashlib, shutil
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
stem=ROOT/'simulation/ltspice/SIM-02_full_line_33V_pilot'
b=stem.with_suffix('.raw').read_bytes()
marker='Binary:\n'.encode('utf-16-le'); pos=b.find(marker)
if pos<0: marker='Binary:\r\n'.encode('utf-16-le'); pos=b.find(marker)
assert pos>=0
h=b[:pos].decode('utf-16-le'); nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1])
names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]); body=b[pos+len(marker):]
d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
t=d['t']; print('Last saved time:',t[-1])
lb=stem.with_suffix('.log').read_bytes(); log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
if t[-1]<.07999 or 'Total elapsed time:' not in log: raise SystemExit('Incomplete run')
def avg(y,a,b):
    m=(t>a)&(t<b); x=np.r_[a,t[m],b]
    return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
stats={}
for j,n in enumerate(names[1:]):
    y=d['v'][:,j].astype(float); m=(t>=.07)&(t<=.08)
    stats[n]={'mean':avg(y,.07,.08),'min':float(y[m].min()),'max':float(y[m].max()),
              'change_from_previous_10ms':avg(y,.07,.08)-avg(y,.06,.07)}
dest=HERE/'results/full_circuit_33V'
(dest/'pilot_metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
manifest=[]
for ext in ['asc','net','log','raw']:
    p=stem.with_suffix('.'+ext); shutil.copy2(p,dest/p.name)
    manifest.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(dest/'pilot_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(stats,indent=2))
