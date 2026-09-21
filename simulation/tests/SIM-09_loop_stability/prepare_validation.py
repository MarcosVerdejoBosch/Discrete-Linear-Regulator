from pathlib import Path
import numpy as np,re,json
H=Path(__file__).resolve().parent;R=H.parents[2];r=R/'simulation/ltspice';jobs=[]
for mode in ['5V','33V']:
 fc=json.loads((H/'results/core/metrics.json').read_text())[mode]['unity_crossings'][0]['frequency_Hz']
 s=(r/f'SIM-02_cal_02_{mode}.asc').read_bytes().decode('cp1252')
 # Keep the original zero-amplitude probe and insert a tone through its voltage source.
 # Its subcircuit is embedded by the symbol; use a netlist derivative to set the source.
 s=(r/f'SIM-02_cal_02_{mode}.net').read_text(encoding='cp1252');s=s.replace('XLGS N033 FB lg_single params: lg_single=lg',f'VTEST N033 FB SINE(0 500u {fc:.12g} 80m)')
 s=s.replace('.tran 0 80m 0 2u','.tran 0 80.25m 0 2u');s=s.replace('.save V(VBAT)', '.save V(N033) V(FB) V(VEE) V(VDOBL) V(VBAT)')
 s=s.replace('.end\n','BRES SIM09_TIMESTEP 0 V=table(time,0,0,79.99m,0,80.25m,260) tripdv=0.001 tripdt=10n\n.end\n')
 q=r/f'SIM-09_full_tone_{mode}.cir';q.write_text(s,encoding='cp1252');jobs.append(dict(mode=mode,frequency_Hz=fc,amplitude_V=.0005,source=q.name,fit_window_ms=[80.05,80.25]))
(H/'results/core/tone_tests.json').write_text(json.dumps(jobs,indent=2))
# Analytic cross-check: return ratio 100/(1+s*0.001).
for tag,p in [('voltage',-1),('current',1)]:
 s=f'''Analytic probe check
R1 OUT 0 1k
C1 OUT 0 1u
G1 OUT 0 A 0 .1
Ii 0 X AC {{u(prb)}}
Vi X A AC {{u(-prb)}}
VBUFFER OUT X 0
.param prb={p}
.ac dec 100 1 1Meg
.end
''';(r/f'SIM-09_analytic_{tag}.cir').write_text(s)
