"""Render SIM-01 from the preserved export; no smoothing or resampling."""
from pathlib import Path
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SOURCE = HERE / 'results/input_switch/signals.txt'
with SOURCE.open() as f:
    names = f.readline().strip().split('\t')
data = np.loadtxt(SOURCE, skiprows=1)
s = dict(zip(names, data.T))
t = s['time']
if not np.isfinite(data).all() or np.any(np.diff(t) < 0) or t[-1] < .14:
    raise ValueError('Incomplete or invalid transient export')
plt.style.use(ROOT / 'simulation/plotting/report.mplstyle')
styles = {
    'V(vctrl)': ('Startup-circuit output', '#D55E00', '-'),
    'V(comp)': ('UVLO/OVLO reference', '#0072B2', '--'),
    'V(ttl)': ('Enable', '#CC79A7', '-.'),
    'V(out)': ('Output', '#009E73', '-'),
    'V(vbat)': ('Input after switch', '#444444', (0, (3, 2))),
}
fig, axes = plt.subplots(2, 1, figsize=(6.0, 5.5))
fig.subplots_adjust(left=.105, right=.98, bottom=.085, top=.80, hspace=.62)

def traces(ax, start, duration, keys, before=0):
    mask = (t >= start - before / 1000) & (t <= start + duration / 1000)
    for key in keys:
        label, color, ls = styles[key]
        ax.plot((t[mask]-start)*1000, s[key][mask], label=label,
                color=color, linestyle=ls)
    ax.set_xlim(-before, duration)
    ax.set_ylim(-.12, 8.5)
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.set_ylabel('Voltage (V)')

traces(axes[0], .005, 35, styles, before=3)
axes[0].set_xticks(np.arange(0, 36, 5))
axes[0].set_title('(a) Startup', loc='left', fontweight='normal', fontsize=9, pad=8)
axes[0].set_xlabel('Time relative to input connection (ms)')
fig.legend(*axes[0].get_legend_handles_labels(), loc='upper center',
           bbox_to_anchor=(.54, .99), ncol=2, columnspacing=1.8, handlelength=2.3)
traces(axes[1], .055, 10, ['V(vctrl)', 'V(out)', 'V(vbat)'], before=1)
axes[1].set_xticks(np.arange(0, 10.1, 2))
axes[1].set_title('(b) Shutdown', loc='left', fontweight='normal', fontsize=9, pad=8)
axes[1].set_xlabel('Time relative to input disconnection (ms)')
target = ROOT / 'docs/figures/SIM-01_startup_shutdown_5V'
for extension in ('pdf', 'svg', 'png'):
    fig.savefig(target.with_suffix('.' + extension), dpi=300)
plt.close(fig)

# Separate, single-column figure resolves the initial step without overlays.
detail, ax = plt.subplots(figsize=(3.0, 2.2))
detail.subplots_adjust(left=.18, right=.91, bottom=.21, top=.72)
traces(ax, .005, .2, ['V(vctrl)', 'V(out)'], before=.02)
ax.set_ylim(-.05, 2.6)
ax.set_yticks([0, 1, 2])
ax.set_xticks([0, .05, .1, .15, .2])
ax.set_xlabel('Time relative to input connection (ms)', fontsize=7.5)
detail.legend(*ax.get_legend_handles_labels(), loc='upper center',
              bbox_to_anchor=(.55, .99), ncol=1)
detail_target = ROOT / 'docs/figures/SIM-01_initial_transient_5V'
for extension in ('pdf', 'svg', 'png'):
    detail.savefig(detail_target.with_suffix('.' + extension), dpi=300)
plt.close(detail)
manifest = {
    'test': 'SIM-01', 'source': SOURCE.relative_to(ROOT).as_posix(),
    'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'samples': len(t), 'python': sys.version.split()[0],
    'matplotlib': matplotlib.__version__, 'numpy': np.__version__,
    'processing': 'Time origin shifted only; no smoothing or resampling.',
    'windows_s': [[.002, .040], [.054, .065]],
    'time_origins_s': [.005, .055],
    'initial_transient_window_s': [.00498, .0052],
}
(HERE / 'results/input_switch/figure_manifest.json').write_text(
    json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(f'Generated PDF, SVG and PNG: {target}')
