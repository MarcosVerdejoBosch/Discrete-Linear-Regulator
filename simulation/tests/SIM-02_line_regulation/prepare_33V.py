"""Create selector-off pilot, retaining the baseline divider adjustment."""
from pathlib import Path
import re, json, hashlib
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT/'simulation/ltspice/SIM-02_full_line_5V_pilot.asc'
text = source.read_bytes().decode('cp1252')
chunks = text.split('SYMBOL ')
removed = [c for c in chunks if re.search(r'^SYMATTR InstName R62\s*$', c, re.M)]
assert len(removed) == 1
text = 'SYMBOL '.join(c for c in chunks if c not in removed)
assert '.param RLOADVAL=5' in text
text = text.replace('.param RLOADVAL=5', '.param RLOADVAL=3.3')
target = ROOT/'simulation/ltspice/SIM-02_full_line_33V_pilot.asc'
target.write_bytes(text.encode('cp1252'))
dest = HERE/'results/full_circuit_33V'
dest.mkdir(exist_ok=True)
(dest/'preparation.json').write_text(json.dumps({
    'source': str(source.relative_to(ROOT)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'test': str(target.relative_to(ROOT)),
    'test_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'changes': ['Remove selector gate feed R62; retain R60 pull-down to turn U8 off',
                'Load 3.3 ohm; preserve R33=14.5k, RFB1=15k, RFB2=25k'],
    'conditions': '8 V source, 27 C, 80 ms transient, maximum step 2 us',
    'status': 'Uncalibrated selector-off pilot, awaiting execution'
}, indent=2)+'\n')
print(target)
