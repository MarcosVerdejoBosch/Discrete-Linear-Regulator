"""Prepare, inspect and plot full-circuit calibrated load-regulation tests."""
from pathlib import Path
import argparse,csv,hashlib,json,os,re,shutil
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
DEST=HERE/'results/calibrated_load';DEST.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','inspect','plot','progress']);args=p.parse_args()
MODES=['5V','33V']
LOAD_TABLE='table(time,0,1,80m,1,80.1m,0.1,120m,0.1,120.1m,0.25,160m,0.25,160.1m,0.5,200m,0.5,200.1m,0.75,240m,0.75,240.1m,1,280m,1)'
def read_raw(path):
    b=path.read_bytes();m='Binary:\n'.encode('utf-16-le');pos=b.find(m)
    if pos<0:m='Binary:\r\n'.encode('utf-16-le');pos=b.find(m)
    assert pos>=0
    h=b[:pos].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[l.split()[1] for l in h.rsplit('Variables:',1)[1].splitlines() if l.strip()]
    dt=np.dtype([('t','<f8'),('v','<f4',(nv-1,))]);body=b[pos+len(m):]
    d=np.frombuffer(body[:len(body)//dt.itemsize*dt.itemsize],dtype=dt)
    return d['t'],dict(zip(names[1:],d['v'].astype(float).T))
if args.action=='prepare':
    manifest=[]
    for mode in MODES:
        nominal=5 if mode=='5V' else 3.3
        source=ROOT/f'simulation/ltspice/SIM-02_cal_02_{mode}.asc';s=source.read_bytes().decode('cp1252');chunks=s.split('SYMBOL ');hits=0
        for i,c in enumerate(chunks):
            if re.search(r'^SYMATTR InstName RLOAD\s*$',c,re.M):
                chunks[i],n=re.subn(r'^SYMATTR Value [^\r\n]*','SYMATTR Value R='+str(nominal)+'/'+LOAD_TABLE,c,flags=re.M);assert n==1;hits+=1
        assert hits==1
        s='SYMBOL '.join(chunks).replace('.tran 0 80m 0 2u','.tran 0 280m 0 2u')
        if mode=='33V':s=s.replace('.options plotwinsize=0','.options plotwinsize=0 itl4=100')
        target=ROOT/f'simulation/ltspice/SIM-03_calibrated_load_{mode}.asc';target.write_bytes(s.encode('cp1252'))
        manifest.append({'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'test':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'load':'Time-dependent resistor, nominal currents 1 A initially then 0.1, 0.25, 0.5, 0.75, 1 A','source_V':8,'temperature_C':27,'duration_ms':280,'max_step_us':2})
    (DEST/'preparation.json').write_text(json.dumps(manifest,indent=2)+'\n')
elif args.action in ['inspect','progress']:
    result={}
    for mode in MODES:
        stem=ROOT/f'simulation/ltspice/SIM-03_calibrated_load_{mode}'
        t,v=read_raw(stem.with_suffix('.raw'));print(mode,'last saved time',t[-1])
        if args.action=='progress':continue
        lb=stem.with_suffix('.log').read_bytes();log=lb.decode('utf-16-le' if lb[1]==0 else 'cp1252')
        if 'Total elapsed time:' not in log or t[-1]<.27999:raise SystemExit('Incomplete run; no final results produced')
        assert np.all(np.diff(t)>=0)
        def avg(y,a,b):
            mask=(t>a)&(t<b);x=np.r_[a,t[mask],b];return float(np.trapezoid(np.interp(x,t,y),x)/(b-a))
        rows=[]
        for current,a,end in [(1,.07,.08),(.1,.11,.12),(.25,.15,.16),(.5,.19,.20),(.75,.23,.24),(1,.27,.28)]:
            mask=(t>=a)&(t<=end);y=v['V(out)']
            r={'nominal_load_A':current,'vout_avg_V':avg(y,a,end),'drift_mV':1000*(avg(y,a,end)-avg(y,a-.01,a)),
               'vout_pp_mV':float(np.ptp(y[mask])*1000),'enable_min_V':float(v['V(ttl)'][mask].min()),
               'input_after_switch_V':avg(v['V(vbat)'],a,end),'load_A':avg(v['I(Rload)'],a,end)}
            assert r['enable_min_V']>5 and abs(r['drift_mV'])<.001, r
            rows.append(r)
        repeat=1e6*(rows[-1]['vout_avg_V']-rows[0]['vout_avg_V']);assert abs(repeat)<1
        calibration=json.loads((HERE.parent/'SIM-02_line_regulation/results/calibration/02/metrics.json').read_text())
        baseline_difference=1e6*(rows[0]['vout_avg_V']-calibration[mode]['mean_V'])
        # Compare like-for-like: the line test now uses the corrected U17 model.
        line_path=HERE.parent/'SIM-02_line_regulation/results/calibrated_line/metrics.json'
        line=json.loads(line_path.read_text())
        line_difference=1e6*(rows[0]['vout_avg_V']-line[mode]['results'][0]['vout_avg_V'])
        assert abs(line_difference)<1

        signed=1000*(rows[-1]['vout_avg_V']-rows[1]['vout_avg_V'])/(rows[-1]['load_A']-rows[1]['load_A'])
        target=5 if mode=='5V' else 3.3
        result[mode]={'all_steps_completed':True,'results':rows,'signed_slope_mV_per_A':signed,'repeat_1A_difference_uV':repeat,'calibration_difference_uV':baseline_difference,'calibration_reference_revision':'Historical pre-U17 calibration; retained for comparison only','current_line_reference_difference_uV':line_difference,'current_line_reference_sha256':hashlib.sha256(line_path.read_bytes()).hexdigest(),
                      'endpoint_change_mV':1000*(rows[-1]['vout_avg_V']-rows[1]['vout_avg_V']),'maximum_nominal_error_percent':max(abs(r['vout_avg_V']-target)/target*100 for r in rows[1:])}
        manifest=[]
        for ext in ['asc','net','log','raw']:
            f=stem.with_suffix('.'+ext);shutil.copy2(f,DEST/f.name);manifest.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
        result[mode]['manifest']=manifest
    if args.action=='inspect':
        (DEST/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
        with (DEST/'sampled_points.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['mode','point']+list(result['5V']['results'][0]))
            writer.writeheader()
            for mode in MODES:
                for i,r in enumerate(result[mode]['results']):writer.writerow({'mode':mode,'point':i,**r})
        print(json.dumps({k:{a:b for a,b in v.items() if a not in ['manifest','results']} for k,v in result.items()},indent=2))
else:
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter
    result=json.loads((DEST/'metrics.json').read_text());plt.style.use(ROOT/'simulation/plotting/report.mplstyle')
    fig,axes=plt.subplots(1,2,figsize=(6.5,2.5));fig.subplots_adjust(left=.12,right=.98,bottom=.22,top=.86,wspace=.5)
    for ax,mode,title in zip(axes,MODES,['(a) 5 V mode','(b) 3.3 V mode']):
        assert result[mode]['all_steps_completed'];rows=result[mode]['results'][1:]
        reference=rows[-1]['vout_avg_V']
        ax.plot([r['load_A'] for r in rows],[1e6*(r['vout_avg_V']-reference) for r in rows],color='#0072B2',marker='o',markersize=3)
        ax.set_xlabel('Mean load current (A)');ax.set_ylabel('Mean output change ('+r'$\mu$'+'V)');ax.set_xticks([.1,.25,.5,.75,1])
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False));ax.set_title(title,fontsize=9,loc='left')
    for ext in ['pdf','svg','png']:fig.savefig(ROOT/f'docs/figures/SIM-03_calibrated_load.{ext}',dpi=300)
    plt.close(fig)
    (DEST/'figure_manifest.json').write_text(json.dumps({'source':'metrics.json','sha256':hashlib.sha256((DEST/'metrics.json').read_bytes()).hexdigest(),'matplotlib':matplotlib.__version__,'numpy':np.__version__,'processing':'Time-weighted final 10 ms means, referenced to final 1 A mean; first startup point excluded from plotted sweep; no smoothing or fitting.'},indent=2)+'\n')
