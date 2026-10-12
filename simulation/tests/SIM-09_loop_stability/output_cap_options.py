"""Compare external output capacitor absent, 1 uF and 10 uF at two loads."""
from pathlib import Path
import ast,argparse,json,re,hashlib,shutil
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];L=R/'simulation/ltspice';D=H/'results/output_cap_options';D.mkdir(exist_ok=True)
tree=ast.parse((H/'analyze_loop.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','analyze']);args=p.parse_args()
if args.action=='prepare':
 jobs=[]
 for mode in ['5V','33V']:
  for load in ['1A','idle']:
   for cap in ['none','1u','10u']:
    for kind in ['voltage','current']:
     src=L/(f'SIM-09_ac_{mode}_{kind}.cir' if load=='1A' else f'SIM-09_load_{mode}_idle_aux_{kind}.cir');s=src.read_text(encoding='cp1252')
     if load=='1A':
      full=(L/f'SIM-08_calibrated_limit_{mode}.net').read_text(encoding='cp1252');branch='\n'.join(re.search(r'^'+n+r' .*$',full,re.M)[0] for n in ['XU20','R98','R100','XU18'])+'\n';s=s.replace('.end\n',branch+'.end\n')
     if cap=='none':s=re.sub(r'^CLOAD .*\n','',s,flags=re.M);s=re.sub(r'^R[^\n]* OUT N016 [^\n]*\n','',s,flags=re.M)
     else:s=re.sub(r'^CLOAD .*$',f'CLOAD N016 0 {cap}',s,flags=re.M)
     s=s.replace('.ac dec 200 1 60Meg','.ac dec 2000 1 60Meg').replace('.end\n','.save V(out) V(fb) V(n033) V(lgs:x) I(lgs:Vi) I(Rload) V(n040) V(n061)\n.end\n')
     target=L/f'SIM-09_outcap_{mode}_{load}_{cap}_{kind}.cir';target.write_text(s,encoding='cp1252');jobs.append({'file':target.name,'source':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'external_C':cap,'series_resistor_ohm':None if cap=='none' else 1})
 (D/'preparation.json').write_text(json.dumps({'scope':'Fixed auxiliary biases; restored output-connected auxiliary branch; 27 C; 1 A or 1 Mohm load. Intrinsic capacitor ESR not included. No-cap removes only output capacitor and its series resistor, not internal compensation.','jobs':jobs},indent=2)+'\n')
else:
 results={}
 for mode in ['5V','33V']:
  for load in ['1A','idle']:
   for cap in ['none','1u','10u']:
    prefix=f'SIM-09_outcap_{mode}_{load}_{cap}';f,T,_=loop(prefix);m=margins(f,T);_,op=raw(L/f'{prefix}_voltage.op.raw');_,oi=raw(L/f'{prefix}_current.op.raw');assert abs(op['V(out)']-oi['V(out)'])<1e-7
    assert abs(op['V(out)']-(5 if mode=='5V' else 3.3))<.005 and op['V(n040)']<op['V(n061)']
    m.update({'output_V':float(op['V(out)']),'load_A':float(op['I(Rload)']),'manifest':[]})
    for kind in ['voltage','current']:m['manifest']+=archive(L/f'{prefix}_{kind}',['cir','log','raw','op.raw'])
    np.savetxt(D/f'{mode}_{load}_{cap}.csv',np.column_stack([f,T.real,T.imag,20*np.log10(abs(T)),np.unwrap(np.angle(T))*180/np.pi]),delimiter=',',header='frequency_Hz,T_real,T_imag,gain_dB,phase_deg',comments='');results[f'{mode}_{load}_{cap}']=m
 (D/'metrics.json').write_text(json.dumps(results,indent=2)+'\n')
 for key,m in results.items():print(key,m['unity_crossings'],m['phase_crossings'])
print('Completed',args.action)
