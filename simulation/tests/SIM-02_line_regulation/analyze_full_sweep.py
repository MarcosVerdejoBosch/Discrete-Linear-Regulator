"""Validate all six completed transient steps before reporting line sensitivity."""
from pathlib import Path
import hashlib,json,re,shutil
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
stem=ROOT/'simulation/ltspice/SIM-02_full_line_5V'
logbytes=stem.with_suffix('.log').read_bytes()
log=logbytes.decode('utf-16-le' if logbytes[1]==0 else 'cp1252')
if 'Total elapsed time:' not in log: raise SystemExit('Sweep still running; results not final.')
b=stem.with_suffix('.raw').read_bytes()
marker='Binary:\n'.encode('utf-16-le'); pos=b.find(marker)
if pos<0: marker='Binary:\r\n'.encode('utf-16-le'); pos=b.find(marker)
assert pos>=0
h=b[:pos].decode('utf-16-le'); nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1])
names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
dtype=np.dtype([('t','<f8'),('v','<f4',(nv-1,))])
d=np.frombuffer(b[pos+len(marker):],dtype=dtype); t=d['t']
edges=np.r_[0,np.where(np.diff(t)<0)[0]+1,len(t)]
assert len(edges)==7, edges
results=[]
for vin,lo,hi in zip(range(6,12),edges[:-1],edges[1:]):
 time=t[lo:hi]; vals=d['v'][lo:hi].astype(float)
 assert time[-1]>=.07999
 signals=dict(zip(names[1:],vals.T))
 def avg(v,a,b):
  mask=(time>a)&(time<b); x=np.r_[a,time[mask],b]
  y=np.r_[np.interp(a,time,v),v[mask],np.interp(b,time,v)]
  return float(np.trapezoid(y,x)/(b-a))
 out=signals['V(out)']; m=(time>=.07)&(time<=.08)
 row={'source_V':vin,'vout_avg_V':avg(out,.07,.08),
 'previous_window_avg_V':avg(out,.06,.07),
 'vout_pp_mV':float(np.ptp(out[m])*1000),
 'enable_min_V':float(signals['V(ttl)'][m].min()),
 'input_after_switch_avg_V':avg(signals['V(vbat)'],.07,.08),
 'iout_avg_A':avg(signals['I(Rload)'],.07,.08)}
 row['window_drift_mV']=1000*(row['vout_avg_V']-row['previous_window_avg_V'])
 results.append(row)
dest=HERE/'results/full_circuit'; dest.mkdir(exist_ok=True)
summary={'mode':'5 V','load_ohm':5,'temperature_C':27,'averaging_window_s':[.07,.08],
 'results':results,
 'endpoint_slope_mV_per_V':1000*(results[-1]['vout_avg_V']-results[0]['vout_avg_V'])/5,
 'note':'Input axis is source VBAT before series switch; compare saved downstream input separately.'}
(dest/'sweep_metrics.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest=[]
for ext in ['.asc','.net','.log','.raw']:
 p=stem.with_suffix(ext); dst=dest/p.name; shutil.copy2(p,dst)
 manifest.append({'file':dst.name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(dest/'sweep_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(summary,indent=2))
