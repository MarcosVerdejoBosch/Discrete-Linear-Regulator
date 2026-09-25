from pathlib import Path
import argparse,re,json,hashlib,shutil,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';p=argparse.ArgumentParser();p.add_argument('action',choices=['progress','analyze','plot']);args=p.parse_args()
def read(p):
 b=p.read_bytes();m='Binary:\n'.encode('utf-16-le');k=b.find(m)
 if k<0:m='Binary:\r\n'.encode('utf-16-le');k=b.find(m)
 assert k>=0
 h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()];dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(m):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt);return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
def avg(t,y,a,b):
 m=(t>a)&(t<b);x=np.r_[a,t[m],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
all_data={};results={}
for mode in ['5V','33V']:
 stem=R/f'simulation/ltspice/SIM-05_calibrated_idle_{mode}';t,v=read(stem.with_suffix('.raw'));all_data[mode]=(t,v);print(mode,t[-1])
 if args.action!='analyze':continue
 lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252');assert 'Total elapsed time:' in log and t[-1]>=.119999
 met={}
 for key,y in v.items():
  m=(t>=.1)&(t<=.12);met[key]=dict(mean=avg(t,y,.1,.12),min=float(y[m].min()),max=float(y[m].max()),last_window_change=avg(t,y,.11,.12)-avg(t,y,.1,.11))
 ii=-met['I(Vbat)']['mean'];load=met['I(Rload)']['mean'];assert ii>0 and met['V(ttl)']['min']>5
 # Switching ripple gives endpoint-dependent partial-cycle averages.
 # Require agreement well inside the report resolution of 0.1 mA.
 window_means=[-avg(t,v['I(Vbat)'],aa,bb)*1000 for aa,bb in [(.08,.09),(.09,.1),(.1,.11),(.11,.12)]]
 assert max(window_means)-min(window_means)<.02,'Averaging uncertainty exceeds 0.02 mA'
 for source in ['I(V5)','I(V10)','I(V1)']:assert max(abs(met[source]['min']),abs(met[source]['max']))<1e-12,'Additional test source supplies current'
 assert abs(met['V(out)']['last_window_change'])<1e-4,'Output mean not settled'
 result=dict(signals=met,ten_ms_window_means_mA=window_means,input_current_mA=ii*1000,external_load_uA=load*1e6,input_minus_load_mA=(ii-load)*1000,input_power_mW=8*ii*1000,window_ms=[100,120],manifest=[])
 for ext in ['asc','net','log','raw']:
  f=stem.with_suffix('.'+ext);shutil.copy2(f,D/f.name);result['manifest'].append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 keys=list(v);m=t>=.09;np.savetxt(D/f'{mode}_settled.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]),delimiter=',',header=','.join(['time_s']+keys),comments='');results[mode]=result
if args.action=='analyze':
 (D/'metrics.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
elif args.action=='plot':
 met=json.loads((D/'metrics.json').read_text());os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(2,1,figsize=(6.5,4),sharex=True);fig.subplots_adjust(left=.13,right=.97,bottom=.14,top=.9,hspace=.12)
 for mode,col,label in [('5V','#0072B2','5 V mode'),('33V','#009E73','3.3 V mode')]:
  t,v=all_data[mode];m=(t>=.119)&(t<=.12);axes[0].plot(t[m]*1000,-v['I(Vbat)'][m]*1000,color=col,label=label);axes[1].plot(t[m]*1000,v['V(out)'][m],color=col)
 fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=2,bbox_to_anchor=(.55,1.0));axes[0].set_ylabel('Source current (mA)');axes[1].set_ylabel('Output voltage (V)');axes[1].set_xlabel('Time (ms)');axes[1].set_xlim(119,120)
 for ext in ['pdf','svg','png']:fig.savefig(R/f'docs/figures/SIM-05_calibrated_idle.{ext}',dpi=300)
 plt.close(fig)
 (D/'figure_manifest.json').write_text(json.dumps(dict(metrics_sha256=hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),processing='Original raw samples, no smoothing; input current is -I(VBAT).',matplotlib=matplotlib.__version__),indent=2))
