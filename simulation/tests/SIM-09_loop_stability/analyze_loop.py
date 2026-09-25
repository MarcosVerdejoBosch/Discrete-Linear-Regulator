from pathlib import Path
import argparse,json,re,hashlib,shutil,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];L=R/'simulation/ltspice';D=H/'results/core';p=argparse.ArgumentParser();p.add_argument('action',choices=['analyze','validate','plot','progress']);args=p.parse_args()
def raw(path):
 b=path.read_bytes();mark='Binary:\n'.encode('utf-16-le');k=b.find(mark)
 if k<0:mark='Binary:\r\n'.encode('utf-16-le');k=b.find(mark)
 assert k>=0
 h=b[:k].decode('utf-16-le');names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()];body=b[k+len(mark):]
 if 'Flags: complex' in h:
  a=np.frombuffer(body,'<c16').reshape(-1,len(names));return a[:,0].real,dict(zip(names[1:],a[:,1:].T))
 dt=np.dtype([('first','<f8'),('v','<f4',(len(names)-1,))]);a=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dt)
 if 'Plotname: Operating Point' in h:return None,dict(zip(names,np.r_[a['first'][0],a['v'][0]]))
 return a['first'],dict(zip(names[1:],a['v'].T))
def complete(stem):
 b=stem.with_suffix('.log').read_bytes();s=b.decode('utf-16-le' if b[1]==0 else 'cp1252');assert 'Total elapsed time:' in s and 'Fatal Error' not in s,stem

def loop(prefix,probe='lgs:'):
 a=L/(prefix+'_voltage');b=L/(prefix+'_current');complete(a);complete(b);f,v=raw(a.with_suffix('.raw'));ff,i=raw(b.with_suffix('.raw'));assert np.array_equal(f,ff)
 xn='V('+probe+'x)';inn='I('+probe+'Vi)';q=2*(v[inn]*i[xn]-v[xn]*i[inn])+v[xn]+i[inn];T=q/(1-q);return f,T,v

def margins(f,T):
 mag=20*np.log10(abs(T));ph=np.unwrap(np.angle(T))*180/np.pi;lf=np.log10(f)
 unity=[];phase_cross=[]
 for j in np.flatnonzero((mag[:-1]>=0)!=(mag[1:]>=0)):
  w=-mag[j]/(mag[j+1]-mag[j]);x=lf[j]+w*(lf[j+1]-lf[j]);pp=ph[j]+w*(ph[j+1]-ph[j]);unity.append(dict(frequency_Hz=float(10**x),phase_deg=float(pp),phase_margin_deg=float(180+pp)))
 for target in range(-180,int(ph.min())-360,-360):
  for j in np.flatnonzero((ph[:-1]>=target)!=(ph[1:]>=target)):
   w=(target-ph[j])/(ph[j+1]-ph[j]);x=lf[j]+w*(lf[j+1]-lf[j]);mm=mag[j]+w*(mag[j+1]-mag[j]);phase_cross.append(dict(frequency_Hz=float(10**x),phase_deg=target,gain_margin_dB=float(-mm)))
 return dict(unity_crossings=unity,phase_crossings=phase_cross,gain_at_1Hz_dB=float(mag[0]),minimum_swept_gain_dB=float(mag.min()))
def archive(stem,extensions):
 out=[]
 for ext in extensions:
  p=stem.with_suffix('.'+ext)
  if not p.exists():continue
  q=D/p.name;shutil.copy2(p,q);out.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 return out
if args.action=='analyze':
 result={};bias=json.loads((D/'bias_reference.json').read_text())
 for mode in ['5V','33V']:
  f,T,v=loop('SIM-09_ac_'+mode);r=margins(f,T);assert len(r['unity_crossings'])==1 and len(r['phase_crossings'])==1
  _,op=raw(L/f'SIM-09_ac_{mode}_voltage.op.raw');_,op2=raw(L/f'SIM-09_ac_{mode}_current.op.raw');r['operating_point']={k:float(op[k]) for k in ['V(out)','V(fb)','V(n032)','V(vref)','V(vee)','V(vctrl)','V(ttl)','V(n057)','I(Rload)','Ic(Q26)']};r['output_difference_from_complete_uV']=1e6*(float(op['V(out)'])-bias[mode]['V(out)']);assert abs(r['output_difference_from_complete_uV'])<5
  assert abs(float(op['V(out)'])-float(op2['V(out)']))<1e-8
  fc=r['unity_crossings'][0]['frequency_Hz'];tv=-v['V(fb)']/v['V(n033)'];j=np.argmin(abs(f-fc));r['voltage_only_difference_at_nearest_crossover']={'gain_dB':float(20*np.log10(abs(tv[j]/T[j]))),'phase_deg':float(np.angle(tv[j]/T[j],deg=True))}
  r['manifest']=[]
  for stem in [L/f'SIM-09_core_{mode}',L/f'SIM-09_core_start_{mode}',L/f'SIM-09_ac_{mode}_voltage',L/f'SIM-09_ac_{mode}_current']:r['manifest']+=archive(stem,['cir','bias','raw','op.raw','log']) if 'core_start' in stem.name or '_ac_' in stem.name else archive(stem,['cir','bias'])
  np.savetxt(D/f'{mode}_loop.csv',np.column_stack([f,T.real,T.imag,20*np.log10(abs(T)),np.unwrap(np.angle(T))*180/np.pi]),delimiter=',',header='frequency_Hz,T_real,T_imag,gain_dB,phase_deg',comments='');result[mode]=r
 f,T,_=loop('SIM-09_analytic',probe='');expected=100/(1+2j*np.pi*f*.001);err=float(np.max(abs(T/expected-1)));assert err<1e-9
 result['analytic_check_max_relative_error']=err
 result['auxiliary_bias_sensitivity']={}
 for biasvalue in [14,16]:
  f,T,_=loop(f'SIM-09_check_dbl{biasvalue}');result['auxiliary_bias_sensitivity'][str(biasvalue)]=margins(f,T)
  for kind in ['voltage','current']:archive(L/f'SIM-09_check_dbl{biasvalue}_{kind}',['cir','raw','op.raw','log'])
 for kind in ['voltage','current']:archive(L/f'SIM-09_analytic_{kind}',['cir','raw','log'])
 (D/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:{'unity':v['unity_crossings'],'phase':v['phase_crossings'],'bias_delta_uV':v['output_difference_from_complete_uV']} for k,v in result.items() if k in ['5V','33V']},indent=2));print('Analytic error',err,'auxiliary sensitivity',result['auxiliary_bias_sensitivity'])
elif args.action in ['progress','validate']:
 tests=json.loads((D/'tone_tests.json').read_text());results={}
 for job in tests:
  mode=job['mode'];stem=L/f'SIM-09_full_tone_{mode}';t,v=raw(stem.with_suffix('.raw'));print(mode,'time',t[-1])
  if args.action=='progress':continue
  complete(stem);assert t[-1]>=.080248 # Completed log plus endpoint within the global 2 us step
  fc=job['frequency_Hz'];end=min(float(t[-1]),.08025);start=end-80/fc;m=(t>=start)&(t<=end);x=t[m].astype(float);dt=np.diff(x);weights=np.sqrt(np.r_[dt[0]/2,(dt[:-1]+dt[1:])/2,dt[-1]/2]);X=np.column_stack([np.cos(2*np.pi*fc*(x-start)),np.sin(2*np.pi*fc*(x-start)),np.ones(len(x)),(x-start)/(end-start)])
  fits={}
  for name in ['V(fb)','V(n033)']:
   y=v[name][m].astype(float);b=np.linalg.lstsq(X*weights[:,None],y*weights,rcond=None)[0];fits[name]=dict(phasor=b[0]-1j*b[1],rms_residual=float(np.sqrt(np.average((y-X@b)**2,weights=weights**2))))
  tv=-fits['V(fb)']['phasor']/fits['V(n033)']['phasor'];f,ac=raw(L/f'SIM-09_ac_{mode}_voltage.raw');ta=-ac['V(fb)']/ac['V(n033)'];expected=complex(np.interp(np.log10(fc),np.log10(f),ta.real),np.interp(np.log10(fc),np.log10(f),ta.imag));ratio=tv/expected
  r=dict(frequency_Hz=fc,amplitude_V=job['amplitude_V'],fit_cycles=80,fit_interval_s=[start,end],full_voltage_return_gain_dB=float(20*np.log10(abs(tv))),full_voltage_return_phase_deg=float(np.angle(tv,deg=True)),difference_from_core_voltage_return_dB=float(20*np.log10(abs(ratio))),difference_from_core_voltage_return_deg=float(np.angle(ratio,deg=True)),max_fit_step_ns=float(dt.max()*1e9),fit_residuals_V={k:z['rms_residual'] for k,z in fits.items()},enable_min_V=float(v['V(ttl)'][m].min()),manifest=archive(stem,['cir','log','raw']))
  assert r['max_fit_step_ns']<10.1 and r['enable_min_V']>5
  results[mode]=r
 (D/'validation.json').write_text(json.dumps(results,indent=2)) if args.action=='validate' else None
 if results:print(json.dumps(results,indent=2))
elif args.action=='plot':
 os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(2,1,figsize=(6.5,4.5),sharex=True);fig.subplots_adjust(left=.13,right=.97,bottom=.12,top=.89,hspace=.12)
 for mode,color,label in [('5V','#0072B2','5 V mode'),('33V','#009E73','3.3 V mode')]:
  a=np.loadtxt(D/f'{mode}_loop.csv',delimiter=',',skiprows=1);axes[0].semilogx(a[:,0],a[:,3],color=color,label=label);axes[1].semilogx(a[:,0],a[:,4],color=color)
 axes[0].axhline(0,color='.45',ls='--',lw=.7);axes[1].axhline(-180,color='.45',ls='--',lw=.7);axes[0].set_ylabel('Return-ratio magnitude (dB)');axes[1].set_ylabel('Phase (degrees)');axes[1].set_xlabel('Frequency (Hz)');axes[1].set_xlim(1,6e7);axes[1].set_yticks([0,-90,-180,-270,-360]);fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=2,bbox_to_anchor=(.55,1))
 for ext in ['pdf','png','svg']:fig.savefig(R/f'docs/figures/SIM-09_core_loop.{ext}',dpi=300)
 plt.close(fig)
 (D/'figure_manifest.json').write_text(json.dumps(dict(metrics_sha256=hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),processing='Tian return ratio from two AC injections, unwrapped phase, original 200 points/decade, no smoothing.',matplotlib=matplotlib.__version__),indent=2))
