"""Rebuild external-capacitance metrics/CSVs from completed LTspice runs.

Usage: python analyze_external.py PATH_TO_PREPARED_LTSPICE_FOLDER
Requires numpy. No simulation, model modification, or smoothing is performed.
"""
from pathlib import Path
import ast,hashlib,json,sys
import numpy as np

home=Path(__file__).resolve().parent
helpers={'np':np}
tree=ast.parse((home/'analyze_loop.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'loop_helpers','exec'),helpers)
source=Path(sys.argv[1]);out=home/'results/external'
old=json.loads((out/'metrics.json').read_text());results={}
for stem,previous in old.items():
 p=source/stem;helpers['complete'](p)
 f,v=helpers['raw'](p.with_suffix('.raw'))
 split=np.flatnonzero(np.diff(f)<0)+1
 assert len(split)==1, f'{stem}: expected two injection steps'
 n=int(split[0]);assert np.array_equal(f[:n],f[n:])
 x=v['V(lgs:x)'];i=v['I(lgs:Vi)']
 q=2*(i[:n]*x[n:]-x[:n]*i[n:])+x[:n]+i[n:]
 T=q/(1-q);f=f[:n]
 m=helpers['margins'](f,T)
 assert len(m['unity_crossings'])==len(m['phase_crossings'])==1
 _,op=helpers['raw'](source/(stem+'.op.raw'))
 m.update({k:previous[k] for k in ['stem','solver','kind','mode','current_A','external_uF','external_series_ohm']})
 m.update(output_bias_V=float(op['V(out)']),load_bias_A=float(op['I(Rload)']))
 assert abs(m['output_bias_V']-({'5V':5.,'33V':3.3}[m['mode']]))<.005
 assert abs(m['load_bias_A']-m['current_A'])<.002
 m['hashes']={ext:hashlib.sha256(p.with_suffix('.'+ext).read_bytes()).hexdigest() for ext in ['asc','net','raw','log']}
 np.savetxt(out/(stem+'.csv'),np.column_stack([f,T.real,T.imag,20*np.log10(abs(T)),np.unwrap(np.angle(T))*180/np.pi]),delimiter=',',header='frequency_Hz,T_real,T_imag,gain_dB,phase_deg',comments='')
 results[stem]=m
(out/'metrics.json').write_text(json.dumps(results,indent=2))
print(f'Validated {len(results)} completed AC cases; metrics and CSVs updated.')
