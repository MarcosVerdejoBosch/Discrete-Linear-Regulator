"""Inspect complete steps, explicitly retaining incomplete-run status."""
from pathlib import Path
import sys,json,re
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
name=sys.argv[1]; voltages=list(map(float,sys.argv[2:]))
p=ROOT/'simulation/ltspice'/name
b=p.with_suffix('.raw').read_bytes(); marker='Binary:\n'.encode('utf-16-le'); pos=b.find(marker)
if pos<0: marker='Binary:\r\n'.encode('utf-16-le');pos=b.find(marker)
assert pos>=0
h=b[:pos].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1])
names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
dtype=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[pos+len(marker):]
d=np.frombuffer(body[:len(body)//dtype.itemsize*dtype.itemsize],dtype=dtype)
edges=np.r_[0,np.where(np.diff(d['t'])<0)[0]+1,len(d)]
rows=[]
for vin,lo,hi in zip(voltages,edges[:-1],edges[1:]):
 t=d['t'][lo:hi];v=dict(zip(names[1:],d['v'][lo:hi].astype(float).T))
 if t[-1]<.07999:
  print('Incomplete',vin,'V, time',float(t[-1]));continue
 def avg(a,b):
  m=(t>a)&(t<b);x=np.r_[a,t[m],b];y=np.interp(x,t,v['V(out)'])
  return float(np.trapezoid(y,x)/(b-a))
 m=(t>=.07)&(t<=.08)
 rows.append({'source_V':vin,'vout_avg_V':avg(.07,.08),
  'drift_mV':1000*(avg(.07,.08)-avg(.06,.07)),
  'vout_pp_mV':float(np.ptp(v['V(out)'][m])*1000),
  'enable_min_V':float(v['V(ttl)'][m].min())})
logb=p.with_suffix('.log').read_bytes();log=logb.decode('utf-16-le' if logb[1]==0 else 'cp1252')
done='Total elapsed time:' in log and len(rows)==len(voltages)
result={'test':name,'all_steps_completed':done,'completed_steps':rows}
(HERE/'results/full_circuit'/ (name+'_inspection.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
