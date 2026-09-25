"""Compare load endpoints with maximum timestep reduced from 2 to 1 us."""
from pathlib import Path
import json,re,hashlib,shutil
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE/'results/calibrated_load/stepcheck';DEST.mkdir(exist_ok=True)
def read(path):
    b=path.read_bytes();m='Binary:\n'.encode('utf-16-le');k=b.find(m)
    if k<0:m='Binary:\r\n'.encode('utf-16-le');k=b.find(m)
    assert k>=0
    h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
    dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(m):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
    return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
results={}
for mode in ['5V','33V']:
    stem=ROOT/f'simulation/ltspice/SIM-03_load_stepcheck_{mode}';t,v=read(stem.with_suffix('.raw'));print(mode,'time',t[-1])
    lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
    if t[-1]<.11999 or 'Total elapsed time:' not in log:raise SystemExit('Check incomplete')
    def avg(t,y,a,b):
        mask=(t>a)&(t<b);x=np.r_[a,t[mask],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
    original=ROOT/f'simulation/ltspice/SIM-03_calibrated_load_{mode}.raw';ot,ov=read(original)
    rows=[]
    for current,a,end in [(1,.07,.08),(.1,.11,.12)]:
        mean=avg(t,v['V(out)'],a,end);old=avg(ot,ov['V(out)'],a,end)
        rows.append({'nominal_A':current,'vout_V':mean,'load_A':avg(t,v['I(Rload)'],a,end),'difference_from_2us_uV':1e6*(mean-old),'drift_uV':1e6*(mean-avg(t,v['V(out)'],a-.01,a))})
    slope=1000*(rows[0]['vout_V']-rows[1]['vout_V'])/(rows[0]['load_A']-rows[1]['load_A'])
    r={'points':rows,'signed_slope_mV_per_A':slope,'manifest':[]}
    for ext in ['asc','net','log','raw']:
        f=stem.with_suffix('.'+ext);shutil.copy2(f,DEST/f.name);r['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    results[mode]=r
(DEST/'metrics.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({m:{k:v for k,v in r.items() if k!='manifest'} for m,r in results.items()},indent=2))
