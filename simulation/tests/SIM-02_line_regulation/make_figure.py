"""Plot the preserved DC sweeps; run extract_dc.py to refresh the input tables."""
from pathlib import Path
import os, json, hashlib
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np

plt.style.use(ROOT / 'simulation/plotting/report.mplstyle')
fig, axes = plt.subplots(1, 2, figsize=(6, 2.65))
fig.subplots_adjust(left=.115, right=.975, bottom=.22, top=.82, wspace=.53)
records = []
for ax, name, nominal, load, color, ticks in zip(
    axes, ['TEST_DROPOUT', 'TEST_DROPOUT_33V'], [5, 3.3], [5, 3.3],
    ['#0072B2', '#009E73'], [[5.008, 5.010, 5.012, 5.014], [3.304, 3.306, 3.308, 3.310]]):
    source = HERE / 'results' / (name + '_line.txt')
    data = np.loadtxt(source, skiprows=1)
    assert len(data) == 5001 and np.all(np.diff(data[:, 0]) > 0)
    ax.plot(data[:, 0], data[:, 1], color=color)
    ax.set_xlim(6, 11); ax.set_xticks([6, 7, 8, 9, 10, 11])
    ax.set_yticks(ticks); ax.set_ylim(ticks[0]-.001, ticks[-1]+.001)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    ax.set_xlabel('Input voltage (V)'); ax.set_ylabel('Output voltage (V)')
    ax.set_title(f'{nominal:g} V mode, load {load:g} '+r'$\Omega$', fontsize=9, loc='left')
    records.append({'source':source.relative_to(ROOT).as_posix(),
                    'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
target = ROOT / 'docs/figures/SIM-02_line_regulation'
for extension in ['pdf', 'svg', 'png']:
    fig.savefig(target.with_suffix('.'+extension), dpi=300)
plt.close(fig)
(HERE / 'results/figure_manifest.json').write_text(json.dumps({
    'test':'SIM-02', 'sources':records, 'matplotlib':matplotlib.__version__,
    'numpy':np.__version__, 'processing':'Original DC samples; no smoothing or fitting.',
    'scope':'Reduced DC test schematics; equivalence to full SIM-01 is not established.'
}, indent=2)+'\n', encoding='utf-8')
print(target)
