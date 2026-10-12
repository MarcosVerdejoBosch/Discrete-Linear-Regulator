"""Compose native KiCad top/bottom renders; preserve the viewing geometry.

Run after rendering docs/figures/pcb_3d.png and pcb_3d_bottom.png.
Only transparent outer margins are cropped. The bottom panel is smaller.
"""
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import pypdfium2

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / 'docs/figures'

def main():
    output = FIG / 'pcb_3d_views.pdf'
    panels = []
    for name, width, label in [
        ('pcb_3d.png', 800, '(a) Top side'),
        ('pcb_3d_bottom.png', 570, '(b) Bottom side'),
    ]:
        im = Image.open(FIG / name).convert('RGBA')
        im = im.crop(im.getchannel('A').getbbox())
        height = width * im.height / im.width
        panels.append((im, width, height, label))
    page_height = sum(p[2] for p in panels) + 120
    c = canvas.Canvas(str(output), pagesize=(900, page_height))
    c.setTitle('PCB top and bottom views')
    top = page_height - 20
    for im, width, height, label in panels:
        c.drawImage(ImageReader(im), (900-width)/2, top-height,
                    width=width, height=height, mask='auto')
        c.setFillColorRGB(.15, .20, .24)
        c.setFont('Helvetica', 17)
        c.drawCentredString(450, top-height-24, label)
        top -= height + 60
    c.save()
    doc = pypdfium2.PdfDocument(output)
    doc[0].render(scale=1.4).to_pil().save(output.with_suffix('.png'))
    print(output)

if __name__ == '__main__':
    main()
