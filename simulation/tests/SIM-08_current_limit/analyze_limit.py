from pathlib import Path
import re,json,hashlib,shutil,argparse,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated'
a=argparse.ArgumentParser();a.add_argument('action',choices=['progress','analyze','plot']);args=a.parse_args()
def read(p):
 b=p.read_bytes();m='Binary:\n'.encode('utf-16-le');k=b.find(m)
 if k<0:m='Binary:\r\n'.encode('utf-16-le');k=b.find(m)
 assert k>=0
 h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()];dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(m):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
 return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
def avg(t,y,a,b):
 m=(t>a)&(t<b);x=np.r_[a,t[m],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
all_data={};result={}
for mode in ['5V','33V']:
 stem=R/f'simulation/ltspice/SIM-08_calibrated_limit_{mode}';t,v=read(stem.with_suffix('.raw'));all_data[mode]=(t,v);print(mode,t[-1],list(v))
 if args.action!='analyze':continue
 lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252');assert 'Total elapsed time:' in log and t[-1]>=.209999
 assert np.all(np.diff(t)>=0)
 plateaus={}
 for name,a,b in [('initial',.07,.08),('overload',.1,.11),('recovered_overload',.13,.14),('short',.16,.17),('final',.20,.21)]:
  m=(t>=a)&(t<=b);p={'window_s':[a,b]}
  for key in ['V(out)','I(Rload)','I(R25)','V(n020)','V(n060)','V(ttl)','V(vctrl)']:
   y=v[key];p[key]={'mean':avg(t,y,a,b),'min':float(y[m].min()),'max':float(y[m].max()),'half_window_drift':avg(t,y,(a+b)/2,b)-avg(t,y,a,(a+b)/2)}
  plateaus[name]=p
 events=[]
 for name,e,end in [('overload',.08,.11),('overload_release',.11,.14),('short',.14,.17),('short_release',.17,.21)]:
  m=(t>=e)&(t<end);x=t[m];y=v['V(out)'][m];ref=avg(t,v['V(out)'],end-.01,end);outside=np.flatnonzero(abs(y-ref)>.01*ref)
  settle=None
  if len(outside) and outside[-1]<len(x)-1:
   j=outside[-1];bound=ref+np.sign(y[j]-ref)*.01*ref;settle=float((x[j]+(bound-y[j])/(y[j+1]-y[j])*(x[j+1]-x[j])-e)*1e3)
  elif not len(outside):settle=0.
  events.append(dict(event=name,edge_s=e,voltage_min=float(y.min()),voltage_max=float(y.max()),load_peak_A=float(v['I(Rload)'][m].max()),sense_peak_A=float((-v['I(R25)'][m]).max()),settling_1pct_ms=settle))
 r=dict(plateaus=plateaus,events=events,enable_min_after_70ms=float(v['V(ttl)'][t>=.07].min()),manifest=[])
 for ext in ['asc','net','log','raw']:
  f=stem.with_suffix('.'+ext);shutil.copy2(f,D/f.name);r['manifest'].append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 m=t>=.07;keys=list(v);np.savetxt(D/f'{mode}_signals.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]),delimiter=',',header=','.join(['time_s']+keys),comments='');result[mode]=r
if args.action=='analyze':
 (D/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
elif args.action=='plot':
 os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(2,2,figsize=(6.5,4.5),sharex=True)
 fig.subplots_adjust(left=.105,right=.98,bottom=.12,top=.88,hspace=.15,wspace=.27)
 for col,(mode,color,title) in enumerate([('5V','#0072B2','(a) 5 V mode'),('33V','#009E73','(b) 3.3 V mode')]):
  t,v=all_data[mode];m=t>=.075;x=t[m]*1000
  axes[0,col].set_title(title,loc='left',fontsize=9)
  axes[0,col].text(95,.94,'Overload',ha='center',va='top',fontsize=7,transform=axes[0,col].get_xaxis_transform())
  axes[0,col].text(155,.94,'Short',ha='center',va='top',fontsize=7,transform=axes[0,col].get_xaxis_transform())
  axes[0,col].plot(x,v['V(out)'][m],color=color)
  axes[1,col].plot(x,v['I(Rload)'][m],color=color,label='Load current')
  axes[1,col].plot(x,-v['I(R25)'][m],color='#D55E00',ls='--',label='Sense-resistor current')
  for row in range(2):
   ax=axes[row,col];ax.axvspan(80,110,color='0.94',zorder=0);ax.axvspan(140,170,color='0.87',zorder=0);ax.set_xlim(75,210)
  axes[1,col].set_xlabel('Time (ms)')
 axes[0,0].set_ylabel('Output voltage (V)');axes[1,0].set_ylabel('Current (A)')
 handles,labels=axes[1,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,bbox_to_anchor=(.5,1),fontsize=8)
 for ext in ['pdf','svg','png']:fig.savefig(R/f'docs/figures/SIM-08_calibrated_limit.{ext}',dpi=300)
 plt.close(fig)
 (D/'figure_manifest.json').write_text(json.dumps(dict(processing='Original samples; no smoothing. Shading: overload 80-110ms; 50mohm short 140-170ms. Sense current is -I(R25), toward load.',metrics_sha256=hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),matplotlib=matplotlib.__version__),indent=2))
