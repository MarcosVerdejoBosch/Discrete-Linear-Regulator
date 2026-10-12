"""Compose four KiCad monochrome copper/Edge.Cuts exports as a vector layer stack.

Usage: python docs/tools/generate_pcb_layers.py <export-directory>
Inputs: pcb-layer-F.Cu.pdf, pcb-layer-In1.Cu.pdf, pcb-layer-In2.Cu.pdf,
pcb-layer-B.Cu.pdf. Export each with pcb export pdf --mode-single
--black-and-white --layers <layer>,Edge.Cuts. No board is modified.
"""
import io
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, FloatObject, RectangleObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import pypdfium2

ROOT = Path(__file__).resolve().parents[2]
MM = 72 / 25.4
LAYERS = [
    ('F.Cu', '#B95742', 'TOP LAYER', 'Signal + power routing', 'Ground copper fills'),
    ('In1.Cu', '#368C83', 'INNER LAYER 1', 'GND reference plane', 'Clearances around non-GND pads'),
    ('In2.Cu', '#54899B', 'INNER LAYER 2', 'GND reference plane', 'Clearances around non-GND pads'),
    ('B.Cu', '#526BA7', 'BOTTOM LAYER', 'Signal + power routing', 'Ground copper fills'),
]

def main():
    inputs = Path(sys.argv[1])
    writer = PdfWriter()
    target = writer.add_blank_page(width=1000, height=1050)
    labels = io.BytesIO()
    c = canvas.Canvas(labels, pagesize=(1000, 1050))
    c.setFillColor(HexColor('#263640'))
    c.setFont('Helvetica', 26)
    c.drawString(48, 999, 'Four-layer copper architecture')
    c.setFont('Helvetica', 12)
    c.setFillColor(HexColor('#67747D'))
    c.drawString(48, 977, 'Final PCB layout  /  200 x 160 mm')
    # Common top-view orientation, affine projection; spacing is illustrative.
    a, b, cc, d = .74, -.15, .38, .30
    for i, (layer, color, subtitle, role, detail) in enumerate(LAYERS):
        source_writer = PdfWriter(clone_from=inputs / f'pcb-layer-{layer}.pdf')
        page = source_writer.pages[0]
        stream = ContentStream(page.get_contents(), page.pdf)
        rgb = HexColor(color).rgb()
        for operands, op in stream.operations:
            if op in (b'rg', b'RG') and all(float(v) < .01 for v in operands):
                operands[:] = [FloatObject(v) for v in rgb]
        page.replace_contents(stream)
        left = 246.89 * MM - .5
        bottom = float(page.mediabox.height) - 238.785 * MM - .5
        width, height = 200 * MM + 1, 160 * MM + 1
        page.cropbox = RectangleObject([left, bottom, left+width, bottom+height])
        page.trimbox = page.cropbox
        x, y = 48, 791 - i*211
        matrix = (a, b, cc, d, x-a*left-cc*bottom, y-b*left-d*bottom)
        target.merge_transformed_page(page, Transformation(matrix))
        anchor_x, anchor_y = x+a*width+cc*height*.5, y+b*width+d*height*.5
        c.setStrokeColor(HexColor(color)); c.setLineWidth(1)
        c.line(anchor_x+7, anchor_y, 688, anchor_y)
        c.setFillColor(HexColor(color)); c.circle(anchor_x+7, anchor_y, 2, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 24); c.drawString(711, anchor_y+28, layer)
        c.setFont('Helvetica', 10); c.drawString(711, anchor_y+11, subtitle)
        c.setFillColor(HexColor('#263640'))
        c.setFont('Helvetica', 15); c.drawString(711, anchor_y-18, role)
        c.setFillColor(HexColor('#67747D'))
        c.setFont('Helvetica', 11); c.drawString(711, anchor_y-37, detail)
    c.setFont('Helvetica', 11); c.setFillColor(HexColor('#67747D'))
    c.drawString(48, 38, 'Actual copper, pads and saved zone fills. All layers viewed from the top; colors identify layers.')
    c.drawString(48, 21, 'Exploded presentation: layer spacing and thickness are not to scale.')
    c.save(); labels.seek(0)
    target.merge_page(PdfReader(labels).pages[0])
    output = ROOT/'docs/figures/pcb_copper_layers.pdf'
    writer.add_metadata({'/Title':'Four-layer copper architecture'})
    writer.write(output)
    doc = pypdfium2.PdfDocument(output)
    doc[0].render(scale=1.5).to_pil().save(output.with_suffix('.png'))
    print(output)

if __name__ == '__main__':
    main()
