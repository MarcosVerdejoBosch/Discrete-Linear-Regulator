"""Terminal-power review of the original driver and a simulation-only R21 candidate."""
from pathlib import Path
import json, hashlib, shutil, sys, os
import numpy as np
from analyze_adjusted import read, avg

H=Path(__file__).resolve().parent; R=H.parents[2]
D=H/'results/driver_thermal'
CASES=[('original',10,'SIM-04_driver_thermal_5V',.163),
       ('R100_candidate',100,'SIM-04_driver_R100_5V',.179)]

def analyze():
    results={}
    for name,res,stemname,end in CASES:
        stem=R/'simulation/ltspice'/stemname
        t,v=read(stem.with_suffix('.raw'))
        print(name,'endpoint_ms',t[-1]*1000)
        if sys.argv[1]=='progress':continue
        b=stem.with_suffix('.log').read_bytes()
        log=b.decode('utf-16-le' if b[1]==0 else 'cp1252')
        assert t[-1]>=end-1e-8 and 'Total elapsed time:' in log
        # LTspice currents are positive into each BJT terminal. Collector is grounded.
        pq=(-v['V(n037)'])*v['Ic(Q14)']+(v['V(n036)']-v['V(n037)'])*v['Ib(Q14)']
        pr=res*v['I(R15)']**2
        pt=(v['V(n008)']-v['V(vctrl)'])*v['Ic(Q26)']+(v['V(n009)']-v['V(vctrl)'])*v['Ib(Q26)']
        pmos=(v['V(n038)']-v['V(n037)'])*v['I(R15)']
        base=avg(t,v['V(out)'],.07,.08)
        rows=[]
        windows=[(8,.08),(5.1,.115),(5,.131),(4.95,.147),(4.94,.163)]
        if end>.17:windows.append((4.90,.179))
        for source,e in windows:
            a=e-.005; m=(t>=a)&(t<=e)
            pqmean=avg(t,pq,a,e)
            rows.append(dict(source_V=source,window_ms=[a*1000,e*1000],
                board_input_V=avg(t,v['V(vbat)'],a,e),output_V=avg(t,v['V(out)'],a,e),
                reference_V=avg(t,v['V(vref)'],a,e),
                output_loss_mV=1000*(base-avg(t,v['V(out)'],a,e)),
                Q3_power_mW=1000*pqmean,R21_power_mW=1000*avg(t,pr,a,e),
                pass_power_mW=1000*avg(t,pt,a,e),
                enable_MOS_path_power_estimate_mW=1000*avg(t,pmos,a,e),
                pass_base_mA=1000*avg(t,-v['Ib(Q26)'],a,e),
                Q3_collector_mA=1000*avg(t,-v['Ic(Q14)'],a,e),
                Q3_current_KCL_error_A=float(np.max(np.abs(v['Ic(Q14)'][m]+v['Ib(Q14)'][m]+v['Ie(Q14)'][m]))),
                output_pp_mV=1000*float(np.ptp(v['V(out)'][m])),
                output_half_window_difference_mV=1000*(avg(t,v['V(out)'],e-.0025,e)-avg(t,v['V(out)'],a,e-.0025)),
                enable_min_fraction=float(np.min((v['V(ttl)']/v['V(vee)'])[m])),
                estimated_Tj_at_35C_500KperW=35+500*pqmean,
                estimated_Tj_at_35C_362KperW=35+362*pqmean))
        folder=D/name;folder.mkdir(exist_ok=True);manifest=[]
        for ext in ['asc','net','log','raw']:
            p=stem.with_suffix('.'+ext);shutil.copy2(p,folder/p.name)
            manifest.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        keys=['V(vbat)','V(vctrl)','V(out)','V(vref)','V(ttl)','V(vee)','Ic(Q14)','Ib(Q14)','Ib(Q26)','I(R15)']
        m=t>=.08
        np.savetxt(folder/'waveforms.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]+[pq[m],pr[m]]),delimiter=',',header=','.join(['time_s']+keys+['Q3_power_W','R21_power_W']),comments='')
        results[name]=dict(R21_ohm=res,baseline_output_V=base,rows=rows,manifest=manifest,
            peak_Q3_power_W=float(np.max(pq)),peak_R21_power_W=float(np.max(pr)),
            peak_Q3_collector_A=float(np.max(np.abs(v['Ic(Q14)']))),
            caveat='Peak values are numerical screening results, not validated hardware pulse ratings. Thermal estimates use electrical power at 27 C without self-heating feedback, and published reference-board resistances, not measured PCB resistance.')
        print(name,json.dumps(rows,indent=2))
    if results:(D/'metrics.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':
    analyze()
