"""Build the frozen hardware payload; no KiCad editing or export is performed."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
manifest = json.loads((root / "hardware/HARDWARE_FREEZE.json").read_text())
records = manifest["files"] + [manifest["manufacturing_archive"]]
for record in records:
    actual = hashlib.sha256((root / record["path"]).read_bytes()).hexdigest()
    if actual != record["sha256"]:
        raise SystemExit("Frozen source changed: " + record["path"])
paths = [r["path"] for r in records] + [
    "hardware/exports/Regulador_schematic.pdf", "hardware/HARDWARE_FREEZE.json",
    "hardware/README.md", "LICENSE",
]
prefix = "Discrete-Linear-Regulator-KiCad-v1.0/"
archive = args.output / "Discrete-Linear-Regulator-KiCad-v1.0.zip"
with ZipFile(archive, "w", ZIP_DEFLATED, compresslevel=9) as z:
    checksums = []
    for path in paths:
        content = (root / path).read_bytes()
        z.writestr(prefix + path, content)
        checksums.append(hashlib.sha256(content).hexdigest() + "  " + path)
    z.writestr(prefix + "SHA256SUMS.txt", "\n".join(checksums) + "\n")
    z.writestr(prefix + "README.txt", "Open hardware/README.md for instructions.\nOpen hardware/kicad/Regulador.kicad_pro in KiCad 9.\nOriginal fabrication archive: hardware/manufacturing/Manufacturing_Regulador.zip\nInstalled BOM and quantitative bench characterization remain pending.\n")
print(json.dumps({"file": str(archive.resolve()), "bytes": archive.stat().st_size,
                  "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))
