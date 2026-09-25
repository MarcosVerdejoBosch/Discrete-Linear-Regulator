"""Prepare and inspect shared-divider calibration of both selector states."""
from pathlib import Path
import argparse,re,json,hashlib,shutil
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','inspect']);p.add_argument('iteration');p.add_argument('--r33',type=float);p.add_argument('--rfb2',type=float);args=p.parse_args()
dest=HERE/'results/calibration'/args.iteration;dest.mkdir(parents=True,exist_ok=True)
results={}
for mode in ['5V','33V']:
    stem=ROOT/f'simulation/ltspice/SIM-02_cal_{args.iteration}_{mode}'
    if args.action=='prepare':
        source=ROOT/f'simulation/ltspice/SIM-02_full_line_{mode}_pilot.asc'
        s=source.read_bytes().decode('cp1252');chunks=s.split('SYMBOL ')
        for name,value in [('R33',args.r33),('RFB2',args.rfb2)]:
            assert value is not None
            count=0
            for i,c in enumerate(chunks):
                if re.search(r'^SYMATTR InstName '+name+r'\s*$',c,re.M):
                    chunks[i],n=re.subn(r'^SYMATTR Value [^\r\n]*','SYMATTR Value '+str(value),c,flags=re.M);assert n==1;count+=1
            assert count==1
        stem.with_suffix('.asc').write_bytes('SYMBOL '.join(chunks).encode('cp1252'))
        print(stem.with_suffix('.asc'))
        results[mode]={'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'R33_ohm':args.r33,'RFB2_ohm':args.rfb2}
    else:
        lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
        if 'Total elapsed time:' not in log: print(mode,'incomplete');continue
        b=stem.with_suffix('.raw').read_bytes();m='Binary:\n'.encode('utf-16-le');pos=b.find(m)
        if pos<0:m='Binary:\r\n'.encode('utf-16-le');pos=b.find(m)
        assert pos>=0
        h=b[:pos].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
        d=np.frombuffer(b[pos+len(m):],dtype=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]));t=d['t'];assert t[-1]>=.07999
        def avg(y,a,z):
            mask=(t>a)&(t<z);x=np.r_[a,t[mask],z];return float(np.trapezoid(np.interp(x,t,y),x)/(z-a))
        v=dict(zip(names[1:],d['v'].astype(float).T));y=v['V(out)'];mask=(t>=.07)&(t<=.08)
        result={'mean_V':avg(y,.07,.08),'pp_mV':float(np.ptp(y[mask])*1000),'drift_mV':1000*(avg(y,.07,.08)-avg(y,.06,.07)),'enable_min_V':float(v['V(ttl)'][mask].min()),'load_A':avg(v['I(Rload)'],.07,.08)}
        assert result['enable_min_V']>5 and abs(result['drift_mV'])<.001
        result['manifest']=[]
        for ext in ['asc','net','log','raw']:
            f=stem.with_suffix('.'+ext);shutil.copy2(f,dest/f.name);result['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
        results[mode]=result; print(mode,json.dumps({k:v for k,v in result.items() if k!='manifest'}))
if results:
    (dest/('preparation.json' if args.action=='prepare' else 'metrics.json')).write_text(json.dumps(results,indent=2)+'\n')
