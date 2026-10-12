"""Build the 36-case archive from the owner's accepted folder, without altering it.

No simulator, RAW files, generated netlists, old runs or optional diagnostics.
Copies only declared model dependencies and the symbol dependency closure.
Third-party notices are preserved; this tool does not grant redistribution rights.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--models', type=Path, required=True)
    p.add_argument('--ltspice-lib', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    dest = args.destination.resolve()
    if dest.exists() or Path(str(dest)+'.zip').exists():
        p.error('Destination or ZIP exists; choose a new path.')
    if repo == dest or repo in dest.parents:
        p.error('Build outside the source checkout.')
    main_cases = json.loads((repo/'simulation/launchers/scenario_catalog.json').read_text())
    extra = json.loads((repo/'simulation/launchers/supplementary_catalog.json').read_text())
    extra = [c for c in extra if c['stem'].startswith('SIM-09_external_')]
    assert len(main_cases) == 16 and len(extra) == 20
    cases = main_cases + extra
    for case in cases:
        case["label"] = case["stem"].replace("_", " ")
    files = {}
    roles = {}

    def add(src, rel, role):
        assert src.is_file(), f'Missing {src}'
        if rel in files:
            assert sha(files[rel]) == sha(src), f'Conflicting dependency {rel}'
        files[rel] = src
        roles[rel] = role

    for c in cases:
        for ext in ('.asc', '.plt'):
            name = c['stem'] + ext
            src = args.models/name
            frozen = repo/'simulation/ltspice'/name
            assert sha(src) == sha(frozen), f'Local edit since freeze: {name}'
            add(src, name, 'validated scenario' if ext == '.asc' else 'saved plot')

    queue = [name for name in files if name.endswith('.asc')]
    scanned = set()
    while queue:
        rel = queue.pop()
        if rel in scanned:
            continue
        scanned.add(rel)
        data = files[rel].read_bytes().decode('cp1252')
        if rel.endswith('.asc'):
            for name in re.findall(r'^SYMBOL (\S+) ', data, re.M):
                name = name.replace('\\', '/')
                name = re.sub('/+', '/', name) + '.asy'
                src = args.models/name
                if not src.exists():
                    src = args.ltspice_lib/'sym'/name
                add(src, name, 'symbol')
                queue.append(name)
        if rel.endswith('.asy') and 'SymbolType BLOCK' in data and not re.search(r'^SYMATTR Prefix ', data, re.M):
            asc = str(Path(rel).with_suffix('.asc'))
            add(args.models/asc, asc, 'hierarchical probe')
            queue.append(asc)
        # Active schematic directive blocks and symbol model-file attributes.
        blocks = re.findall(r'^TEXT .*? !([^\r\n]*)', data, re.M)
        directive_text = '\n'.join(blocks).replace('\\n', '\n')
        for kind, name in re.findall(r'^\s*\.(lib|inc|include|loadbias)\s+([^\s]+)', directive_text, re.M | re.I):
            name = name.strip('"')
            assert ':' not in name and '..' not in Path(name).parts, name
            src = args.models/name
            if not src.exists():
                src = args.ltspice_lib/'sub'/name
            add(src, name, 'bias' if kind.lower() == 'loadbias' else 'model library')
        for name in re.findall(r'^SYMATTR ModelFile ([^\r\n]+)', data, re.M):
            name = name.strip().strip('"')
            assert ':' not in name, f'Absolute symbol dependency: {rel}: {name}'
            src = args.models/name
            if not src.exists():
                src = args.ltspice_lib/'sub'/name
            add(src, name, 'model library')

    # LTspice may insert these automatically when netlisting primitive devices.
    for name in ['standard.bjt', 'standard.dio', 'standard.jft', 'standard.mos']:
        src = args.models/name
        if not src.exists():
            src = args.ltspice_lib/'cmp'/name
        add(src, name, 'standard models')
    dest.mkdir(parents=True)
    for rel, src in files.items():
        target = dest/'Simulaciones'/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    rows = [dict(file='Simulaciones/'+rel, bytes=src.stat().st_size,
                 sha256=sha(src), role=roles[rel]) for rel, src in sorted(files.items())]
    (dest/'MANIFEST.json').write_text(json.dumps({
        'baseline': 'simulations-v1.0 / d26b998',
        'scenario_count': 36, 'cases': cases, 'files': rows,
        'third_party_redistribution_permissions': 'Not established for all supplied dependencies; original notices retained.',
    }, indent=2)+'\n', encoding='utf-8')
    readme = (repo/'simulation/PACKAGE_README.md').read_text(encoding='utf-8')
    (dest/'README.md').write_text(readme + '\n' + ''.join(
        f'| `{c["stem"]}.asc` | {"Alternate" if c["solver"] == "alt" else "Normal"} |\n'
        for c in cases), encoding='utf-8')
    archive = Path(str(dest)+'.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src in sorted(dest.rglob('*')):
            if src.is_file():
                z.write(src, src.relative_to(dest).as_posix())
    digest = sha(archive)
    archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'sha256': digest, 'dependencies_and_cases': len(files),
                      'scenarios': 36}, indent=2))


if __name__ == '__main__':
    main()
