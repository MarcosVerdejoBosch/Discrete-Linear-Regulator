"""Recheck archived evidence without rerunning LTspice or replacing results."""
from pathlib import Path
import ast
import hashlib
import json
import re
import numpy as np

here = Path(__file__).resolve().parent
archive = here / 'results/calibrated'
root = here.parents[2]
# Reuse only the reader and integration functions, without analyzer side effects.
tree = ast.parse((here / 'analyze_idle.py').read_text())
helpers = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
exec(compile(helpers, 'analyze_idle.py', 'exec'))
metrics = json.loads((archive / 'metrics.json').read_text())
review = {'date': '2026-09-20', 'method': 'Archived RAW reanalysis and SHA256 checks; no new LTspice run',
          'hardware_validation': 'pending', 'user_review': 'pending', 'modes': {}}
for mode, stored in metrics.items():
    for entry in stored['manifest']:
        for folder in [archive, root / 'simulation/ltspice']:
            assert hashlib.sha256((folder / entry['file']).read_bytes()).hexdigest() == entry['sha256']
    stem = archive / f'SIM-05_calibrated_idle_{mode}'
    log = stem.with_suffix('.log').read_bytes()
    assert 'Total elapsed time:' in log.decode('utf-16-le' if log[1] == 0 else 'cp1252')
    net = stem.with_suffix('.net').read_text(encoding='cp1252')
    for line in ['R15 N009 N038 10', 'R33 FB N022 14846.5', 'RFB2 N022 0 28759.8', '.tran 0 120m 0 2u', '.temp 27']:
        assert line in net, line
    t, v = read(stem.with_suffix('.raw'))
    assert t[-1] >= .119999 and np.all(np.diff(t) >= 0)
    current = -avg(t, v['I(Vbat)'], .1, .12) * 1000
    output = avg(t, v['V(out)'], .1, .12)
    assert abs(current - stored['input_current_mA']) < 1e-9
    assert abs(output - stored['signals']['V(out)']['mean']) < 1e-12
    mask = (t >= .1) & (t <= .12)
    assert v['V(ttl)'][mask].min() > 5
    for key in ['I(V5)', 'I(V10)', 'I(V1)']:
        assert np.max(np.abs(v[key][mask])) < 1e-12
    windows = [-avg(t, v['I(Vbat)'], a, a+.01)*1000 for a in [.08, .09, .1, .11]]
    assert max(windows)-min(windows) < .02
    review['modes'][mode] = {'input_current_mA': current, 'output_V': output,
        'end_time_s': float(t[-1]), 'window_spread_mA': max(windows)-min(windows),
        'archived_and_active_hashes_match': True, 'enabled': True, 'auxiliary_source_currents_zero': True}
(archive / 'review_verification.json').write_text(json.dumps(review, indent=2)+'\n', encoding='utf-8')
print(json.dumps(review, indent=2))
