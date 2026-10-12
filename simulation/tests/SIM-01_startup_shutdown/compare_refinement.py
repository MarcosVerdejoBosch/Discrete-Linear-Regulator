"""Compare a complete stricter transient run with the accepted 2-us run."""
from pathlib import Path
import runpy
import sys
import json
import numpy as np

H = Path(__file__).resolve().parent
sys.argv = ['analyze_startup.py', 'progress']
helpers = runpy.run_path(str(H / 'analyze_startup.py'))
read, avg, cross, R = (helpers[k] for k in ('read', 'avg', 'cross', 'R'))
results = {}
for mode, nominal, fine in [('5V', 5, 'trtol'), ('33V', 3.3, 'finalcheck')]:
    metrics = []
    for prefix in ('calibrated_startup', fine):
        stem = R / f'simulation/ltspice/SIM-01_{prefix}_{mode}'
        t, v = read(stem.with_suffix('.raw'))
        b = stem.with_suffix('.log').read_bytes()
        log = b.decode('utf-16-le' if b[1] == 0 else 'cp1252')
        assert t[-1] >= .139999 and 'Total elapsed time:' in log, f'{stem.name} incomplete'
        m = {'mean_V': avg(t, v['V(out)'], .045, .055),
             'restart_mean_V': avg(t, v['V(out)'], .13, .14)}
        for origin, end, name in [(.005, .055, 'first'), (.085, .14, 'restart')]:
            e = cross(t, v['V(ttl)'], 3.5, origin, end)
            q = cross(t, v['V(out)'], .98 * nominal, e, end)
            m[name + '_enable_ms'] = (e-origin)*1000
            m[name + '_98pct_ms'] = (q-origin)*1000
            m[name + '_pulse_V'] = float(v['V(out)'][(t >= origin) & (t < e)].max())
        for key, name in [('V(out)', 'out'), ('V(vctrl)', 'vctrl')]:
            q = cross(t, v[key], .05, .055, .085, False)
            assert q is not None
            m[name + '_50mV_ms'] = (q-.055)*1000
        metrics.append(m)
    delta = {key: metrics[1][key] - metrics[0][key] for key in metrics[0]}
    results[mode] = dict(nominal=metrics[0], refined=metrics[1], difference=delta)
(H / 'results/refined/comparison.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
