"""Extract the existing real, point-major LTspice DC records, without rerunning."""
from pathlib import Path
import json, re
import numpy as np

HERE = Path(__file__).resolve().parent
folder = HERE / 'results/imported_dc'
summary = []
for name, nominal, load in [('TEST_DROPOUT', 5., 5.), ('TEST_DROPOUT_33V', 3.3, 3.3)]:
    raw = (folder / (name + '.raw')).read_bytes()
    marker = 'Binary:\n'.encode('utf-16-le')
    pos = raw.find(marker)
    if pos < 0:
        marker = 'Binary:\r\n'.encode('utf-16-le'); pos = raw.find(marker)
    if pos < 0:
        raise ValueError('Unsupported raw header')
    header = raw[:pos].decode('utf-16-le')
    nv = int(re.search(r'No. Variables:\s*(\d+)', header)[1])
    points = int(re.search(r'No. Points:\s*(\d+)', header)[1])
    variables = re.findall(r'^\s*(\d+)\s+(\S+)\s+\S+\s*$', header.rsplit('Variables:', 1)[1], re.M)
    indexes = {label.lower(): int(i) for i, label in variables}
    assert 'Flags: real forward' in header
    dtype = np.dtype([('sweep', '<f8'), ('values', '<f4', (nv-1,))])
    body = raw[pos+len(marker):]
    assert len(body) == points * dtype.itemsize
    data = np.frombuffer(body, dtype=dtype)
    vin = data['sweep']; vout = data['values'][:, indexes['v(out)']-1].astype(float)
    assert np.isfinite(vout).all() and np.all(np.diff(vin) > 0)
    keep = (vin >= 6-1e-9) & (vin <= 11+1e-9)
    output = HERE / 'results' / (name + '_line.txt')
    np.savetxt(output, np.column_stack([vin[keep], vout[keep]]),
               header='Vin_V\tVout_V', comments='', delimiter='\t', fmt='%.10g')
    v6, v11 = np.interp([6, 11], vin, vout)
    row = dict(source=name, nominal_V=nominal, load_ohm=load,
               temperature_C=27, vout_at_6_V=float(v6), vout_at_11_V=float(v11),
               slope_mV_per_V=float(1000*(v11-v6)/5),
               minimum_V=float(vout[keep].min()), maximum_V=float(vout[keep].max()),
               note='Existing DC run; resistive load. No new LTspice run.')
    summary.append(row)
(HERE / 'results/metrics.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
