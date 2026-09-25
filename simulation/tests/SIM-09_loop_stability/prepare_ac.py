from pathlib import Path
r=Path(__file__).resolve().parents[3]/'simulation/ltspice'
for mode in ['5V','33V']:
 assert (r/f'SIM-09_core_{mode}.bias').exists()
 s=(r/f'SIM-09_core_{mode}.cir').read_text(encoding='cp1252')
 for label,sign in [('voltage',-1),('current',1)]:
  ss=s.replace('.param lg = 0',f'.param lg = {sign}').replace('.op\n',f'.ac dec 200 1 60Meg\n.loadbias SIM-09_core_{mode}.bias\n.options srcsteps=0\n');(r/f'SIM-09_ac_{mode}_{label}.cir').write_text(ss,encoding='cp1252')

for bias in [14,16]:
 for kind in ['voltage','current']:
  s=(r/f'SIM-09_ac_5V_{kind}.cir').read_text(encoding='cp1252').replace('VDBL_BIAS VDOBL 0 14.9',f'VDBL_BIAS VDOBL 0 {bias}')
  (r/f'SIM-09_check_dbl{bias}_{kind}.cir').write_text(s,encoding='cp1252')

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
