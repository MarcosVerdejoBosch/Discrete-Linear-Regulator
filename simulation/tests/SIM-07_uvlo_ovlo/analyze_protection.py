"""Extract protection-comparator and system-enable events independently."""
from pathlib import Path
import argparse,re,json,hashlib,shutil,os
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE/'results/calibrated'
p=argparse.ArgumentParser();p.add_argument('action',choices=['progress','analyze','plot']);args=p.parse_args()
stem=ROOT/'simulation/ltspice/SIM-07_calibrated_protection_5V'
b=stem.with_suffix('.raw').read_bytes();marker='Binary:\n'.encode('utf-16-le');k=b.find(marker)
if k<0:marker='Binary:\r\n'.encode('utf-16-le');k=b.find(marker)
assert k>=0
h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(marker):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
t=d['t'];v=dict(zip(names[1:],d['v'].astype(float).T));print('Saved time',t[-1])
def avg(y,a,z):
    m=(t>a)&(t<z);x=np.r_[a,t[m],z];return float(np.trapezoid(np.interp(x,t,y),x)/(z-a))
if args.action=='analyze':
    lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
    assert 'Total elapsed time:' in log and t[-1]>=.263999,'Incomplete run'
    assert np.all(np.diff(t)>=0)
    channels={'uvlo':'V(1)','ovlo':'V(2)','delay':'V(ldo_2)','enable':'V(ttl)'}
    events={}
    for key,name in channels.items():
        s=v[name]-.5*v['V(vee)'];ix=np.flatnonzero(((s[:-1]>=0)!=(s[1:]>=0))&(t[:-1]>=.07))
        events[key]=[]
        for i in ix:
            tc=float(t[i]-s[i]/(s[i+1]-s[i])*(t[i+1]-t[i]))
            r={'edge':'rising' if s[i+1]>s[i] else 'falling','time_ms':tc*1000,
               'sensed_supply_V':float(np.interp(tc,t,v['V(vee)'])),
               'source_V':float(np.interp(tc,t,v['V(n034)'])),
               'input_after_switch_V':float(np.interp(tc,t,v['V(vbat)'])),
               'vout_V':float(np.interp(tc,t,v['V(out)'])),
               'reference_V':float(np.interp(tc,t,v['V(comp)'])),
               'bracket_dt_us':float((t[i+1]-t[i])*1e6),
               'bracket_supply_V':[float(v['V(vee)'][i]),float(v['V(vee)'][i+1])],
               'other_controls_above_half_supply':{c:bool(np.interp(tc,t,v[n]-.5*v['V(vee)'])>0) for c,n in channels.items() if c!=key}}
            events[key].append(r)
    plateau={}
    for label,a,z in [('initial',.07,.08),('undervoltage_hold',.115,.122),('overvoltage_hold',.197,.204),('final',.254,.264)]:
        m=(t>=a)&(t<=z);plateau[label]={n:avg(v[n],a,z) for n in ['V(out)','V(vee)','V(comp)','V(ttl)','I(Rload)']}
        plateau[label]['output_pp_mV']=float(np.ptp(v['V(out)'][m])*1000)
    result={'completed':True,'events':events,'plateaus':plateau,'threshold_definition':'Comparator output crossing 50% of local VEE; linearly interpolated samples; dynamic test at source ramp 0.1 V/ms; events before 70 ms excluded.'}
    if len(events['uvlo'])==2 and len(events['ovlo'])==2:
        uv={r['edge']:r['sensed_supply_V'] for r in events['uvlo']};ov={r['edge']:r['sensed_supply_V'] for r in events['ovlo']}
        result['thresholds_V']={'uvlo_enable_rising':uv['rising'],'uvlo_disable_falling':uv['falling'],'uvlo_hysteresis':uv['rising']-uv['falling'],
            'ovlo_disable_rising':ov['falling'],'ovlo_enable_falling':ov['rising'],'ovlo_hysteresis':ov['falling']-ov['rising']}
    result['manifest']=[]
    for ext in ['asc','net','log','raw']:
        f=stem.with_suffix('.'+ext);shutil.copy2(f,DEST/f.name);result['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    (DEST/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savetxt(DEST/'signals.csv',np.column_stack([t]+[v[n] for n in ['V(vee)','V(n034)','V(out)','V(1)','V(2)','V(ldo_2)','V(ttl)','V(comp)']]),delimiter=',',header='time_s,sensed_supply_V,source_V,vout_V,uvlo_permission_V,ovlo_permission_V,delay_permission_V,enable_V,protection_reference_V',comments='')
    print(json.dumps({a:b for a,b in result.items() if a!='manifest'},indent=2))
elif args.action=='plot':
    result=json.loads((DEST/'metrics.json').read_text());assert result['completed']
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.style.use(ROOT/'simulation/plotting/report.mplstyle')
    fig,axes=plt.subplots(2,2,figsize=(6.5,4.6),sharex='col',gridspec_kw={'height_ratios':[1.3,1]})
    fig.subplots_adjust(left=.11,right=.98,bottom=.2,top=.88,hspace=.15,wspace=.28)
    for col,(key,window,title) in enumerate([('uvlo',(.075,.15),'(a) Undervoltage cycle'),('ovlo',(.16,.264),'(b) Overvoltage cycle')]):
        m=(t>=window[0])&(t<=window[1]);x=t[m]*1000
        axes[0,col].plot(x,v['V(vee)'][m],color='#666666',ls='--',label='Protection input')
        axes[0,col].plot(x,v['V(out)'][m],color='#009E73',label='Output')
        axes[0,col].set_title(title,fontsize=9,loc='left')
        for j,r in enumerate(result['events'][key]):
            axes[0,col].scatter(r['time_ms'],r['sensed_supply_V'],color='#0072B2',s=12,zorder=5)
            axes[0,col].annotate(f"{r['sensed_supply_V']:.3f} V",(r['time_ms'],r['sensed_supply_V']),xytext=(-4,8 if j==0 else 18),textcoords='offset points',ha='center',fontsize=7)
        node='V(1)' if key=='uvlo' else 'V(2)'
        for n,color,ls,label in [(node,'#0072B2','-','Comparator output'),('V(ldo_2)','#CC79A7',':','Delay permission'),('V(ttl)','#D55E00','--','Enable')]:
            axes[1,col].plot(x,v[n][m]/v['V(vee)'][m],color=color,ls=ls,label=label)
        axes[1,col].set_xlabel('Time (ms)');axes[1,col].set_ylim(-.05,1.1);axes[1,col].set_xlim(window[0]*1000,window[1]*1000)
    handles,labels=axes[1,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.55,.01),ncol=3,fontsize=7)
    axes[0,0].set_ylabel('Voltage (V)');axes[1,0].set_ylabel('Control voltage / input')
    voltage_handles,voltage_labels=axes[0,0].get_legend_handles_labels()
    fig.legend(voltage_handles,voltage_labels,loc='upper center',bbox_to_anchor=(.55,1.0),ncol=2,fontsize=7)
    for ext in ['pdf','png','svg']:fig.savefig(ROOT/f'docs/figures/SIM-07_calibrated_protection.{ext}',dpi=300)
    plt.close(fig)
    (DEST/'figure_manifest.json').write_text(json.dumps({'source':'metrics.json','sha256':hashlib.sha256((DEST/'metrics.json').read_bytes()).hexdigest(),'matplotlib':matplotlib.__version__,'processing':'Original transient samples; control voltages normalized to actual protection supply; no smoothing. Markers indicate protection-comparator midpoint crossings, not system-enable thresholds.'},indent=2)+'\n')
