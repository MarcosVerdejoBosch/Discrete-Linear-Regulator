"""Plot selector-off results, explicitly retaining uncalibrated setpoint."""
from pathlib import Path
import os,json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
r=json.loads((HERE/'results/full_circuit_33V/line_change_metrics.json').read_text())
assert r['all_steps_completed']
rows=r['results'][1:]
assert [x['source_V'] for x in rows]==list(range(6,12))
assert all(x['enable_min_V']>5 and abs(x['drift_mV'])<.001 for x in rows)
plt.style.use(ROOT/'simulation/plotting/report.mplstyle')
fig,ax=plt.subplots(figsize=(3,2.4))
fig.subplots_adjust(left=.25,right=.94,bottom=.23,top=.87)
ax.plot([x['source_V'] for x in rows],[x['vout_avg_V'] for x in rows],color='#0072B2',marker='o',markersize=3)
ax.set_xlabel('Source voltage (V)'); ax.set_ylabel('Mean output voltage (V)')
ax.set_xticks(range(6,12)); ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.set_title('Selector off, 3.3 '+r'$\Omega$'+' load',fontsize=9,loc='left')
for ext in ['pdf','png','svg']:
    fig.savefig(ROOT/f'docs/figures/SIM-02_full_line_selector_off.{ext}',dpi=300)
print('Endpoint sensitivity (mV/V):',1000*(rows[-1]['vout_avg_V']-rows[0]['vout_avg_V'])/5)
print('Repeated 8 V difference (uV):',1e6*(rows[2]['vout_avg_V']-r['results'][0]['vout_avg_V']))
