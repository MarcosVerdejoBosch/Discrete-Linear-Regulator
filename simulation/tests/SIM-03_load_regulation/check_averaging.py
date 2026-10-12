"""Audit recorded adaptive steps and averaging-window sensitivity of SIM-03.

Run from the full local evidence archive. This does not rerun LTspice and
does not establish independence from integration step or solver tolerance.
"""
from pathlib import Path
import hashlib,json,re
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2]
out={}
for mode in ['5V','33V']:
 p=R/f'simulation/ltspice/SIM-03_calibrated_load_{mode}.raw'
 b=p.read_bytes();mark='Binary:\n'.encode('utf-16-le');k=b.find(mark)
 if k<0:mark='Binary:\r\n'.encode('utf-16-le');k=b.find(mark)
 assert k>=0
 header=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',header)[1])
 names=[x.split()[1] for x in header.rsplit('Variables:',1)[1].splitlines() if x.strip()]
 dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(mark):]
 a=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
 t=a['t'];y=a['v'][:,names.index('V(out)')-1].astype(float)
 assert t[-1]>=.28-1e-8
 def avg(start,end):
  mask=(t>start)&(t<end);x=np.r_[start,t[mask],end]
  return float(np.trapezoid(np.interp(x,t,y),x)/(end-start))
 rows=[]
 for current,end in [(1,.08),(.1,.12),(.25,.16),(.5,.20),(.75,.24),(1,.28)]:
  mask=(t>=end-.01)&(t<=end);steps=np.diff(t[mask]);base=avg(end-.01,end)
  values={str(ms):avg(end-ms*.001,end) for ms in [2,5,10]}
  rows.append({'nominal_A':current,'end_ms':end*1000,'saved_samples_last_10ms':int(mask.sum()),'maximum_saved_step_ns':float(steps.max()*1e9),'median_saved_step_ns':float(np.median(steps)*1e9),'means_V_by_window_ms':values,'max_window_difference_from_10ms_uV':max(abs(v-base)*1e6 for v in values.values())})
 out[mode]={'raw_sha256':hashlib.sha256(b).hexdigest(),'scope':'Postprocessing of one completed 2 us maximum-step run. Window sensitivity and internal consistency only; not an independent timestep-convergence test.','windows':rows}
dest=H/'results/calibrated_load/averaging_check.json';dest.write_text(json.dumps(out,indent=2)+'\n')
for mode,v in out.items():
 print(mode,'max saved step ns',max(r['maximum_saved_step_ns'] for r in v['windows']),'minimum samples',min(r['saved_samples_last_10ms'] for r in v['windows']),'max averaging sensitivity uV',max(r['max_window_difference_from_10ms_uV'] for r in v['windows']))
