"""Separate SIM-09 load-sensitivity scenarios; nominal circuits are read only."""
from pathlib import Path
import ast,argparse,json,re,hashlib,shutil,os
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];L=R/'simulation/ltspice';D=H/'results/load_sensitivity';D.mkdir(exist_ok=True)
tree=ast.parse((H/'analyze_loop.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'loop_helpers','exec'))
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','ac','analyze','plot']);p.add_argument('--aux',action='store_true');args=p.parse_args()
jobs=[(mode,tag,res) for mode,nom in [('5V',5),('33V',3.3)] for tag,res in [('100mA',nom/.1),('idle',1e6)]]
if args.aux:
 D=H/'results/load_aux';D.mkdir(exist_ok=True);jobs=[(mode,'idle_aux',1e6) for mode in ['5V','33V']]
if args.action=='prepare':
 records=[]
 for mode,tag,res in jobs:
  src=L/f'SIM-09_core_{mode}.cir';s=src.read_text(encoding='cp1252');s=re.sub(r'^RLOAD .*$',f'RLOAD OUT 0 {res:.12g}',s,flags=re.M);prefix=f'SIM-09_load_{mode}_{tag}'
  if args.aux:
   full=(L/f'SIM-08_calibrated_limit_{mode}.net').read_text(encoding='cp1252')
   branch='\n'.join(re.search(r'^'+name+r' .*$',full,re.M)[0] for name in ['XU20','R98','R100','XU18'])+'\n'
   s=s.replace('.op\n',branch+'.op\n')
  (L/f'{prefix}.cir').write_text(s,encoding='cp1252');start=s.replace('.op\n',f'.tran 0 10m 0 200n uic\n.savebias {prefix}.bias time=10m\n.options plotwinsize=0\n')
  (L/f'{prefix}_start.cir').write_text(start,encoding='cp1252');records.append({'mode':mode,'tag':tag,'load_ohm':res,'source':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 (D/'preparation.json').write_text(json.dumps({'scope':'Load sensitivity with nominal fixed auxiliary supplies unchanged; each load has a new settled bias. Not a full-circuit light-load equivalence test.','jobs':records},indent=2)+'\n')
elif args.action=='ac':
 for mode,tag,res in jobs:
  prefix=f'SIM-09_load_{mode}_{tag}';stem=L/f'{prefix}_start';complete(stem);t,v=raw(stem.with_suffix('.raw'));assert t[-1]>=.009999
  assert (L/f'{prefix}.bias').exists()
  s=(L/f'{prefix}.cir').read_text(encoding='cp1252')
  for kind,sign in [('voltage',-1),('current',1)]:
   ss=s.replace('.param lg = 0',f'.param lg = {sign}').replace('.op\n',f'.ac dec 2000 1 60Meg\n.loadbias {prefix}.bias\n.options srcsteps=0\n')
   (L/f'{prefix}_{kind}.cir').write_text(ss,encoding='cp1252')
elif args.action=='analyze':
 result={}
 for mode,tag,res in jobs:
  prefix=f'SIM-09_load_{mode}_{tag}';f,T,_=loop(prefix);m=margins(f,T);_,op=raw(L/f'{prefix}_voltage.op.raw');_,op2=raw(L/f'{prefix}_current.op.raw');t,v=raw(L/f'{prefix}_start.raw')
  assert np.all(np.isfinite(T));assert max(abs(float(op[k])-float(op2[k])) for k in op)<1e-7
  sel=t>.009;drift=float(np.ptp(v['V(out)'][sel]));delta=(float(op['V(out)'])-float(v['V(out)'][-1]))*1e6
  assert drift<1e-6 and abs(delta)<5, ('Unsettled bias',prefix,drift,delta)
  assert abs(float(op['V(out)'])-(5 if mode=='5V' else 3.3))<.005
  m.update({'mode':mode,'tag':tag,'load_ohm':res,'output_V':float(op['V(out)']),'load_A':float(op['I(Rload)']),'start_final_1ms_output_pp_V':drift,'ac_minus_start_output_uV':delta,'current_limit_diode_anode_minus_cathode_V':float(op['V(n040)']-op['V(n061)']),'aux_branch_current_A':float(op.get('I(R98)',0)),'pass_collector_current_A':float(op['Ic(Q26)']),'manifest':[]})
  for suffix,exts in [('', ['cir','bias']),('_start',['cir','raw','log']),('_voltage',['cir','raw','log','op.raw']),('_current',['cir','raw','log','op.raw'])]:m['manifest']+=archive(L/(prefix+suffix),exts)
  np.savetxt(D/f'{mode}_{tag}_loop.csv',np.column_stack([f,T.real,T.imag,20*np.log10(abs(T)),np.unwrap(np.angle(T))*180/np.pi]),delimiter=',',header='frequency_Hz,T_real,T_imag,gain_dB,phase_deg',comments='');result[f'{mode}_{tag}']=m
 (D/'metrics.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='manifest'} for k,v in result.items()},indent=2))
else:
 assert not args.aux, 'Use the main comparison plot for standard load variants; auxiliary results are separate.'
 os.environ.setdefault('MPLCONFIGDIR',str(R/'.cache/matplotlib'))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use(R/'simulation/plotting/report.mplstyle');fig,axes=plt.subplots(2,2,figsize=(7,5),sharex=True);fig.subplots_adjust(left=.12,right=.97,bottom=.13,top=.86,hspace=.15,wspace=.24)
 for col,mode in enumerate(['5V','33V']):
  for folder,name,label,color,style in [(H/'results/core',f'{mode}_loop.csv','1 A','#0072B2','-'),(D,f'{mode}_100mA_loop.csv','0.1 A','#009E73','--'),(D,f'{mode}_idle_loop.csv','1 MOhm','#CC79A7',':')]:
   a=np.loadtxt(folder/name,delimiter=',',skiprows=1);axes[0,col].semilogx(a[:,0],a[:,3],label=label,color=color,ls=style);axes[1,col].semilogx(a[:,0],a[:,4],color=color,ls=style)
  axes[0,col].set_title('5 V mode' if mode=='5V' else '3.3 V mode',fontsize=9);axes[0,col].axhline(0,color='.5',lw=.6);axes[1,col].axhline(-180,color='.5',lw=.6);axes[1,col].set_xlabel('Frequency (Hz)');axes[1,col].set_xlim(1,6e7)
 axes[0,0].set_ylabel('Return ratio (dB)');axes[1,0].set_ylabel('Phase (degrees)');fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',ncol=3)
 for ext in ['png','pdf','svg']:fig.savefig(D/f'SIM-09_load_sensitivity.{ext}',dpi=250)
 plt.close(fig)
print('Completed',args.action)
