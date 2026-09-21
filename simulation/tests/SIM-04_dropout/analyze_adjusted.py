from pathlib import Path
import re,json,sys,hashlib,shutil
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/adjusted'
def read(p):
 b=p.read_bytes();mark='Binary:\n'.encode('utf-16-le');k=b.find(mark)
 if k<0:mark='Binary:\r\n'.encode('utf-16-le');k=b.find(mark)
 assert k>=0
 h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[x.split()[1] for x in h.rsplit('Variables:',1)[1].splitlines() if x.strip()];dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[k+len(mark):];a=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
 return a['t'],dict(zip(names[1:],a['v'].astype(float).T))
def avg(t,y,a,b):
 m=(t>a)&(t<b);x=np.r_[a,t[m],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
def fall(t,y,level,start=.08):
 m=(t>=start);x=t[m];z=y[m]-level;ii=np.flatnonzero((z[:-1]>0)&(z[1:]<=0))
 if not len(ii):return None
 i=ii[0];return float(x[i]-z[i]*(x[i+1]-x[i])/(z[i+1]-z[i]))
def main():
    results={};action=sys.argv[1] if len(sys.argv)>1 else 'progress'
    for mode,nom in [('5V',5),('33V',3.3)]:
     stem=R/f'simulation/ltspice/SIM-04_adjusted_{mode}'
     if not stem.with_suffix('.raw').exists():print(mode,'no transient yet');continue
     t,v=read(stem.with_suffix('.raw'));print(mode,'endpoint_ms',t[-1]*1000)
     if action=='progress':continue
     lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
     assert 'Total elapsed time:' in log and t[-1]>=.141999,'Incomplete run'
     base=avg(t,v['V(out)'],.07,.08);ref=avg(t,v['V(vref)'],.07,.08)
     events={}
     for label,signal,level in [('output_100mV',v['V(out)'],base-.1),('output_98pct',v['V(out)'],nom*.98),('enable_half',v['V(ttl)']-.5*v['V(vee)'],0),('delay_half',v['V(ldo_2)']-.5*v['V(vee)'],0),('uvlo_half',v['V(1)']-.5*v['V(vee)'],0)]:
      q=fall(t,signal,level)
      if q is None:events[label]=None;continue
      values={k:float(np.interp(q,t,y)) for k,y in v.items()}
      values['pass_VEC']=values['V(vctrl)']-values['V(n008)'];values['pass_VEB']=values['V(vctrl)']-values['V(n009)'];values['board_headroom']=values['V(vbat)']-values['V(out)'];values['stage_headroom']=values['V(vctrl)']-values['V(out)'];values['reference_change_mV']=1000*(values['V(vref)']-ref)
      # Room-temperature screening of two relevant LM339 comparisons; not a full IC qualification.
      values['uvlo_either_input_in_CM']=bool(min(values['V(n086)'],values['V(comp)'])<=values['V(vee)']-1.5)
      values['delay_detector_either_input_in_CM']=bool(min(values['V(n088)'],values['V(comp)'])<=values['V(vee)']-1.5)
      events[label]={'time_ms':q*1000,'values':values}
     result={'baseline_output_V':base,'baseline_reference_V':ref,'events':events,'manifest':[]}
     for ext in ['asc','net','log','raw']:
      f=stem.with_suffix('.'+ext);shutil.copy2(f,D/f.name);result['manifest'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
     results[mode]=result
     print(mode,json.dumps({k:None if e is None else {'time_ms':e['time_ms'],**{n:e['values'][n] for n in ['V(vbat)','V(vctrl)','V(out)','V(ttl)','V(vref)','reference_change_mV','pass_VEC','stage_headroom','uvlo_either_input_in_CM']}} for k,e in events.items()},indent=2))
    if action=='analyze':(D/'metrics.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':
    main()
