from pathlib import Path
import re,json,sys,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'results/core';D.mkdir(parents=True,exist_ok=True)
def read(p):
 b=p.read_bytes();mark='Binary:\n'.encode('utf-16-le');k=b.find(mark);h=b[:k].decode('utf-16-le');nv=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);names=[x.split()[1] for x in h.rsplit('Variables:',1)[1].splitlines() if x.strip()];a=np.frombuffer(b[k+len(mark):],np.dtype([('t','<f8'),('v','<f4',(nv-1,))]));return a['t'],dict(zip(names[1:],a['v'].astype(float).T))
def avg(t,y):
 m=(t>.07)&(t<.08);x=np.r_[.07,t[m],.08];return float(np.trapezoid(np.interp(x,t,y),x)/.01)
records={}
for mode,nom in [('5V',5),('33V',3.3)]:
 full=(R/f'simulation/ltspice/SIM-02_cal_02_{mode}.net').read_text(encoding='cp1252');t,v=read(R/f'simulation/ltspice/SIM-08_calibrated_limit_{mode}.raw');bias={k:avg(t,v[k]) for k in ['V(vee)','V(vctrl)','V(vref)','V(ttl)','V(out)']}
 core=full[:full.index('XU3 ')];remove=['VBAT','V5','V10','XU1','Q23','Q24','R23','R24','R26','XU5']
 for name in remove:core=re.sub(r'^'+name+r' .*\n','',core,flags=re.M)
 for name in ['R67','D13','R11','D1','R60','R62','D6','J3','R99','R63','R61']:
  z=re.search(r'^'+name+r' .*$',full,re.M)
  if z:core+=z[0]+'\n'
 directives=full[full.index('* block symbol definitions'):];directives=re.sub(r'^\.(tran|save|meas|options).*\n','',directives,flags=re.M)
 core+=directives
 core=core.replace('.end\n',f'VEE_BIAS VEE 0 {bias["V(vee)"]:.12g}\nVCTRL_BIAS VCTRL 0 {bias["V(vctrl)"]:.12g}\nVREF_BIAS VREF 0 {bias["V(vref)"]:.12g}\nVEN_BIAS TTL 0 {bias["V(ttl)"]:.12g}\nVDBL_BIAS VDOBL 0 14.9\n.op\n.end\n')
 (R/f'simulation/ltspice/SIM-09_core_{mode}.cir').write_text(core,encoding='cp1252');records[mode]=bias
(D/'bias_reference.json').write_text(json.dumps(records,indent=2))

for mode in ['5V','33V']:
 p=R/f'simulation/ltspice/SIM-09_core_{mode}.cir';s=p.read_text(encoding='cp1252')
 s=s.replace('.op\n',f'.tran 0 10m 0 200n uic\n.savebias SIM-09_core_{mode}.bias time=10m\n.options plotwinsize=0\n')
 (p.parent/f'SIM-09_core_start_{mode}.cir').write_text(s,encoding='cp1252')
