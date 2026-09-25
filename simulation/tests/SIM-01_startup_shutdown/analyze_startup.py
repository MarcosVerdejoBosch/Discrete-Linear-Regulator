from pathlib import Path
import re,json,hashlib,shutil,sys,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/calibrated';D.mkdir(parents=True,exist_ok=True)
def read(p):
 b=p.read_bytes();mark='Binary:\n'.encode('utf-16-le');k=b.find(mark)
 if k<0:mark='Binary:\r\n'.encode('utf-16-le');k=b.find(mark)
 assert k>=0
 h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()];dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(mark):];a=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt);return a['t'],dict(zip(names[1:],a['v'].astype(float).T))
def avg(t,y,a,b):
 m=(t>a)&(t<b);x=np.r_[a,t[m],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
def cross(t,y,level,a,b,rising=True):
 m=(t>=a)&(t<=b);x=t[m];z=y[m]-level;ix=np.where((z[:-1]<0)&(z[1:]>=0) if rising else (z[:-1]>0)&(z[1:]<=0))[0]
 if not len(ix):return None
 i=ix[0];return float(x[i]-z[i]*(x[i+1]-x[i])/(z[i+1]-z[i]))
mode_action=sys.argv[1] if len(sys.argv)>1 else 'progress';all_data={};metrics={}
for mode,nom in [('5V',5),('33V',3.3)]:
 stem=R/f'simulation/ltspice/SIM-01_calibrated_startup_{mode}';t,v=read(stem.with_suffix('.raw'));all_data[mode]=(t,v);print(mode,'last_ms',t[-1]*1000)
 if mode_action!='analyze':continue
 b=stem.with_suffix('.log').read_bytes();log=b.decode('utf-16-le' if b[1]==0 else 'cp1252');assert 'Total elapsed time:' in log and t[-1]>=.139999
 out=v['V(out)'];enable=v['V(ttl)'];m=(t>=.045)&(t<=.055);assert enable[m].min()>5
 settled=avg(t,out,.045,.055);assert abs(settled/nom-1)<.005
 assert abs(avg(t,out,.045,.05)-avg(t,out,.05,.055))<.001
 met={'output_mean_V':settled,'restart_mean_V':avg(t,out,.13,.14),'source_V':8,'load_ohm':50 if mode=='5V' else 33,'first_mean_window_ms':[45,55],'second_mean_window_ms':[130,140]}
 for origin,stop,prefix in [(.005,.055,'first'),(.085,.14,'restart')]:
  e=cross(t,enable,3.5,origin,stop);assert e is not None;met[prefix+'_enable_delay_ms']=(e-origin)*1000
  q=cross(t,out,nom*.98,e,stop);assert q is not None;met[prefix+'_output_98pct_delay_ms']=(q-origin)*1000
  mask=(t>=origin)&(t<e);met[prefix+'_preenable_peak_V']=float(out[mask].max())
  met[prefix+'_reference_2p45_delay_ms']=(cross(t,v['V(comp)'],2.45,origin,stop)-origin)*1000
 for key,name in [('V(out)','output'),('V(vctrl)','startup_supply')]:
  q=cross(t,v[key],.05,.055,.085,False);met[name+'_first_below_50mV_ms']=None if q is None else (q-.055)*1000
 met['manifest']=[]
 for ext in ['asc','net','log','raw']:
  f=stem.with_suffix('.'+ext);shutil.copy2(f,D/f.name);met['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 keys=['V(vbat)','V(vctrl)','V(comp)','V(ttl)','V(out)'];np.savetxt(D/f'signals_{mode}.txt',np.column_stack([t]+[v[k] for k in keys]),delimiter='\t',header='\t'.join(['time']+keys),comments='')
 metrics[mode]=met
if mode_action=='analyze':
 (D/'metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2))
if mode_action=='plot':
 os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle')
 fig,axes=plt.subplots(2,2,figsize=(6.5,4.7));fig.subplots_adjust(left=.09,right=.98,bottom=.12,top=.82,hspace=.55,wspace=.24)
 styles=[('V(vbat)','Input after switch','#444444','--'),('V(vctrl)','Startup-circuit output','#D55E00','-'),('V(comp)','UVLO/OVLO reference','#0072B2','--'),('V(ttl)','Enable','#CC79A7','-.'),('V(out)','Output','#009E73','-')]
 for col,mode in enumerate(['5V','33V']):
  t,v=all_data[mode]
  for row,start,duration,before in [(0,.005,35,3),(1,.055,10,1)]:
   ax=axes[row,col];mask=(t>=start-before/1000)&(t<=start+duration/1000)
   for key,label,color,ls in styles:
    if row==1 and key in ['V(comp)','V(ttl)']:continue
    ax.plot((t[mask]-start)*1000,v[key][mask],label=label,color=color,ls=ls)
   ax.set_xlim(-before,duration);ax.set_ylim(-.12,8.5);ax.set_yticks([0,2,4,6,8]);ax.set_xlabel('Time from '+('connection' if row==0 else 'disconnection')+' (ms)');ax.set_title(('5 V' if mode=='5V' else '3.3 V')+' — '+('startup' if row==0 else 'shutdown'),fontsize=9,fontweight='normal',loc='left');ax.set_ylabel('Voltage (V)' if col==0 else '')
 fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',ncol=2,bbox_to_anchor=(.55,1.0))
 for ext in ['pdf','png','svg']:fig.savefig(R/f'docs/figures/SIM-01_calibrated_startup.{ext}',dpi=300)
 plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(6.5,2.5));fig.subplots_adjust(left=.09,right=.98,bottom=.23,top=.75,wspace=.25)
 for ax,mode in zip(axes,['5V','33V']):
  t,v=all_data[mode];mask=(t>=.00498)&(t<=.0052)
  for key,label,color,ls in styles:
   if key in ['V(vctrl)','V(out)']:ax.plot((t[mask]-.005)*1000,v[key][mask],color=color,label=label)
  ax.set_xlim(-.02,.2);ax.set_ylim(-.05,2.6);ax.set_xlabel('Time from connection (ms)');ax.set_title('5 V mode' if mode=='5V' else '3.3 V mode',fontweight='normal',fontsize=9,loc='left')
 axes[0].set_ylabel('Voltage (V)');fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=2)
 for ext in ['pdf','png','svg']:fig.savefig(R/f'docs/figures/SIM-01_calibrated_initial_both.{ext}',dpi=300)
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(3.0,2.2));fig.subplots_adjust(left=.18,right=.94,bottom=.23,top=.72)
 t,v=all_data['5V'];mask=(t>=.00498)&(t<=.0052)
 for key,label,color,ls in styles:
  if key in ['V(vctrl)','V(out)']:ax.plot((t[mask]-.005)*1000,v[key][mask],color=color,label=label)
 ax.set_xlim(-.02,.2);ax.set_ylim(-.05,2.6);ax.set_yticks([0,1,2]);ax.set_xticks([0,.05,.1,.15,.2]);ax.set_ylabel('Voltage (V)');ax.set_xlabel('Time from connection (ms)',fontsize=8)
 fig.legend(*ax.get_legend_handles_labels(),loc='upper center',ncol=1,bbox_to_anchor=(.56,1.0))
 for ext in ['pdf','png','svg']:fig.savefig(R/f'docs/figures/SIM-01_calibrated_initial.{ext}',dpi=300)
 plt.close(fig)
 (D/'figure_manifest.json').write_text(json.dumps({'metrics_sha256':hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),'processing':'Original RAW samples; no smoothing. Event origins 5 and 55 ms.','matplotlib':matplotlib.__version__},indent=2))
