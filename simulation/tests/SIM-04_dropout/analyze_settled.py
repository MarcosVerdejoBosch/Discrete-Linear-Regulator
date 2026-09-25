"""Time-weighted fixed-input checks; estimates are not electrothermal results."""
from pathlib import Path
import json, sys, shutil, hashlib
import numpy as np
import analyze_adjusted as a
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/adjusted_settled'
stem=R/'simulation/ltspice/SIM-04_adjusted_settled_5V'
t,v=a.read(stem.with_suffix('.raw'))
print('Settled check endpoint_ms',t[-1]*1000)
if len(sys.argv)<2 or sys.argv[1]!='analyze':sys.exit()
b=stem.with_suffix('.log').read_bytes();log=b.decode('utf-16-le' if b[1]==0 else 'cp1252')
assert t[-1]>=.162999 and 'Total elapsed time:' in log
base=a.avg(t,v['V(out)'],.07,.08)
rows=[]
for source,end in [(8,.08),(5.10,.115),(5.00,.131),(4.95,.147),(4.94,.163)]:
    start=end-.005
    means={k:a.avg(t,y,start,end) for k,y in v.items()}
    ir21=(v['V(n009)']-v['V(n038)'])/10
    # Current delivered through the enable path. Bias-mirror contribution and
    # driver base current are omitted, so this is a screening estimate only.
    driver_est=v['V(n037)']*ir21
    row={'source_V':source,'window_ms':[start*1000,end*1000],'means':means,
         'output_loss_mV':1000*(base-means['V(out)']),
         'board_headroom_mV':1000*(means['V(vbat)']-means['V(out)']),
         'stage_headroom_mV':1000*(means['V(vctrl)']-means['V(out)']),
         'pass_VEC_mV':1000*(means['V(vctrl)']-means['V(n008)']),
         'driver_power_screening_mW':1000*a.avg(t,driver_est,start,end),
         'R21_power_mW':1000*a.avg(t,ir21**2*10,start,end),
         'last_halves_output_difference_mV':1000*(a.avg(t,v['V(out)'],end-.0025,end)-a.avg(t,v['V(out)'],start,end-.0025)),
         'output_pp_mV':1000*float(np.ptp(v['V(out)'][(t>=start)&(t<=end)])),
         'enable_min_fraction':float(np.min((v['V(ttl)']/v['V(vee)'])[(t>=start)&(t<=end)])),
         'meets_100mV_criterion':bool(means['V(out)']>=base-.1)}
    rows.append(row)
manifest=[]
for ext in ['asc','net','log','raw']:
    p=stem.with_suffix('.'+ext);shutil.copy2(p,D/p.name)
    manifest.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
result={'baseline_output_V':base,'rows':rows,'manifest':manifest,
        'scope':'Electrical simulation at 27 C; no self-heating model. Q3 screening uses emitter voltage times current through series drive resistor; excludes bias mirror contribution and base-power correction. Not an exact transistor power measurement.'}
(D/'metrics.json').write_text(json.dumps(result,indent=2))
for r in rows:
    print(json.dumps({k:r[k] for k in ['source_V','output_loss_mV','board_headroom_mV','stage_headroom_mV','driver_power_screening_mW','R21_power_mW','last_halves_output_difference_mV','output_pp_mV','enable_min_fraction','meets_100mV_criterion']}))
