"""One-factor sensitivity of the nearly unloaded, auxiliary-restored SIM-09 core."""
from pathlib import Path
import ast,argparse,json,re,hashlib,os,shutil
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];L=R/'simulation/ltspice';D=H/'results/cap_esr';D.mkdir(exist_ok=True)
tree=ast.parse((H/'analyze_loop.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','analyze','plot']);args=p.parse_args()
cases=[('nominal',1,1),('C080',.8,1),('C120',1.2,1),('ESR010',1,.1),('ESR300',1,3)]
if args.action=='prepare':
 jobs=[]
 for mode in ['5V','33V']:
  for tag,cap,esr in cases:
   for kind in ['voltage','current']:
    source=L/f'SIM-09_load_{mode}_idle_aux_{kind}.cir';s=source.read_text(encoding='cp1252');s=re.sub(r'^CLOAD .*$',f'CLOAD N016 0 {cap}u',s,flags=re.M);s=re.sub(r'^(R\S+ OUT N016) .*$',lambda m:m[1]+f' {esr}',s,flags=re.M)
    s=s.replace('.end\n','.save V(out) V(fb) V(n033) V(lgs:x) I(lgs:Vi) I(Rload) V(n040) V(n061)\n.end\n')
    target=L/f'SIM-09_ce_{mode}_{tag}_{kind}.cir';target.write_text(s,encoding='cp1252');jobs.append({'file':target.name,'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'C_uF':cap,'ESR_ohm':esr})
 (D/'preparation.json').write_text(json.dumps({'date':'2026-09-21','scope':'One-factor diagnostic variations; not a real capacitor tolerance specification. 1 Mohm load, restored output auxiliary branch, fixed nominal supplies, 27 C.','solver':'Alternate','jobs':jobs},indent=2)+'\n')
elif args.action=='analyze':
 out={};baseline=json.loads((H/'results/load_aux/metrics.json').read_text())
 for mode in ['5V','33V']:
  for tag,cap,esr in cases:
   prefix=f'SIM-09_ce_{mode}_{tag}';f,T,_=loop(prefix);m=margins(f,T);_,op=raw(L/f'{prefix}_voltage.op.raw');_,oi=raw(L/f'{prefix}_current.op.raw');delta=(float(op['V(out)'])-baseline[f'{mode}_idle_aux']['output_V'])*1e6
   assert abs(delta)<5 and abs(op['V(out)']-oi['V(out)'])<1e-7
   assert op['V(n040)']<op['V(n061)'] and np.all(np.isfinite(T))
   m.update({'C_uF':cap,'ESR_ohm':esr,'output_V':float(op['V(out)']),'bias_output_delta_uV':delta,'load_A':float(op['I(Rload)']),'manifest':[]})
   for kind in ['voltage','current']:m['manifest']+=archive(L/f'{prefix}_{kind}',['cir','log','raw','op.raw'])
   np.savetxt(D/f'{mode}_{tag}.csv',np.column_stack([f,T.real,T.imag,20*np.log10(abs(T)),np.unwrap(np.angle(T))*180/np.pi]),delimiter=',',header='frequency_Hz,Treal,Timag,gain_dB,phase_deg',comments='');out[f'{mode}_{tag}']=m
 (D/'metrics.json').write_text(json.dumps(out,indent=2)+'\n')
 for key,m in out.items():print(key,'PM',m['unity_crossings'],'GM',m['phase_crossings'])
else:
 os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 m=json.loads((D/'metrics.json').read_text());plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(1,2,figsize=(7,3))
 for mode,col,label in [('5V','#0072B2','5 V'),('33V','#009E73','3.3 V')]:
  for ax,tags,xx in [(axes[0],['C080','nominal','C120'],[.8,1,1.2]),(axes[1],['ESR010','nominal','ESR300'],[.1,1,3])]:
   ax.plot(xx,[m[f'{mode}_{tag}']['unity_crossings'][0]['phase_margin_deg'] for tag in tags],'-o',color=col,label=label)
 axes[0].set_xlabel('Output capacitance (uF), ESR = 1 ohm');axes[1].set_xlabel('ESR (ohm), output capacitance = 1 uF');axes[0].set_ylabel('Phase margin (degrees)');axes[1].legend();fig.tight_layout()
 for ext in ['png','pdf','svg']:fig.savefig(D/f'SIM09_cap_esr.{ext}',dpi=250)
print('Completed',args.action)
