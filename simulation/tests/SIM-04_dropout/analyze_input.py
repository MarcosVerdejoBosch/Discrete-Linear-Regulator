from pathlib import Path
import re,json,hashlib,shutil,argparse,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';a=argparse.ArgumentParser();a.add_argument('action',choices=['progress','analyze','plot']);args=a.parse_args()
def read(p):
 b=p.read_bytes();m='Binary:\n'.encode('utf-16-le');k=b.find(m)
 if k<0:m='Binary:\r\n'.encode('utf-16-le');k=b.find(m)
 assert k>=0
 h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()];dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(m):];d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
 return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
all_data={};result={}
for mode,nom,stemname,endpoint in [('5V',5,'SIM-07_calibrated_protection_5V',.264),('33V',3.3,'SIM-04_calibrated_input_33V',.122)]:
 stem=R/f'simulation/ltspice/{stemname}';t,v=read(stem.with_suffix('.raw'));all_data[mode]=(t,v);print(mode,t[-1])
 if args.action!='analyze':continue
 lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252');assert 'Total elapsed time:' in log and t[-1]>=endpoint-1e-6
 def event(signal,level):
  s=signal-level;ii=np.flatnonzero((s[:-1]>=0)&(s[1:]<0)&(t[:-1]>.08)&(t[1:]<.112));assert len(ii)==1,ii;i=ii[0];tc=float(t[i]-s[i]/(s[i+1]-s[i])*(t[i+1]-t[i]));return dict(time_ms=tc*1000,bracket_us=(t[i+1]-t[i])*1e6,values={k:float(np.interp(tc,t,y)) for k,y in v.items()})
 events={'output_98pct':event(v['V(out)'],.98*nom),'delay_midpoint':event(v['V(ldo_2)'],.5*v['V(vee)']),'enable_midpoint':event(v['V(ttl)'],.5*v['V(vee)']),'uvlo_midpoint':event(v['V(1)'],.5*v['V(vee)'])}
 # Evaluate immediately before the delay transition; keep a 0.1 ms guard.
 pre=events['delay_midpoint']['time_ms']/1000-.0001;pv={k:float(np.interp(pre,t,y)) for k,y in v.items()}
 assert events['delay_midpoint']['time_ms']<events['enable_midpoint']['time_ms']<events['output_98pct']['time_ms']<events['uvlo_midpoint']['time_ms']
 assert abs(pv['V(out)']/nom-1)<.001
 row=dict(completed=True,events=events,pre_disable=dict(time_ms=pre*1000,values=pv),conclusion='Protection/enable shutdown precedes an observable intrinsic-dropout knee; output 98% crossing is a dynamic system event.',manifest=[])
 for ext in ['asc','net','log','raw']:
  f=stem.with_suffix('.'+ext)
  # Avoid duplicating the already archived 5 V raw file; reference its existing archive.
  if mode=='33V':shutil.copy2(f,D/f.name)
  row['manifest'].append(dict(file=str(f.relative_to(R)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 m=(t>=.08)&(t<=.122);keys=['V(n034)','V(vee)','V(vctrl)','V(out)','V(vref)','V(ttl)','V(ldo_2)','V(1)','I(Rload)'];np.savetxt(D/f'{mode}_falling_input.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]),delimiter=',',header=','.join(['time_s']+keys),comments='');result[mode]=row
if args.action=='analyze':
 (D/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:{'events':v['events'],'pre_disable':v['pre_disable']} for k,v in result.items()},indent=2))
elif args.action=='plot':
 met=json.loads((D/'metrics.json').read_text());os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(1,2,figsize=(6.5,2.8));fig.subplots_adjust(left=.10,right=.98,bottom=.23,top=.82,wspace=.28)
 for ax,(mode,nom,color,title) in zip(axes,[('5V',5,'#0072B2','(a) 5 V mode'),('33V',3.3,'#009E73','(b) 3.3 V mode')]):
  t,v=all_data[mode];m=(t>=.08)&(t<=.112);x=v['V(n034)'][m];ax.plot(x,v['V(out)'][m],color=color)
  ev=met[mode]['events']['output_98pct']['values'];xx=ev['V(n034)'];ax.axhline(.98*nom,color='.5',ls='--',lw=.7);ax.scatter(xx,.98*nom,s=14,color=color,zorder=5);ax.annotate(f'{xx:.3f} V',(xx,.98*nom),xytext=(12,-25),textcoords='offset points',fontsize=8)
  ax.set_title(title,fontsize=9,loc='left');ax.set_xlabel('Source voltage, falling (V)');ax.set_xlim(8,4.75);ax.set_ylim(-.12,nom*1.07)
 axes[0].set_ylabel('Output voltage (V)');fig.text(.54,.96,'Dashed line: 98% of nominal output',ha='center',va='top',fontsize=8)
 for ext in ['pdf','png','svg']:fig.savefig(R/f'docs/figures/SIM-04_calibrated_input.{ext}',dpi=300)
 plt.close(fig)
 (D/'figure_manifest.json').write_text(json.dumps(dict(metrics_sha256=hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),processing='Original samples from falling-source ramp. Reversed source axis follows time; no smoothing. Dashes mark 98% output criterion, not dropout.',matplotlib=matplotlib.__version__),indent=2))
