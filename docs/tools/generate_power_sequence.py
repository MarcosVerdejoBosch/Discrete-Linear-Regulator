from pathlib import Path
import hashlib, json, re, os
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
OUT = ROOT/'docs/figures'
os.environ['MPLCONFIGDIR'] = str(ROOT/'tmp/mpl-sequence')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def load(sub, stem, mode=None):
    key = 'SIM-01' if mode else 'SIM-07'
    sources = json.loads((REPO/'docs/data/power_sequence/sources.json').read_text())
    prov = next(x for x in sources if x['export_file'] == key+'.npz')
    path = REPO/'docs/data/power_sequence'/prov['export_file']
    assert hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() == prov['export_sha256']
    m=json.loads((REPO/'simulation/tests'/sub/'results/calibrated/metrics.json').read_text())
    if mode: m=m[mode]
    assert prov['sha256'] == next(x['sha256'] for x in m['manifest'] if x['file'].endswith('.raw'))
    with np.load(path, allow_pickle=False) as data:
        t=data['time_ms']; v={k:data[k] for k in data.files if k!='time_ms'}
    assert len(t)==prov['export_samples'] and np.all(np.diff(t)>=0)
    return t,v,m,prov

s=load('SIM-01_startup_shutdown','SIM-01_calibrated_startup_5V','5V')
p=load('SIM-07_uvlo_ovlo','SIM-07_calibrated_protection_5V')
plt.style.use(REPO/'simulation/plotting/report.mplstyle')
plt.rcParams.update({'font.size':11,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'path.simplify':False})
fig=plt.figure(figsize=(15,9.0))
gs=fig.add_gridspec(3,3,left=.065,right=.985,bottom=.22,top=.80,hspace=.25,wspace=.28,height_ratios=[2,1.35,.50])
colors={'V(vbat)':'#56606B','V(vctrl)':'#C97B17','V(comp)':'#236DB0','V(out)':'#008D87'}
labels={'V(vbat)':'Input after switch','V(vctrl)':'Startup-circuit output','V(comp)':'Protection reference','V(out)':'Regulated output'}
styles={'V(vbat)':'--','V(vctrl)':'-','V(comp)':':','V(out)':'-'}
titles=['(a) Power-on','(b) Undervoltage cycle','(c) Overvoltage cycle']
manifest={'sources':[s[3],p[3]],'mode':'5 V','load_ohm':{'SIM-01':50,'SIM-07':5},'processing':'Original samples, no smoothing/resampling. SIM-01 time origin shifted by 5 ms. Control traces divided by local VEE. Enable bands use 50% VEE for display only; these are not transistor switching thresholds.','windows_ms':[[2,45],[75,150],[160,264]],'scope':'Separate experiments, not a continuous time record. Initial pulse is retained but requires SIM-01 detail figure for resolution.'}
for col,(data,window,origin) in enumerate([(s,(2,45),5),(p,(75,150),0),(p,(160,264),0)]):
    t,v,m,_=data;sel=(t>=window[0])&(t<=window[1]);x=t[sel]-origin
    ax=fig.add_subplot(gs[0,col]);ctrl=fig.add_subplot(gs[1,col],sharex=ax);band=fig.add_subplot(gs[2,col],sharex=ax)
    for key in colors:
        ax.plot(x,v[key][sel],color=colors[key],ls=styles[key],lw=1.5,label=labels[key])
    ax.set_title(titles[col],loc='left',pad=13,fontsize=13,fontweight='normal')
    ax.set_ylim(-.25,14 if col==2 else 8.7);ax.set_yticks([0,4,8,12] if col==2 else [0,2,4,6,8])
    ax.tick_params(labelbottom=False)
    if col==0:ax.set_ylabel('Voltage (V)')
    keys=[('V(ttl)','Enable','#8A4BA3','-')]
    if col:keys=[('V(1)' if col==1 else 'V(2)','UVLO permission' if col==1 else 'OVLO permission','#236DB0','--'),('V(ldo_2)','Delay permission','#C97B17',':')]+keys
    for key,label,color,ls in keys:
        ratio=np.divide(v[key][sel],v['V(vee)'][sel],out=np.zeros(len(x)),where=np.abs(v['V(vee)'][sel])>.1)
        ctrl.plot(x,ratio,color=color,ls=ls,lw=1.4,label=label)
    ctrl.set_ylim(-.08,1.15);ctrl.set_yticks([0,.5,1]);ctrl.axhline(.5,color='#BCC4C9',lw=.6,zorder=0)
    ctrl.legend(loc='upper left',bbox_to_anchor=(0,-.62),fontsize=9,handlelength=2,ncol=1)
    if col==0:
        ctrl.set_ylabel('Control voltage / VEE')
        ax.yaxis.set_label_coords(-.12,.5)
        ctrl.yaxis.set_label_coords(-.12,.5)
    ctrl.set_xlabel('Time from connection (ms)' if col==0 else 'Simulation time (ms)')
    band.set_ylim(0,1);band.set_xlim(window[0]-origin,window[1]-origin);band.axis('off')
    if col==0:
        on=m['first_enable_delay_ms'];segments=[(-3,0,'Off'),(0,on,'Bias / delay'),(on,40,'Enabled')]
        edges=[on]
    else:
        ev=[e['time_ms'] for e in m['events']['enable'] if window[0]<e['time_ms']<window[1]];edges=ev
        segments=[(window[0],ev[0],'Enabled'),(ev[0],ev[1],'Disabled'),(ev[1],window[1],'Enabled')]
    for a,b,label in segments:
        color='#DCEEEB' if label=='Enabled' else '#ECEEF1'
        band.add_patch(Rectangle((a,.18),b-a,.64,color=color,linewidth=0))
        if label!='Off':band.text((a+b)/2,.5,label,ha='center',va='center',fontsize=9,color='#34454F')
    for edge in edges:
        for a in (ax,ctrl):a.axvline(edge,color='#8A4BA3',lw=.65,ls=(0,(2,3)),alpha=.65)
    if col==0:handles,legendlabels=ax.get_legend_handles_labels()

fig.text(.065,.95,'Power-on and input-fault response',fontsize=21,color='#263640')
fig.text(.065,.911,'5 V mode  |  Accepted LTspice results  |  Load: SIM-01 = 50 ohm; SIM-07 = 5 ohm',fontsize=11,color='#65717A')
fig.legend(handles,legendlabels,loc='upper left',bbox_to_anchor=(.06,.883),ncol=4,frameon=False,columnspacing=2)
notes=[('SIM-01  /  8 V source, 50 ohm load','Reference establishes first; enable follows the delay.\nOutput rises after enable. The initial pulse is retained.'),('SIM-07  /  Undervoltage, 5 ohm load','Delay permission drops before UVLO in this test.\nRecovery waits for the delay path as well as UVLO.'),('SIM-07  /  Overvoltage, 5 ohm load','OVLO and system enable have distinct analog transitions.\nTheir 50% crossings are comparison markers only.')]
for col,(head,body) in enumerate(notes):
    left=gs[0,col].get_position(fig).x0
    fig.text(left,.115,head,fontsize=10,color='#263640',weight='bold')
    fig.text(left,.062,body,fontsize=9.1,color='#52616B',linespacing=1.5)
fig.text(.065,.025,'Separate experiments and time windows. Bands use enable > 0.5 VEE; they do not indicate measured hardware states. No physical measurements shown.',fontsize=9,color='#65717A')
for ext in ['pdf','png']:fig.savefig(OUT/f'power_sequence.{ext}',dpi=170)
(REPO/'docs/data/power_sequence/figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(OUT/'power_sequence.png')

