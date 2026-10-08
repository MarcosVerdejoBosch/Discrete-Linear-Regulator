from pathlib import Path
import json,numpy as np,os
os.environ.setdefault('MPLCONFIGDIR',str(Path('tmp/mpl-cache').resolve()))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
home=Path(__file__).resolve().parent;repo=home.parents[2];r=home/'results/external';out=repo/'docs/figures';data=json.loads((r/'metrics.json').read_text())
plt.style.use(repo/'simulation/plotting/report.mplstyle')
colors=['#0072B2','#D55E00','#009E73','#8A5993']
def get(mode,current,cap=0,esr=0):
 m=next(v for v in data.values() if v['mode']==mode and v['current_A']==current and v['external_uF']==cap and v['external_series_ohm']==esr)
 return m,np.loadtxt(r/(m['stem']+'.csv'),delimiter=',',skiprows=1)
def setup(axg,axp):
 axg.axhline(0,color='.5',ls='--',lw=.65);axp.axhline(-180,color='.5',ls='--',lw=.65)
 axg.set_ylim(-85,145);axp.set_ylim(-400,5);axp.set_yticks([0,-90,-180,-270,-360]);axp.set_xlim(1,6e7);axp.xaxis.set_major_formatter(EngFormatter(unit='Hz'));axp.set_xlabel('Frequency')
 axg.set_ylabel('Loop gain (dB)');axp.set_ylabel('Phase (deg)')
for mode in ['5V','33V']:
 fig,(ag,ap)=plt.subplots(2,1,figsize=(6.8,4.7),sharex=True);fig.subplots_adjust(left=.12,right=.98,top=.88,bottom=.31,hspace=.10)
 rows=[]
 for i,current in enumerate([.1,1.]):
  m,a=get(mode,current);c=colors[i];ls='-' if i==0 else '--';pm=m['unity_crossings'][0];gm=m['phase_crossings'][0]
  ag.semilogx(a[:,0],a[:,3],c=c,ls=ls,label='100 mA' if i==0 else '1 A');ap.semilogx(a[:,0],a[:,4],c=c,ls=ls)
  fc=pm['frequency_Hz'];fp=gm['frequency_Hz'];ph=pm['phase_deg']
  ag.plot(fc,0,'o',color=c,ms=4);ap.plot(fc,ph,'o',color=c,ms=4);ag.axvline(fc,color=c,ls=':',lw=.65,alpha=.7);ap.vlines(fc,-180,ph,color=c,ls=':',lw=1)
  ag.plot(fp,-gm['gain_margin_dB'],'s',color=c,ms=3.7);ap.plot(fp,-180,'s',color=c,ms=3.7);ag.vlines(fp,-gm['gain_margin_dB'],0,color=c,ls=':',lw=1)
  rows.append([('100 mA' if i==0 else '1 A'),f"{fc/1e3:.1f} kHz",f"{pm['phase_margin_deg']:.1f} deg",f"{gm['gain_margin_dB']:.1f} dB"])
 setup(ag,ap);ag.legend(loc='lower left',frameon=False,ncol=2);fig.suptitle(('5 V' if mode=='5V' else '3.3 V')+' | load comparison',fontsize=10,fontweight='normal')
 tax=fig.add_axes([0,0,1,1],zorder=-1);tax.axis("off");table=tax.table(cellText=rows,colLabels=['Load','Unity-gain frequency','Phase margin','Gain margin'],cellLoc='center',bbox=[.12,.018,.86,.115]);table.auto_set_font_size(False);table.set_fontsize(8)
 for cell in table.get_celld().values():cell.set_edgecolor('.85');cell.set_linewidth(.35)
 pm0=get(mode,.1)[0]['unity_crossings'][0]['phase_margin_deg'];pm1=get(mode,1.)[0]['unity_crossings'][0]['phase_margin_deg'];gm0=get(mode,.1)[0]['phase_crossings'][0]['gain_margin_dB'];gm1=get(mode,1.)[0]['phase_crossings'][0]['gain_margin_dB']
 fig.text(.12,.165,f'Delta (1 A - 100 mA): PM {pm1-pm0:+.2f} deg; GM {gm1-gm0:+.2f} dB.  On-board 1 µF + 1 Ω; no added capacitor.',fontsize=7.5)
 for ext in ['png','pdf']:fig.savefig(out/f'SIM-09_load_comparison_{mode}.{ext}',dpi=230)
 plt.close(fig)
 fig,axs=plt.subplots(2,2,figsize=(6.8,5.0),sharex=True,sharey='row');fig.subplots_adjust(left=.11,right=.98,top=.84,bottom=.34,hspace=.12,wspace=.19)
 for col,current in enumerate([.1,1.]):
  labels=[]
  for i,cap in enumerate([0,1,10,47]):
   m,a=get(mode,current,cap,0 if cap==0 else .1);ls=['-','--','-.',':'][i];label='No added C' if cap==0 else f'{cap} µF';labels.append(label)
   axs[0,col].semilogx(a[:,0],a[:,3],color=colors[i],ls=ls,label=label);axs[1,col].semilogx(a[:,0],a[:,4],color=colors[i],ls=ls)
   u=m['unity_crossings'][0];axs[0,col].plot(u['frequency_Hz'],0,'o',color=colors[i],ms=3);axs[1,col].plot(u['frequency_Hz'],u['phase_deg'],'o',color=colors[i],ms=3)
  setup(axs[0,col],axs[1,col]);axs[1,col].set_xticks([1,100,1e4,1e6]);axs[0,col].set_title('100 mA' if col==0 else '1 A',fontsize=9,fontweight='normal')
  if col:axs[0,col].set_ylabel('');axs[1,col].set_ylabel('')
 fig.suptitle(('5 V' if mode=='5V' else '3.3 V')+' | additional external capacitance',fontsize=10,fontweight='normal')
 fig.legend(*axs[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.55,.945),ncol=4,frameon=False,fontsize=8)
 rows=[]
 for cap in [0,1,10,47]:
  values=[get(mode,cur,cap,0 if cap==0 else .1)[0] for cur in [.1,1.]]
  rows.append(['None' if cap==0 else f'{cap} µF']+[f"{m['unity_crossings'][0]['phase_margin_deg']:.1f} / {m['phase_crossings'][0]['gain_margin_dB']:.1f}" for m in values])
 tax=fig.add_axes([0,0,1,1],zorder=-1);tax.axis("off");table=tax.table(cellText=rows,colLabels=['Added capacitor','100 mA: PM (deg) / GM (dB)','1 A: PM (deg) / GM (dB)'],cellLoc='center',bbox=[.11,.012,.87,.15]);table.auto_set_font_size(False);table.set_fontsize(7.4)
 for cell in table.get_celld().values():cell.set_edgecolor('.85');cell.set_linewidth(.35)
 fig.text(.11,.205,'On-board 1 µF + 1 Ω retained. Added branch series resistance: 0.1 Ω (assumed); fixed auxiliary biases.',fontsize=7.2)
 for ext in ['png','pdf']:fig.savefig(out/f'SIM-09_external_capacitance_{mode}.{ext}',dpi=230)
 plt.close(fig)
print('Four comparative figures generated.')
