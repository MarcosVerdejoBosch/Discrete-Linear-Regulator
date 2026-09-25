"""Supporting diagnostic: original samples, adjusted thresholds, complete circuit."""
from pathlib import Path
import os, json, hashlib
import numpy as np
import analyze_adjusted as data

H=Path(__file__).resolve().parent
R=H.parents[2]
D=H/'results/adjusted'
metrics=json.loads((D/'metrics.json').read_text())
os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use(R/'simulation/plotting/report.mplstyle')
fig,axes=plt.subplots(3,2,figsize=(6.7,6.0),sharex=True)
fig.subplots_adjust(left=.11,right=.98,bottom=.10,top=.89,hspace=.25,wspace=.32)
for j,(mode,nom) in enumerate([('5V',5),('33V',3.3)]):
    t,v=data.read(D/f'SIM-04_adjusted_{mode}.raw')
    m=(t>=.08)&(t<=.115)
    x=v['V(vbat)'][m]
    axes[0,j].plot(x,v['V(out)'][m],label=r'$V_{out}$',color='#0072B2')
    axes[0,j].axhline(metrics[mode]['baseline_output_V']-.1,color='.5',ls='--',lw=.8,label='Baseline minus 100 mV')
    axes[0,j].set_ylim(0,nom*1.06)
    axes[0,j].set_title(f'{nom:g} V mode / {50 if j==0 else 33} '+r'$\Omega$',loc='left',fontsize=9,fontweight='normal')
    axes[1,j].plot(x,v['V(vref)'][m],label='Main reference',color='#009E73')
    axes[1,j].plot(x,v['V(comp)'][m],label='Protection reference',color='#D55E00',ls='--')
    axes[1,j].set_ylim(0,2.65)
    axes[2,j].plot(x,v['V(ttl)'][m]/v['V(vee)'][m],label='Enable',color='#0072B2')
    axes[2,j].plot(x,v['V(1)'][m]/v['V(vee)'][m],label='UVLO permission',color='#D55E00',ls='--')
    axes[2,j].plot(x,v['V(ldo_2)'][m]/v['V(vee)'][m],label='Delay permission',color='#009E73',ls=':')
    axes[2,j].set_ylim(-.04,1.08)
    axes[2,j].set_xlim(5.7,4.65)
    axes[2,j].set_xlabel('Board input voltage, falling (V)')
    for i in range(3):
        axes[i,j].legend(loc='lower left',fontsize=6.5,frameon=False)
    keys=['V(vbat)','V(vctrl)','V(out)','V(vref)','V(comp)','V(ttl)','V(vee)','V(1)','V(ldo_2)']
    np.savetxt(D/f'{mode}_falling_input.csv',np.column_stack([t[m]]+[v[k][m] for k in keys]),delimiter=',',header=','.join(['time_s']+keys),comments='')
axes[0,0].set_ylabel('Output (V)')
axes[1,0].set_ylabel('References (V)')
axes[2,0].set_ylabel(r'Logic voltage / $V_{EE}$')
fig.text(.5,.96,r'RV10 = 100 k$\Omega$; RV12 = 47 k$\Omega$; source ramp = $-0.1$ V/ms; 27 $^\circ$C',ha='center',fontsize=9)
for ext in ['pdf','png','svg']:
    fig.savefig(D/f'SIM-04_adjusted.{ext}',dpi=250)
plt.close(fig)
(D/'figure_manifest.json').write_text(json.dumps({'metrics_sha256':hashlib.sha256((D/'metrics.json').read_bytes()).hexdigest(),'processing':'Original transient samples; no smoothing. Board input is VBAT, after the external switch. Logic divided by instantaneous VEE only for display; not digital thresholds.','matplotlib':matplotlib.__version__},indent=2))
