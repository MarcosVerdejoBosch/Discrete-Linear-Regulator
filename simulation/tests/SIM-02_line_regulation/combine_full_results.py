"""Combine explicitly identified operating-point histories; never relabel a failed sweep."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
p=HERE/'results/full_circuit'
low=json.loads((p/'SIM-02_full_line_5V_inspection.json').read_text())['completed_steps']
high=json.loads((p/'line_change_metrics.json').read_text())
assert [r['source_V'] for r in low]==[6,7,8,9] and high['all_steps_completed']
highrows=high['results']
assert abs(low[2]['vout_avg_V']-highrows[0]['vout_avg_V'])<1e-6
rows=[]
for r in low:
 r['history']='Independent startup, average 70--80 ms';rows.append(r)
for r in highrows[1:]:
 r['history']='Input increased after startup at 8 V; average last 10 ms';rows.append(r)
assert all(r['enable_min_V']>5 for r in rows)
assert all(abs(r['drift_mV'])<.001 for r in rows)
result={'mode':'5 V','load_ohm':5,'temperature_C':27,
 'results':rows,'endpoint_slope_mV_per_V':1000*(rows[-1]['vout_avg_V']-rows[0]['vout_avg_V'])/5,
 'scope':'Combined complete operating points from two transient runs; not a completed independent-startup sweep.',
 'numerical_note':'Modified trap, max step 2 us. Gear/1 us cross-check at 8 V agrees within 0.1 uV.'}
(p/'sweep_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['endpoint_slope_mV_per_V'])
