"""Draw source-backed net maps from extract_pcb_nets.py JSON.

Usage: python generate_pcb_routing.py geometry.json --silkscreen export.pdf
The silkscreen input is KiCad's unscaled full-sheet F.Silkscreen/Edge.Cuts
PDF export. All geometry is read-only; saved zone fills are not recalculated.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, FloatObject, RectangleObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import pypdfium2

ROOT = Path(__file__).resolve().parents[2]
MM = 72/25.4
COLORS = {'VCC':'#C03936','VEE':'#C97B17','VCTRL':'#00928C',
          'OUT':'#236DB0','Net-(D18-A)':'#236DB0',
          'FB':'#008A58','VREF':'#8A4BA3','Net-(U1E-B)':'#8A4BA3'}
POWER = ['VCC','VEE','VCTRL','OUT','Net-(D18-A)']
FEEDBACK = ['OUT','FB','VREF','Net-(U1E-B)']

def arc_points(t):
    a,b,c=t['start'],t['mid'],t['end']
    ax,ay=a;bx,by=b;cx,cy=c
    det=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
    if abs(det)<1e-10: return [a,b,c]
    aa=ax*ax+ay*ay;bb=bx*bx+by*by;cc=cx*cx+cy*cy
    ux=(aa*(by-cy)+bb*(cy-ay)+cc*(ay-by))/det
    uy=(aa*(cx-bx)+bb*(ax-cx)+cc*(bx-ax))/det
    start,mid,end=[math.atan2(y-uy,x-ux) for x,y in [a,b,c]]
    sweep=(end-start)%(2*math.pi)
    if (mid-start)%(2*math.pi)>sweep: sweep-=2*math.pi
    radius=math.hypot(ax-ux,ay-uy)
    count=max(4,int(abs(sweep)*radius/.05)+1)
    return [[ux+radius*math.cos(start+sweep*i/count),
             uy+radius*math.sin(start+sweep*i/count)] for i in range(count+1)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('geometry');p.add_argument('--silkscreen',required=True)
    args=p.parse_args()
    data=json.loads(Path(args.geometry).read_text())
    source=ROOT/data['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==data['sha256']
    w,h=960,565
    # The right panel is a magnified crop; both panels use a top-side projection.
    panels=[dict(roi=(245,77,449,241), x=18,y=78,width=545,nets=POWER),
            dict(roi=(329,100,382,149),x=603,y=198,width=327,nets=FEEDBACK)]
    under=io.BytesIO();c=canvas.Canvas(under,pagesize=(w,h))
    def mapping(panel):
        x0,y0,x1,y1=panel['roi'];s=panel['width']/(x1-x0)
        return lambda p:(panel['x']+(p[0]-x0)*s,panel['y']+(y1-p[1])*s),s
    def clip(panel):
        x0,y0,x1,y1=panel['roi'];_,s=mapping(panel)
        path=c.beginPath();path.rect(panel['x'],panel['y'],panel['width'],(y1-y0)*s)
        c.clipPath(path,stroke=0,fill=0)
    def copper(panel, selected):
        point,s=mapping(panel)
        for zone in data['zones']:
            if zone['net']=='GND':continue
            if (zone['net'] in panel['nets']) != selected:continue
            c.setFillColor(HexColor(COLORS[zone['net']]) if selected else HexColor('#E9ECEF'))
            c.setFillAlpha(.38 if selected else 1)
            for polygon in zone['polygons']:
                path=c.beginPath()
                for ring in polygon:
                    if not ring:continue
                    path.moveTo(*point(ring[0]))
                    for pos in ring[1:]:path.lineTo(*point(pos))
                    path.close()
                c.drawPath(path,stroke=0,fill=1,fillMode=0)
        c.setFillAlpha(1)
        c.setLineCap(1);c.setLineJoin(1)
        for t in data['tracks']:
            if (t['net'] in panel['nets']) != selected:continue
            if t['layer'] not in ['F.Cu','B.Cu']:continue
            c.setStrokeColor(HexColor(COLORS[t['net']]) if selected else HexColor('#E3E6E9'))
            c.setFillColor(HexColor(COLORS[t['net']]) if selected else HexColor('#E3E6E9'))
            c.setLineWidth(max(t['width']*s,.35))
            if t['kind']=='PCB_VIA':
                x,y=point(t['start']);c.circle(x,y,t['width']*s/2,stroke=0,fill=1)
            else:
                pts=arc_points(t) if t['kind']=='PCB_ARC' else [t['start'],t['end']]
                path=c.beginPath();path.moveTo(*point(pts[0]))
                for pos in pts[1:]:path.lineTo(*point(pos))
                c.drawPath(path)
        if selected:
            for pad in data['pads']:
                if pad['net'] not in panel['nets']:continue
                c.setFillColor(HexColor(COLORS[pad['net']]))
                x,y=point(pad['at']);c.circle(x,y,1.0*s,stroke=0,fill=1)
                c.setFillColor(HexColor('#FFFFFF'));c.circle(x,y,.32*s,stroke=0,fill=1)
    for panel in panels:
        c.saveState();clip(panel);copper(panel,False);c.restoreState()
    c.save();under.seek(0)
    writer=PdfWriter();page=writer.add_page(PdfReader(under).pages[0])
    # Desaturate the KiCad silkscreen, preserving all text and outline geometry.
    for panel in panels:
        base_writer=PdfWriter(clone_from=args.silkscreen)
        base=base_writer.pages[0]
        stream=ContentStream(base.get_contents(),base.pdf)
        operations=[]
        for operands,operator in stream.operations:
            if operator in [b'RG',b'G',b'K']:
                operands=[FloatObject(.67)];operator=b'G'
            elif operator in [b'rg',b'g',b'k']:
                operands=[FloatObject(.67)];operator=b'g'
            operations.append((operands,operator))
        stream.operations=operations;base.replace_contents(stream)
        x0,y0,x1,y1=panel['roi'];sheet_h=float(base.mediabox.height)
        base.cropbox=RectangleObject([x0*MM,sheet_h-y1*MM,x1*MM,sheet_h-y0*MM])
        base.trimbox=base.cropbox
        _,s=mapping(panel);scale=s/MM
        page.merge_transformed_page(base,Transformation().scale(scale).translate(
            panel['x']-x0*s,panel['y']-(sheet_h-y1*MM)*scale))
    overlay=io.BytesIO();c=canvas.Canvas(overlay,pagesize=(w,h))
    for panel in panels:
        c.saveState();clip(panel);copper(panel,True);c.restoreState()
    c.setFillColor(HexColor('#263440'));c.setFont('Helvetica',18)
    c.drawString(18,539,'(a) Supply distribution and output routing')
    c.drawString(603,539,'(b) Feedback and reference detail')
    c.setFont('Helvetica',13)
    c.drawString(18,521,'Full board - top-side projection')
    c.drawString(603,521,'Magnified upper-board region')
    def legend(x,y,net,text):
        c.setStrokeColor(HexColor(COLORS[net]));c.setLineWidth(3);c.line(x,y,x+20,y)
        c.setFillColor(HexColor('#263440'));c.setFont('Helvetica',14)
        c.drawString(x+28,y-3,text)
    legend(24,61,'VCC','VCC - input terminal')
    legend(278,61,'VEE','VEE - after polarity protection')
    legend(24,41,'VCTRL','VCTRL - startup-circuit output')
    legend(278,41,'OUT','Output path - pass device / Rsns / OUT')
    legend(606,177,'OUT','OUT - output pickup at R24 / C4')
    legend(606,156,'FB','FB - divider to U1 pin 11')
    legend(606,135,'VREF','VREF - reference and path through R44')
    c.setFont('Helvetica',12)
    for i,line in enumerate(['Front and back copper projected together.',
                             'Ground fills omitted; other nets shown in gray.',
                             'Colored circles mark connected pad centers.',
                             'R44 separates VREF from U1 pin 14.',
                             'Rsns separates the pass collector from OUT.']):
        c.drawString(606,106-16*i,line)
    # The selected region is a locator, not a functional-block boundary.
    point,_=mapping(panels[0]);x,y=point((329,149))
    c.setDash(4,3);c.setStrokeColor(HexColor('#647481'));c.setLineWidth(.8)
    c.rect(x,y,(382-329)*panels[0]['width']/204,(149-100)*panels[0]['width']/204)
    c.setDash();c.setFont('Helvetica',10);c.drawString(x,y-12,'Detail (b)')
    c.save();overlay.seek(0);page.merge_page(PdfReader(overlay).pages[0])
    output=ROOT/'docs/figures/pcb_routing.pdf'
    writer.add_metadata({'/Title':'PCB power and feedback net maps',
                         '/Subject':'Read-only KiCad tracks, vias and saved copper fills; top-side projection.'})
    page.compress_content_streams()
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    writer.write(output)
    pdf=pypdfium2.PdfDocument(output);pdf[0].render(scale=1.5).to_pil().save(output.with_suffix('.png'))
    selected=set(POWER+FEEDBACK)
    evidence=dict(source=data['source'],sha256=data['sha256'],kicad=data['kicad'],
                  nets={n:dict(tracks_vias=sum(t['net']==n for t in data['tracks']),
                              zones=sum(z['net']==n for z in data['zones']),
                              pads=[p for p in data['pads'] if p['net']==n]) for n in sorted(selected)})
    (ROOT/'hardware/PCB_NET_MAP_EVIDENCE.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(output)

if __name__=='__main__':main()
