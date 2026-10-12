"""Export the unmodified KiCad front silkscreen and annotate PCB landmarks.

Requires KiCad 9 CLI, pypdf, reportlab and pypdfium2. Run with --kicad-cli
when the executable is not on PATH. Annotations use board coordinates (mm).
"""
import argparse
import io
from pathlib import Path
import subprocess
import tempfile

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.pdfgen import canvas
import pypdfium2

ROOT = Path(__file__).resolve().parents[2]
MM = 72 / 25.4
# Actual board outline from Edge.Cuts; the PDF export uses sheet coordinates.
X0, Y0, X1, Y1 = 246.89, 78.785, 446.89, 238.785
MARKERS = [
    (1, (378, 96), (379, 107), "Error amplifier", "CA3096 arrays U1-U3"),
    (2, (358, 140), (366, 133), "Output-voltage adjustment", "Feedback trimmers RV1 and RV2"),
    (3, (380, 159), (392.43, 151.13), "Series pass device", "TIP42C (Q_PASS)"),
    (4, (321, 188), (339.09, 166), "Protection and current control", "LM324 (U4)"),
    (5, (282, 128), (300, 138), "Supervisory comparators", "LM339 (U7)"),
    (6, (437, 129), (426.72, 142.24), "Reverse-polarity protection", "IRF4905 (Q_POL)"),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-cli', default='kicad-cli')
    args = parser.parse_args()
    output = ROOT / 'docs/figures/pcb_placement.pdf'
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory) / 'placement.pdf'
        subprocess.run([args.kicad_cli, 'pcb', 'export', 'pdf', '--layers',
                        'F.Silkscreen,Edge.Cuts', '--mode-single', '--black-and-white',
                        '-o', str(base), str(ROOT / 'hardware/kicad/Regulador.kicad_pcb')], check=True)
        page = PdfReader(base).pages[0]
        height = float(page.mediabox.height)
        left, bottom = X0 * MM - 1, height - Y1 * MM - 1
        width, board_height = (X1-X0)*MM+2, (Y1-Y0)*MM+2
        page.cropbox = RectangleObject([left, bottom, left+width, bottom+board_height])
        page.trimbox = page.cropbox
        w, h = width+30, board_height+116
        writer = PdfWriter()
        target = writer.add_blank_page(width=w, height=h)
        target.merge_transformed_page(page, Transformation().translate(15-left, 106-bottom))
        stream = io.BytesIO()
        c = canvas.Canvas(stream, pagesize=(w,h))
        def point(p):
            return 16+(p[0]-X0)*MM, 107+(Y1-p[1])*MM
        def badge(n,x,y):
            c.setFillColorRGB(1,1,1)
            c.setStrokeColorRGB(.10,.28,.36)
            c.setLineWidth(1.1)
            c.circle(x,y,7,stroke=1,fill=1)
            c.setFillColorRGB(.10,.28,.36)
            c.setFont('Helvetica-Bold',9)
            c.drawCentredString(x,y-3,str(n))
        for n, position, anchor, title, detail in MARKERS:
            x,y=point(position); ax,ay=point(anchor)
            c.setStrokeColorRGB(.10,.28,.36); c.setLineWidth(.8)
            c.line(x,y,ax,ay)
            badge(n,x,y)
            col=(n-1)//3; row=(n-1)%3
            lx=24+col*(w/2); ly=83-row*29
            badge(n,lx,ly)
            c.setFillColorRGB(.12,.12,.12); c.setFont('Helvetica',10)
            c.drawString(lx+13,ly+1,title)
            c.setFont('Helvetica',8.5); c.setFillColorRGB(.35,.35,.35)
            c.drawString(lx+13,ly-11,detail)
        c.save(); stream.seek(0)
        target.merge_page(PdfReader(stream).pages[0])
        writer.add_metadata({'/Title':'PCB component placement', '/Subject':
                             'KiCad front silkscreen and board outline; numbered landmarks, not functional boundaries.'})
        writer.write(output)
    doc=pypdfium2.PdfDocument(output)
    doc[0].render(scale=2).to_pil().save(output.with_suffix('.png'))
    print(output)

if __name__ == '__main__':
    main()
