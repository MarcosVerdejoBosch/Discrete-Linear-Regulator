"""Does disconnecting the external load provide a thermal rest for the driver?"""
from pathlib import Path
import json, hashlib, shutil, sys, os
import numpy as np
from analyze_adjusted import read, avg
H=Path(__file__).resolve().parent;R=H.parents[2]
INHIBIT=len(sys.argv)>2 and sys.argv[2]=='inhibit'
D=H/('results/pulsed_load_inhibit' if INHIBIT else 'results/pulsed_load')
stem=R/'simulation/ltspice'/('SIM-04_pulsed_load_inhibit_5V' if INHIBIT else 'SIM-04_pulsed_load_5V')

def run():
    if not stem.with_suffix('.raw').exists():
        print('Initializing');return
    t,v=read(stem.with_suffix('.raw'));print('endpoint_ms',t[-1]*1000)
    action=sys.argv[1] if len(sys.argv)>1 else 'progress'
    if action=='progress':return
    pq=-v['V(n037)']*v['Ic(Q14)']+(v['V(n036)']-v['V(n037)'])*v['Ib(Q14)']
    pr=10*v['I(R15)']**2
    if action=='analyze':
        b=stem.with_suffix('.log').read_bytes();log=b.decode('utf-16-le' if b[1]==0 else 'cp1252')
        assert t[-1]>=.209999 and 'Total elapsed time:' in log
        rows=[]
        for name,start,end in [('8V_loaded',.075,.080),('5p10_loaded',.105,.110),('5p10_unloaded',.125,.130),('4p94_before_pulse',.145,.150),('4p94_pulse1',.155,.160),('4p94_rest1',.175,.180),('4p94_pulse2',.185,.190),('4p94_rest2',.205,.210)]:
            # Keep a guard from command edges; do not interpolate switching current
            # across the boundary when computing an unloaded-state mean.
            start+=20e-6;end-=20e-6
            m=(t>=start)&(t<=end);mid=(start+end)/2
            rows.append(dict(name=name,window_ms=[start*1000,end*1000],
                board_input_V=avg(t,v['V(vbat)'],start,end),Vout_V=avg(t,v['V(out)'],start,end),
                Vref_V=avg(t,v['V(vref)'],start,end),load_mA=1000*avg(t,v['I(Rload)'],start,end),
                pass_base_mA=-1000*avg(t,v['Ib(Q26)'],start,end),
                Q3_power_mW=1000*avg(t,pq,start,end),R21_power_mW=1000*avg(t,pr,start,end),
                Q3_energy_mJ=1000*avg(t,pq,start,end)*(end-start),
                Vout_pp_mV=1000*float(np.ptp(v['V(out)'][m])),
                Vout_half_window_difference_mV=1000*(avg(t,v['V(out)'],mid,end)-avg(t,v['V(out)'],start,mid)),
                enable_min_fraction=float(np.min((v['V(ttl)']/v['V(vee)'])[m]))))
        cycles=[dict(window_ms=[a*1000,b*1000],Q3_average_mW=1000*avg(t,pq,a,b),R21_average_mW=1000*avg(t,pr,a,b),Q3_energy_mJ=1000*avg(t,pq,a,b)*(b-a)) for a,b in [(.15,.18),(.18,.21)]]
        pulses=[]
        for a,b in [(.15,.16),(.18,.19)]:
            final=avg(t,v['V(out)'],b-.00498,b-.00002)
            ii=np.flatnonzero((t>=a)&(t<=b-.00002))
            outside=ii[np.abs(v['V(out)'][ii]-final)>.001]
            last=outside[-1]+1 if len(outside) else ii[0]
            settled=None if last>ii[-1] else 1000*(float(t[last])-a)
            pulses.append(dict(command_window_ms=[a*1000,b*1000],
                final_mean_V=final,settled_within_1mV_after_ms=settled,
                peak_Q3_power_mW=1000*float(np.max(pq[ii])),
                Q3_energy_mJ=1000*avg(t,pq,a,b)*(b-a)))
        manifest=[]
        for ext in ['asc','net','log','raw']:
            p=stem.with_suffix('.'+ext);shutil.copy2(p,D/p.name)
            manifest.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        result=dict(rows=rows,cycles=cycles,pulses=pulses,manifest=manifest,external_drive_inhibition=INHIBIT,scope='Electrical simulation of prescribed external-load conductance, with optional external TTL pull-down during load-off. Pulse timings are diagnostic, not a qualified physical test. No electrothermal feedback or ESP32/MOSFET device implementation.')
        screen=(t>=.14)&(t<=.21)
        result['peak_Q3_including_turnoff_mW']=1000*float(np.max(pq[screen]))
        result['peak_R21_including_turnoff_mW']=1000*float(np.max(pr[screen]))
        if INHIBIT:result['peak_inhibit_sink_mA']=1000*float(np.max(v[next(k for k in v if k.lower()=='i(rinhibit)')]))
        (D/'metrics.json').write_text(json.dumps(result,indent=2))
        m=t>=.10;keys=['V(vbat)','V(out)','V(vref)','V(ttl)','V(vee)','I(Rload)','Ib(Q26)']
        np.savetxt(D/'waveforms.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]+[pq[m],pr[m]]),delimiter=',',header=','.join(['time_s']+keys+['Q3_power_W','R21_power_W']),comments='')
        print(json.dumps(result,indent=2))
    elif action=='plot':
        assert (D/'metrics.json').exists()
        os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.style.use(R/'simulation/plotting/report.mplstyle')
        fig,axes=plt.subplots(3,1,figsize=(6.5,5.8),sharex=True)
        fig.subplots_adjust(left=.13,right=.97,bottom=.10,top=.89,hspace=.20)
        m=(t>=.14)&(t<=.21);x=t[m]*1000
        axes[0].plot(x,v['V(out)'][m],color='#0072B2',label='Output')
        axes[0].plot(x,v['V(vbat)'][m],color='.45',ls='--',label='Board input')
        axes[0].set_ylabel('Voltage (V)')
        axes[1].plot(x,v['I(Rload)'][m]*1000,color='#009E73',label='External load')
        axes[1].plot(x,-v['Ib(Q26)'][m]*1000,color='#D55E00',label='Pass-transistor base')
        axes[1].set_ylabel('Current (mA)')
        axes[2].plot(x,pq[m]*1000,color='#0072B2',label=r'$Q_3$')
        axes[2].plot(x,pr[m]*1000,color='#D55E00',label=r'$R_{21}$')
        axes[2].set_ylabel('Power (mW)');axes[2].set_xlabel('Time (ms)')
        for ax in axes:
            for a,b in [(150,160),(180,190)]:ax.axvspan(a,b,color='.5',alpha=.10,lw=0)
            ax.legend(loc='best',fontsize=7,frameon=True,facecolor='white',framealpha=.95)
        axes[2].set_xlim(139,211)
        fig.text(.13,.97,r'SIM-04 / 4.94 V source / $R_{21}=10\,\Omega$ / 27 $^\circ$C',fontsize=9)
        fig.text(.13,.93,('External drive inhibited between pulses. ' if INHIBIT else '')+r'Shading: 50 $\Omega$ load.',fontsize=8)
        for ext in ['pdf','png','svg']:fig.savefig(D/f'pulsed_load_driver.{ext}',dpi=250)
        plt.close(fig)

if __name__=='__main__':run()
