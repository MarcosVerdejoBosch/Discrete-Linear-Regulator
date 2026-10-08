"""Inspect saved pilot samples; completion must also be confirmed in LTspice log."""
from pathlib import Path
import json, re
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
p=ROOT/'simulation/ltspice/SIM-02_full_line_5V_pilot.raw'
b=p.read_bytes(); marker='Binary:\n'.encode('utf-16-le'); pos=b.find(marker)
if pos<0:
 marker='Binary:\r\n'.encode('utf-16-le'); pos=b.find(marker)
assert pos>=0
h=b[:pos].decode('utf-16-le')
nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1])
names=[line.split()[1] for line in h.rsplit('Variables:',1)[1].splitlines() if line.strip()]
dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))])
body=b[pos+len(marker):]; count=len(body)//dt.itemsize
d=np.frombuffer(body[:count*dt.itemsize],dtype=dt)
t=d['t']; print('Saved samples',len(t),'last time',t[-1])
if t[-1] < .07999:
 raise SystemExit('Pilot is still incomplete')
stats={}
m=(t>=.070)&(t<=.080)
for j,n in enumerate(names[1:]):
 v=d['v'][:,j].astype(float)
 stats[n]={'min':float(v[m].min()),'max':float(v[m].max()),'last':float(v[-1])}
print(json.dumps(stats,indent=2))
(HERE/'results/full_circuit/pilot_sample_metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
