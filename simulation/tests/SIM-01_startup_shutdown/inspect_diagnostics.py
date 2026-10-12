"""Report numerical trial progress without changing accepted SIM-01 results."""
from pathlib import Path
import re
import json
import hashlib
import shutil
import sys
import numpy as np

H = Path(__file__).resolve().parent
R = H.parents[2]
records = []
for trial in ('refined', 'precision', 'trtol', 'trtol_alt', 'finalcheck'):
    for mode in ('5V', '33V'):
        stem = R / f'simulation/ltspice/SIM-01_{trial}_{mode}'
        if not stem.with_suffix('.raw').exists():
            continue
        raw = stem.with_suffix('.raw').read_bytes()
        marker = 'Binary:\n'.encode('utf-16-le')
        offset = raw.index(marker)
        header = raw[:offset].decode('utf-16-le')
        variables = int(re.search(r'No. Variables:\s*(\d+)', header)[1])
        record_bytes = 8 + 4 * (variables - 1)
        data = raw[offset + len(marker):]
        n = len(data) // record_bytes
        endpoint = float(np.frombuffer(data[(n-1)*record_bytes:(n-1)*record_bytes+8], '<f8')[0])
        b = stem.with_suffix('.log').read_bytes()
        log = b.decode('utf-16-le' if b[1] == 0 else 'cp1252', errors='replace')
        record = dict(trial=trial, mode=mode, endpoint_s=endpoint,
                      complete='Total elapsed time:' in log and endpoint >= .139999,
                      last_log_line=log.splitlines()[-1])
        if '--archive' in sys.argv:
            target = H / 'results/refined' / trial
            target.mkdir(parents=True, exist_ok=True)
            record['sha256'] = {}
            for ext in ('asc', 'net', 'log', 'raw'):
                f = stem.with_suffix('.' + ext)
                shutil.copy2(f, target / f.name)
                record['sha256'][f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
        records.append(record)
print(json.dumps(records, indent=2))
if '--archive' in sys.argv:
    (H / 'results/refined/manifest.json').write_text(json.dumps(records, indent=2))
