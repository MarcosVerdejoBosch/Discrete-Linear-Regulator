"""Compare settled electrical dissipation; thermal lines are stated assumptions."""
from pathlib import Path
import json, os
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/driver_thermal'
j=json.loads((D/'metrics.json').read_text())
os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use(R/'simulation/plotting/report.mplstyle')
fig,axes=plt.subplots(2,1,figsize=(6.5,5.0),sharex=True)
fig.subplots_adjust(left=.12,right=.97,bottom=.17,top=.79,hspace=.22)
for name,label,color in [('original',r'Original: $R_{21}=10\,\Omega$','#0072B2'),]:
    rows=j[name]['rows'][1:];x=[r['board_input_V'] for r in rows]
    for ax,key in zip(axes,['Q3_power_mW','R21_power_mW']):
        ax.plot(x,[r[key] for r in rows],'-o',ms=4,color=color,label=label)
axes[0].axhline(130,color='.45',ls='--',lw=.9,label=r'Review target: 130 mW ($T_a=35^\circ$C, $R_{\theta JA}=500$ K/W)')
axes[1].axhline(125,color='.45',ls='--',lw=.9,label=r'Review target: 50% of a 0.25 W rating')
axes[0].set_ylabel(r'$Q_3$ power (mW)')
axes[1].set_ylabel(r'$R_{21}$ power (mW)')
axes[1].set_xlabel('Board input voltage (V)')
axes[1].set_xlim(5.12,4.87)
axes[0].set_ylim(0,max(400,max(r['Q3_power_mW'] for a in j.values() for r in a['rows'])*1.1))
axes[1].set_ylim(0,max(270,max(r['R21_power_mW'] for a in j.values() for r in a['rows'])*1.1))
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles[:1],labels[:1],loc='upper left',bbox_to_anchor=(.12,.865),ncol=2,fontsize=8,frameon=False)
axes[0].text(.98,.36,'130 mW review target',transform=axes[0].transAxes,ha='right',fontsize=7,color='.35')
axes[1].text(.98,.50,'125 mW review target',transform=axes[1].transAxes,ha='right',fontsize=7,color='.35')
fig.text(.12,.95,r'SIM-04 / 5 V mode / 50 $\Omega$ load / electrical model at 27 $^\circ$C',fontsize=9)
fig.text(.12,.90,'Settled means; connecting lines are guides. Implemented R21 = 10 ohm.',fontsize=8)
fig.text(.12,.025,r'Targets: $Q_3$: $T_j=100^\circ$C, $T_a=35^\circ$C, $R_{\theta JA}=500$ K/W; $R_{21}$: 50% of 0.25 W.',fontsize=7)
for ext in ['pdf','png','svg']:fig.savefig(D/f'driver_power_comparison.{ext}',dpi=250)
plt.close(fig)
