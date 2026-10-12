from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch


def read_raw(path):
    b = path.read_bytes()
    for ending in ['Binary:\n', 'Binary:\r\n']:
        marker = ending.encode('utf-16-le')
        offset = b.find(marker)
        if offset >= 0:
            break
    if offset < 0:
        raise ValueError('No binary RAW header: ' + str(path))
    header = b[:offset].decode('utf-16-le')
    if 'Flags: complex' not in header:
        raise ValueError('Expected AC complex data')
    names = [line.split()[1] for line in header.rsplit('Variables:', 1)[1].splitlines() if line.strip()]
    a = np.frombuffer(b[offset+len(marker):], '<c16').reshape(-1, len(names))
    return a[:, 0].real, dict(zip(names[1:], a[:, 1:].T))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--plot-only', action='store_true', help='Redraw existing completed RAW results without running LTspice')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    exe = Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
    results = folder / 'Resultados_SIM09'
    results.mkdir(exist_ok=True)
    curves = []
    report = {'scope': 'Nominal fixed-bias main loop; approximately 1 A, 27 C, 1 uF and external 1 ohm. Not hardware validation.', 'modes': {}}
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.alpha': .22})
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True, constrained_layout=True)
    for mode, color in [('5V', '#0072B2'), ('33V', '#D55E00')]:
        stem = folder / f'SIM-09_loop_{mode}'
        source = stem.with_suffix('.asc')
        manifest = []
        print(f'{"Leyendo" if args.plot_only else "Ejecutando"} {stem.name}...', flush=True)
        if not args.plot_only:
            for suffix in ['.log', '.raw', '.op.raw']:
                stem.with_suffix(suffix).unlink(missing_ok=True)
            subprocess.run([str(exe), '-alt', '-b', '-Run', str(source)], cwd=folder, check=True)
        logbytes = stem.with_suffix('.log').read_bytes()
        log = logbytes.decode('utf-16-le' if len(logbytes)>1 and logbytes[1]==0 else 'cp1252')
        if 'Total elapsed time:' not in log or 'Fatal Error' in log:
            raise RuntimeError('Incomplete simulation: ' + stem.name)
        frequencies, vectors = read_raw(stem.with_suffix('.raw'))
        boundaries = np.r_[0, np.flatnonzero(np.diff(frequencies)<0)+1, len(frequencies)]
        if len(boundaries)!=3:
            raise ValueError('Expected exactly two steps: lg=-1 then lg=+1')
        if not re.search(r'\.step\s+param\s+lg\s+list\s+-1\s+1', source.read_bytes().decode('cp1252'), re.I):
            raise ValueError('Step order must be voltage (-1), then current (+1)')
        data = {}
        for j, injection in enumerate(['voltage','current']):
            lo,hi = boundaries[j:j+2]
            data[injection] = frequencies[lo:hi], {name: values[lo:hi] for name,values in vectors.items()}
        for suffix in ['.asc', '.net', '.raw', '.log']:
            p = stem.with_suffix(suffix)
            manifest.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        f, v = data['voltage']
        ff, i = data['current']
        if not np.array_equal(f, ff):
            raise ValueError('Injection frequency grids differ')
        q = 2*(v['I(lgs:Vi)']*i['V(lgs:x)']-v['V(lgs:x)']*i['I(lgs:Vi)'])+v['V(lgs:x)']+i['I(lgs:Vi)']
        t = q/(1-q)
        mag = 20*np.log10(abs(t))
        phase = np.unwrap(np.angle(t))*180/np.pi
        crosses = np.flatnonzero((mag[:-1]>=0)!=(mag[1:]>=0))
        pcross = np.flatnonzero((phase[:-1]>=-180)!=(phase[1:]>=-180))
        if len(crosses)!=1 or len(pcross)!=1:
            raise ValueError('Multiple or missing crossings: inspect full loop response before reporting one margin.')
        j = crosses[0]
        w = -mag[j]/(mag[j+1]-mag[j])
        fc = 10**(np.log10(f[j])+w*np.log10(f[j+1]/f[j]))
        pm = 180+phase[j]+w*(phase[j+1]-phase[j])
        j = pcross[0]
        w = (-180-phase[j])/(phase[j+1]-phase[j])
        gm = -(mag[j]+w*(mag[j+1]-mag[j]))
        f180 = 10**(np.log10(f[j])+w*np.log10(f[j+1]/f[j]))
        curves.append((mode,color,f,mag,phase,float(f180),float(gm)))
        report['modes'][mode] = {'phase_margin_deg': float(pm), 'gain_margin_dB': float(gm), 'crossover_Hz': float(fc), 'phase_crossover_Hz': float(f180), 'manifest': manifest}
        label = f'{"5 V" if mode=="5V" else "3.3 V"}: PM {pm:.1f} deg, GM {gm:.1f} dB'
        axes[0].semilogx(f, mag, color=color, label=label, linewidth=1.3)
        axes[1].semilogx(f, phase, color=color, linewidth=1.3)
        phase_at_fc = pm - 180
        fig.add_artist(ConnectionPatch(xyA=(fc, 0), xyB=(fc, phase_at_fc), coordsA='data', coordsB='data', axesA=axes[0], axesB=axes[1], color=color, linestyle=':', linewidth=1.1, alpha=.85))
        axes[0].plot(fc, 0, 'o', color=color, markersize=3)
        axes[1].plot(fc, phase_at_fc, 'o', color=color, markersize=3)
        axes[1].annotate('', xy=(fc, phase_at_fc), xytext=(fc, -180), arrowprops=dict(arrowstyle='<->', color=color, linewidth=1))
        offset = (28, 16) if mode == '5V' else (-98, -28)
        axes[1].annotate(f'{pm:.1f} deg', xy=(fc, (phase_at_fc-180)/2), xytext=offset, textcoords='offset points', color=color, fontsize=9, arrowprops=dict(arrowstyle='-', color=color, linewidth=.7), bbox=dict(facecolor='white', edgecolor='none', alpha=.9, pad=2))
        np.savetxt(results/f'{mode}_loop.csv', np.column_stack([f, mag, phase]), delimiter=',', header='frequency_Hz,gain_dB,phase_deg', comments='')
        print(f'{mode}: PM={pm:.2f} deg; GM={gm:.2f} dB; fc={fc/1000:.2f} kHz', flush=True)
    axes[0].axhline(0, color='.4', linestyle='--', linewidth=.8)
    axes[1].axhline(-180, color='.4', linestyle='--', linewidth=.8)
    axes[0].set_ylabel('Loop gain (dB)')
    axes[1].set_ylabel('Phase (deg)')
    axes[1].set_xlabel('Frequency (Hz)')
    axes[0].legend(frameon=False, fontsize=9)
    axes[0].set_title('SIM-09 | Nominal regulation loop', loc='left', fontsize=11, fontweight='normal')
    for ax in axes:
        ax.set_xlim(1, 60e6)
    for suffix in ['png', 'pdf']:
        fig.savefig(results/f'SIM09_bode.{suffix}', dpi=180)
    gainfig, gainaxes = plt.subplots(2, 1, figsize=(8,6), sharex=True, constrained_layout=True)
    for mode,color,f,mag,phase,f180,gm in curves:
        gainaxes[0].semilogx(f,mag,color=color,linewidth=1.3,label=('5 V' if mode=='5V' else '3.3 V'))
        gainaxes[1].semilogx(f,phase,color=color,linewidth=1.3)
        gainfig.add_artist(ConnectionPatch(xyA=(f180,-180),xyB=(f180,-gm),coordsA='data',coordsB='data',axesA=gainaxes[1],axesB=gainaxes[0],color=color,linestyle=':',linewidth=1.1))
        gainaxes[1].plot(f180,-180,'o',color=color,markersize=3)
        gainaxes[0].plot(f180,-gm,'o',color=color,markersize=3)
        gainaxes[0].plot([f180,f180],[-gm,0],color=color,linewidth=.9,marker='_',markersize=7,markeredgewidth=.9)
        gainaxes[0].annotate(f'{gm:.1f} dB',xy=(f180,-gm/2),xytext=((30,30) if mode=='5V' else (-105,5)),textcoords='offset points',color=color,fontsize=9,arrowprops=dict(arrowstyle='-',color=color,linewidth=.7),bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=2))
    gainaxes[0].axhline(0,color='.4',linestyle='--',linewidth=.8)
    gainaxes[1].axhline(-180,color='.4',linestyle='--',linewidth=.8)
    gainaxes[0].set_ylabel('Loop gain (dB)')
    gainaxes[1].set_ylabel('Phase (deg)')
    gainaxes[1].set_xlabel('Frequency (Hz)')
    gainaxes[0].legend(frameon=False,fontsize=9)
    gainaxes[0].set_title('SIM-09 | Gain margin',loc='left',fontsize=11,fontweight='normal')
    for ax in gainaxes: ax.set_xlim(1,60e6)
    for suffix in ['png','pdf']: gainfig.savefig(results/f'SIM09_gain_margin.{suffix}',dpi=180)
    (results/'margenes.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Resultados guardados en ' + str(results))
    if args.open:
        os.startfile(results/'SIM09_bode.png')
        os.startfile(results/'SIM09_gain_margin.png')


if __name__ == '__main__':
    main()
