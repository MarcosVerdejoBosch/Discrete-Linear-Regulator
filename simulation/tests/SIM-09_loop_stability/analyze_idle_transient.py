"""Read the two near-no-load transient controls and retain original samples."""
from pathlib import Path
import ast,json,re,hashlib,shutil,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];L=R/'simulation/ltspice';D=H/'results/cap_esr'
tree=ast.parse((H/'analyze_loop.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(1,2,figsize=(7,3),sharey=True);results={}
for tag,color,label in [('nominal','#0072B2','ESR = 1 ohm'),('ESR010','#D55E00','ESR = 0.1 ohm')]:
 stem=L/f'SIM-09_ce_transient_33V_{tag}';complete(stem);t,v=raw(stem.with_suffix('.raw'));assert t[-1]>=.004999;y=v['V(out)'].astype(float);base=float(y[(t>.0005)&(t<.001)].mean());events=[]
 for col,(edge,end) in enumerate([(.001,.003),(.003,.005)]):
  m=(t>=edge)&(t<end);yy=y[m];xx=t[m];ref=float(y[(t>end-.0005)&(t<end)].mean());peak=float(np.max(abs(yy-ref)));bound=.02*peak;outside=np.flatnonzero(abs(yy-ref)>bound);settle=float((xx[outside[-1]+1]-edge)*1e6) if len(outside) and outside[-1]+1<len(xx) else None
  events.append({'edge_s':edge,'peak_deviation_mV':peak*1000,'final_mean_V':ref,'last_500us_pp_uV':float(np.ptp(y[(t>end-.0005)&(t<end)]))*1e6,'settling_to_2pct_of_peak_us':settle,'band_uV':bound*1e6})
  plot=(t>=edge-10e-6)&(t<=edge+250e-6);axes[col].plot((t[plot]-edge)*1e6,(y[plot]-base)*1000,color=color,label=label);axes[col].set_xlabel('Time from change (us)');axes[col].set_title('Add 10 uA' if col==0 else 'Remove 10 uA',fontsize=9);axes[col].set_xlim(-10,250)
 results[tag]={'events':events,'base_V':base,'manifest':archive(stem,['cir','log','raw','op.raw'])};np.savetxt(D/f'transient_{tag}.csv',np.column_stack([t,y]),delimiter=',',header='time_s,vout_V',comments='')
axes[0].set_ylabel('Output change (mV)');axes[1].legend(fontsize=7);fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(D/f'SIM09_idle_transient.{ext}',dpi=250)
(D/'transient_metrics.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v['events'] for k,v in results.items()},indent=2))
