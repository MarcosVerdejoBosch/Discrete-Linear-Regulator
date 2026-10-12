"""Inspect completed transient runs, extract peaks/settling, and plot original samples."""
from pathlib import Path
import argparse,json,hashlib,shutil,re,os,csv
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE/'results/calibrated';DEST.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('action',choices=['progress','analyze','plot']);args=p.parse_args()
def read(path):
    b=path.read_bytes();m='Binary:\n'.encode('utf-16-le');k=b.find(m)
    if k<0:m='Binary:\r\n'.encode('utf-16-le');k=b.find(m)
    assert k>=0
    h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
    dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(m):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
    return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
def avg(t,y,a,b):
    m=(t>a)&(t<b);x=np.r_[a,t[m],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
all_data={};result={}
for mode in ['5V','33V']:
    stem=ROOT/f'simulation/ltspice/SIM-06_calibrated_transient_{mode}'
    t,v=read(stem.with_suffix('.raw'));print(mode,'last time',t[-1]);all_data[mode]=(t,v)
    if args.action!='analyze':continue
    lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
    assert 'Total elapsed time:' in log and t[-1]>=.159999,'Incomplete run'
    assert np.all(np.diff(t)>=0)
    refs=[avg(t,v['V(out)'],a,b) for a,b in [(.07,.08),(.11,.12),(.15,.16)]]
    currents=[avg(t,v['I(Rload)'],a,b) for a,b in [(.07,.08),(.11,.12),(.15,.16)]]
    edges=[]
    for j,(name,e,end) in enumerate([('step_up',.08,.12),('step_down',.12,.16)]):
        ref=refs[j+1];mask=(t>=e)&(t<end);x=t[mask];y=v['V(out)'][mask]
        assert len(x)>100
        lo=int(np.argmin(y));hi=int(np.argmax(y));band=.01*ref
        outside=np.flatnonzero(np.abs(y-ref)>band)
        if len(outside):
            last=int(outside[-1]);assert last<len(x)-1,'Output did not settle within the observation interval'
            # Interpolate the last inward crossing of the relevant band edge.
            boundary=ref+np.sign(y[last]-ref)*band
            crossing=x[last]+(boundary-y[last])/(y[last+1]-y[last])*(x[last+1]-x[last])
            settling=(crossing-e)*1e6
            settled_sample=(x[last+1]-e)*1e6
        else:settling=0.;settled_sample=0.
        fine=(t[:-1]>=e-9e-6)&(t[1:]<=e+199e-6)
        maxdt=float(np.diff(t)[fine].max()*1e9);assert maxdt<=20.1,(mode,name,maxdt)
        assert settling<190,'Refinement window must be extended before reporting settling'
        enable=float(v['V(ttl)'][mask].min());assert enable>5
        r={'direction':name,'edge_s':e,'reference_V':ref,'initial_mean_V':refs[j],
           'current_before_A':currents[j],'current_after_A':currents[j+1],
           'minimum_V':float(y[lo]),'maximum_V':float(y[hi]),
           'undershoot_mV':max(0.,float((ref-y[lo])*1000)),
           'overshoot_mV':max(0.,float((y[hi]-ref)*1000)),
           'minimum_time_us':float((x[lo]-e)*1e6),'maximum_time_us':float((x[hi]-e)*1e6),
           'settling_1pct_us':float(settling),'first_settled_sample_us':float(settled_sample),
           'max_fine_step_ns':maxdt,'enable_min_V':enable,
           'final_window_drift_uV':1e6*(avg(t,v['V(out)'],end-.01,end)-avg(t,v['V(out)'],end-.02,end-.01))}
        assert abs(r['final_window_drift_uV'])<1
        edges.append(r)
        # Export original samples around the edge; no interpolation or smoothing.
        m=(t>=e-10e-6)&(t<=e+200e-6)
        np.savetxt(DEST/f'{mode}_{name}.csv',np.column_stack([(t[m]-e)*1e6,v['V(out)'][m],v['I(Rload)'][m]]),delimiter=',',header='time_relative_us,vout_V,load_A',comments='')
    r={'all_completed':True,'edges':edges,'return_low_load_difference_uV':1e6*(refs[-1]-refs[0]),'manifest':[]}
    for ext in ['asc','net','log','raw']:
        f=stem.with_suffix('.'+ext);shutil.copy2(f,DEST/f.name);r['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    result[mode]=r
if args.action=='analyze':
    (DEST/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{a:b for a,b in v.items() if a!='manifest'} for k,v in result.items()},indent=2))
elif args.action=='plot':
    result=json.loads((DEST/'metrics.json').read_text())
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.style.use(ROOT/'simulation/plotting/report.mplstyle')
    fig,axes=plt.subplots(3,2,figsize=(6.5,5.8),sharex='col',gridspec_kw={'height_ratios':[1,1,.7]})
    fig.subplots_adjust(left=.12,right=.98,bottom=.1,top=.93,hspace=.22,wspace=.25)
    maximum=max(e['settling_1pct_us'] for r in result.values() for e in r['edges'])
    xmax=max(25.,float(np.ceil(maximum*1.5/5)*5));assert xmax<190
    for col,(edge,title) in enumerate([(.08,'(a) Load increase'),(.12,'(b) Load decrease')]):
        axes[0,col].set_title(title,fontsize=9,loc='left')
        for row,(mode,color,label) in enumerate([('5V','#0072B2','5 V mode'),('33V','#009E73','3.3 V mode')]):
            t,v=all_data[mode];ref=result[mode]['edges'][col]['reference_V'];m=(t>=edge-3e-6)&(t<=edge+xmax*1e-6)
            x=(t[m]-edge)*1e6;ax=axes[row,col]
            ax.axhspan(ref*.99,ref*1.01,color='0.94',zorder=0)
            ax.axhline(ref,color='0.45',lw=.6,ls='--')
            ax.plot(x,v['V(out)'][m],color=color,label=label)
            if col==0:ax.set_ylabel(label+'\nOutput voltage (V)')
            axes[2,col].plot(x,v['I(Rload)'][m],color=color,label=label)
        axes[2,col].set_xlabel('Time from load change ('+r'$\mu$'+'s)')
        axes[2,col].set_xlim(-3,xmax)
    axes[2,0].set_ylabel('Load current (A)');axes[2,1].legend(loc='best',fontsize=7)
    for ext in ['pdf','svg','png']:fig.savefig(ROOT/f'docs/figures/SIM-06_calibrated_transient.{ext}',dpi=300)
    plt.close(fig)
    (DEST/'figure_manifest.json').write_text(json.dumps({'source':'metrics.json','sha256':hashlib.sha256((DEST/'metrics.json').read_bytes()).hexdigest(),'matplotlib':matplotlib.__version__,'processing':'Original raw samples, no smoothing or fitting; time relative to start of conductance transition; shaded band +/-1% of final mean; dashed line final mean.'},indent=2)+'\n')
