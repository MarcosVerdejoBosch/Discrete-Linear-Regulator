"""Plot completed full-circuit results without replacing historical DC data."""
from pathlib import Path
import os,json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
result=json.loads((HERE/'results/full_circuit/sweep_metrics.json').read_text())
rows=result['results']
assert len(rows)==6
plt.style.use(ROOT/'simulation/plotting/report.mplstyle')
fig,ax=plt.subplots(figsize=(3,2.4))
fig.subplots_adjust(left=.25,right=.94,bottom=.23,top=.87)
ax.plot([r['source_V'] for r in rows],[r['vout_avg_V'] for r in rows],
        color='#0072B2',marker='o',markersize=3)
ax.set_xlabel('Source voltage (V)'); ax.set_ylabel('Mean output voltage (V)')
ax.set_xticks([6,7,8,9,10,11])
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.set_title('Full circuit, 5 '+r'$\Omega$'+' load',fontsize=9,loc='left')
target=ROOT/'docs/figures/SIM-02_full_line_5V'
for ext in ['pdf','png','svg']: fig.savefig(target.with_suffix('.'+ext),dpi=300)
plt.close(fig)
print(target)
