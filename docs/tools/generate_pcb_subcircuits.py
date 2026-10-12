"""Generate four read-only PCB subcircuit maps and a companion routing atlas.

Run after extract_pcb_nets.py and a KiCad F.Silkscreen/Edge.Cuts PDF export
with --exclude-refdes, so selected bold references are not duplicated:
python generate_pcb_subcircuits.py geometry.json --silkscreen silkscreen.pdf
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import textwrap

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, FloatObject, RectangleObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import pypdfium2
from generate_pcb_routing import arc_points, ROOT, MM

RED='#C03936';ORANGE='#C97B17';TEAL='#008D87';BLUE='#236DB0';PURPLE='#8A4BA3';GREEN='#008A58'
VIEWS = [
 dict(name='pcb_power_path',title='Input-to-output power path',roi=(369,135,448,183),
      groups=[
       ('Input and polarity protection',RED,['VCC'],['INPUT','Q_POL'],'VCC enters Q_POL at pin 2.'),
       ('Protected supply',ORANGE,['VEE'],[],'VEE joins Q_POL pin 3 to Q4B pin 3.'),
       ('Startup output',TEAL,['VCTRL'],['Q4'],'Q4B pins 3-5 feed the pass emitter. Q4 is a dual-device package.'),
       ('Pass collector',PURPLE,['Net-(D18-A)'],['Q_PASS','Rsns'],'Q_PASS pin 2 reaches Rsns pin 1.'),
       ('Load output',BLUE,['OUT'],['OUTPUT'],'Rsns pin 2 reaches OUTPUT pin 1. The load is external.')],
      flow=['Supply','INPUT','Q_POL','Q4B','Q_PASS','Rsns','OUTPUT','Load'],
      flow_note='Functional series path; supply and load are external. Arrows indicate connectivity, not current density.',
      footer='Crop of the power-device region; auxiliary supply branches extend beyond this view.'),
 dict(name='pcb_current_sense',title='Current sensing and limiting',roi=(329,103,384,178),
      groups=[
       ('Differential sensing',ORANGE,['Net-(D18-A)','OUT','Net-(U4A-+)','Net-(U4A--)'],['Rsns','R33','R34','R35','R36'],
        'R33 / R34 pick up opposite sides of Rsns. R35 / R36 complete the amplifier network.'),
       ('Amplified signal',BLUE,['Net-(C5-Pad2)','Net-(U4B--)','Net-(C7-Pad2)'],['U4','R39','R38','C7'],
        'U4A output at pin 1 reaches U4B through R39. U4 contains several amplifier sections.'),
       ('Adjustable limit',PURPLE,['VREF','Net-(U4C-+)','Net-(U4B-+)'],['R40','RV13'],
        'R40 / RV13 set the threshold; U4C buffers it for U4B.'),
       ('Limiting action',GREEN,['Net-(C7-Pad1)','Net-(D5-K)','Net-(D5-A)'],['R42','D5','U1'],
        'U4B output reaches the error-amplifier node through R42 and D5.')],
      flow=['Rsns','R33-R36','U4A','R39 / U4B','R42 / D5','EA node'],
      flow_note='Signal flow, not load-current flow. RV13 -> U4C -> U4B provides the adjustable comparison threshold.',
      footer='A shared color may span series components. Their pads and copper breaks remain distinct.'),
 dict(name='pcb_enable_control',title='Enable logic and pass-drive switch',roi=(295,121,426,213),
      groups=[
       ('Permission inputs',ORANGE,['1','2','LDO2','Net-(Q25-B)','Net-(Q26-B)','Net-(Q27-B)'],['R90','R91','R93'],
        'PCB nets 1 (UVLO), 2 (OVLO), and LDO2 (delay) drive the series NPN chain.'),
       ('Discrete AND function',TEAL,['Net-(Q25-C)','Net-(Q26-C)','Net-(Q27-C)','Net-(Q23-B)','TTL'],['Q25','Q26','Q27','Q23'],
        'Q25-Q27 and the inverter Q23 generate the TTL enable node.'),
       ('Gate control',PURPLE,['Net-(D1-K)','Net-(Q6-D)','Net-(Q4-Pad2)'],['R20','Q6','R17'],
        'TTL drives Q6 through R20. Q6 controls Q4A through R17.'),
       ('Pass-base drive',BLUE,['Net-(Q3-E)','Net-(Q4-Pad1)','Net-(Q_PASS1-B)'],['Q3','Q4','R21','Q_PASS'],
        'Q4A connects the Q3 output-stage path through R21 to the pass base.')],
      flow=['UVLO / OVLO / delay','Q25-Q27','Q23: TTL','R20 / Q6','R17 / Q4A','R21 / pass base'],
      flow_note='Control sequence only. The load-current path passes through Q4B and Q_PASS, not through this logic chain.',
      footer='Q4A and Q4B share the Q4 footprint. This view highlights the enable section Q4A.'),
 dict(name='pcb_startup_control',title='Startup ramp and series switch',roi=(390,110,433,155),
      groups=[
       ('Protected supply',ORANGE,['VEE'],['R55','D10'],'VEE supplies the startup stage and Q4B pin 3.'),
       ('Ramp feedback',PURPLE,['Net-(Q15-B)','Net-(Q15-E)','Net-(Q14-B)'],['C11','R58','Q15','R57','Q14'],
        'C11 couples changes of VCTRL into the Q15 / Q14 control network.'),
       ('Switch gate',RED,['Net-(D10-A)'],['R56','Q4'],
        'The Q14-controlled node drives Q4B gate pin 4; D10 connects it to VEE.'),
       ('Ramped supply',TEAL,['VCTRL'],['C12','Q_PASS'],
        'Q4B pin 5 feeds VCTRL, C12 and the pass emitter. C12 is 10 uF in the PCB.')],
      flow=['VEE','Q4B pins 3-5','VCTRL / C12','C11 / Q15','Q14','Q4B gate'],
      flow_note='The first three blocks show the supply path; the remaining blocks show the feedback path to the switch gate.',
      footer='Q4B is the startup section of the shared Q4 package. The enable section Q4A is a separate path.'),
]

def make_view(data, silkscreen, spec):
    w,h=1000,650
    roi=spec['roi'];x0,y0,x1,y1=roi
    scale=min(640/(x1-x0),420/(y1-y0))
    px=20+(640-(x1-x0)*scale)/2;py=150+(420-(y1-y0)*scale)/2
    def pt(p): return px+(p[0]-x0)*scale, py+(y1-p[1])*scale
    net_colors={n:color for _,color,nets,_,_ in spec['groups'] for n in nets}
    component_colors={r:color for _,color,_,refs,_ in spec['groups'] for r in refs}
    def clip(c):
        path=c.beginPath();path.rect(px,py,(x1-x0)*scale,(y1-y0)*scale)
        c.clipPath(path,stroke=0,fill=0)
    def copper(c,selected):
        for z in data['zones']:
            if z['net']=='GND' or (z['net'] in net_colors)!=selected:continue
            c.setFillColor(HexColor(net_colors[z['net']] if selected else '#E9ECEF'))
            c.setFillAlpha(.35 if selected else 1)
            for poly in z['polygons']:
                path=c.beginPath()
                for ring in poly:
                    if not ring:continue
                    path.moveTo(*pt(ring[0]))
                    for p in ring[1:]:path.lineTo(*pt(p))
                    path.close()
                c.drawPath(path,stroke=0,fill=1,fillMode=0)
        c.setFillAlpha(1);c.setLineCap(1);c.setLineJoin(1)
        c.setStrokeAlpha(.60 if selected else 1)
        for t in data['tracks']:
            if (t['net'] in net_colors)!=selected:continue
            color=HexColor(net_colors[t['net']] if selected else '#E3E6E9')
            c.setStrokeColor(color);c.setFillColor(color)
            c.setLineWidth(max(t['width']*scale,.3))
            if t['kind']=='PCB_VIA':c.circle(*pt(t['start']),t['width']*scale/2,stroke=0,fill=1)
            else:
                pts=arc_points(t) if t['kind']=='PCB_ARC' else [t['start'],t['end']]
                path=c.beginPath();path.moveTo(*pt(pts[0]))
                for p in pts[1:]:path.lineTo(*pt(p))
                c.drawPath(path)
        c.setStrokeAlpha(1)
        if selected:
            for p in data['pads']:
                if p['net'] not in net_colors:continue
                c.setFillColor(HexColor(net_colors[p['net']]))
                c.circle(*pt(p['at']),.7*scale,stroke=0,fill=1)
                c.setFillColor(HexColor('#FFFFFF'));c.circle(*pt(p['at']),.25*scale,stroke=0,fill=1)

    bg=io.BytesIO();c=canvas.Canvas(bg,pagesize=(w,h))
    c.saveState();clip(c);copper(c,False);c.restoreState();c.save();bg.seek(0)
    writer=PdfWriter();page=writer.add_page(PdfReader(bg).pages[0])
    source_writer=PdfWriter(clone_from=silkscreen);base=source_writer.pages[0]
    stream=ContentStream(base.get_contents(),base.pdf)
    stream.operations=[([FloatObject(.72)],b'G') if op in [b'RG',b'G',b'K'] else
                       ([FloatObject(.72)],b'g') if op in [b'rg',b'g',b'k'] else (v,op)
                       for v,op in stream.operations]
    base.replace_contents(stream);sheet_h=float(base.mediabox.height)
    base.cropbox=RectangleObject([x0*MM,sheet_h-y1*MM,x1*MM,sheet_h-y0*MM]);base.trimbox=base.cropbox
    page.merge_transformed_page(base,Transformation().scale(scale/MM).translate(px-x0*scale,py-(sheet_h-y1*MM)*scale/MM))
    top=io.BytesIO();c=canvas.Canvas(top,pagesize=(w,h))
    c.saveState();clip(c);copper(c,True);c.restoreState()
    # Highlight actual footprint fabrication outlines, with silkscreen fallback.
    occupied=[]
    def overlaps(a,b):
        return a[0]<b[2]+2 and a[2]+2>b[0] and a[1]<b[3]+2 and a[3]+2>b[1]
    for ref,color in component_colors.items():
        pads=[p for p in data['pads'] if p['ref']==ref]
        assert pads,ref
        xs=[p['at'][0] for p in pads];ys=[p['at'][1] for p in pads]
        left,bottom=pt((min(xs)-1.2,max(ys)+1.2))
        ww=(max(xs)-min(xs)+2.4)*scale;hh=(max(ys)-min(ys)+2.4)*scale
        shapes=data['footprint_graphics'][ref]['shapes']
        assert shapes,ref
        c.saveState();clip(c)
        for thickness,alpha in [(6,.12),(1.8,1)]:
            c.setStrokeColor(HexColor(color));c.setStrokeAlpha(alpha);c.setLineWidth(thickness)
            for shape in shapes:
                kind=shape['kind']
                if kind==3:
                    c.circle(*pt(shape['center']),shape['radius']*scale,stroke=1,fill=0)
                    continue
                if kind==0:rings=[[shape['start'],shape['end']]]
                elif kind==2:rings=[arc_points(shape)]
                elif kind==1:
                    ax,ay=shape['start'];bx,by=shape['end']
                    rings=[[[ax,ay],[bx,ay],[bx,by],[ax,by],[ax,ay]]]
                elif kind==4:rings=[ring+[ring[0]] for ring in shape['rings'] if ring]
                else:continue
                for ring in rings:
                    path=c.beginPath();path.moveTo(*pt(ring[0]))
                    for p in ring[1:]:path.lineTo(*pt(p))
                    c.drawPath(path)
        c.restoreState()
        label=ref
        c.setFont('Helvetica-Bold',12)
        label_w=c.stringWidth(label,'Helvetica-Bold',12)+6
        candidates=[(left,bottom+hh),(left+ww-label_w,bottom+hh),
                    (left,bottom-15),(left+ww+3,bottom+hh/2),
                    (left-label_w-3,bottom+hh/2),(left,bottom+hh+16)]
        lx,ly=next(((x,y) for x,y in candidates if not any(
            overlaps((x,y,x+label_w,y+14),b) for b in occupied)),candidates[-1])
        occupied.append((lx,ly,lx+label_w,ly+14))
        c.setFillColor(HexColor('#172D3A'));c.drawString(lx+3,ly+2,label)
    c.setFillColor(HexColor('#233440'));c.setFont('Helvetica',21)
    c.drawString(20,613,spec['title'])
    c.setFont('Helvetica',12)
    c.drawString(20,591,'Actual KiCad copper + component highlights | Top-side projection of both outer layers')
    y=563
    for title,color,nets,refs,description in spec['groups']:
        c.setStrokeColor(HexColor(color));c.setLineWidth(4);c.line(686,y+2,706,y+2)
        c.setFillColor(HexColor('#233440'));c.setFont('Helvetica-Bold',14);c.drawString(715,y-3,title)
        c.setFont('Helvetica',13)
        for line in textwrap.wrap(description,39):
            y-=18;c.drawString(686,y-3,line)
        y-=28
    c.setFont('Helvetica',11);c.setFillColor(HexColor('#56636D'))
    for i,line in enumerate(textwrap.wrap(spec['footer'],95)):
        c.drawString(20,127-15*i,line)
    # Functional flow strip is deliberately separated from copper geometry.
    steps=spec['flow'];gap=14;box_w=(960-gap*(len(steps)-1))/len(steps)
    for i,label in enumerate(steps):
        x=20+i*(box_w+gap)
        c.setStrokeColor(HexColor('#A8B3BB'));c.setFillColor(HexColor('#F7F9FA'));c.setLineWidth(.8)
        c.roundRect(x,65,box_w,39,4,stroke=1,fill=1)
        c.setFillColor(HexColor('#233440'));c.setFont('Helvetica',12)
        lines=textwrap.wrap(label,max(12,int(box_w/6)))
        for k,line in enumerate(lines):c.drawCentredString(x+box_w/2,83+(len(lines)-1)*6-k*13,line)
        if i<len(steps)-1:
            c.setStrokeColor(HexColor('#657785'));c.line(x+box_w+2,84,x+box_w+gap-2,84)
            c.line(x+box_w+gap-5,87,x+box_w+gap-2,84);c.line(x+box_w+gap-5,81,x+box_w+gap-2,84)
    note_y=47
    if spec['name']=='pcb_power_path':
        first=20+box_w/2;last=20+(len(steps)-1)*(box_w+gap)+box_w/2
        c.setStrokeColor(HexColor('#657785'));c.setLineWidth(.8)
        c.line(last,65,last,55);c.line(last,55,first,55);c.line(first,55,first,65)
        c.line(first-3,61,first,65);c.line(first+3,61,first,65)
        c.setFillColor(HexColor('#FFFFFF'));c.rect(360,48,280,14,stroke=0,fill=1)
        c.setFillColor(HexColor('#657785'));c.setFont('Helvetica',10)
        c.drawCentredString(500,51,'GND return: OUTPUT pin 2 -> INPUT pin 2')
        note_y=31
    c.setFont('Helvetica',11)
    for i,line in enumerate(textwrap.wrap(spec['flow_note'],145)):c.drawString(20,note_y-i*14,line)
    c.setFillColor(HexColor('#657785'));c.setFont('Helvetica',10)
    c.drawString(20,12,'Ground fills omitted. Pad centers are schematic markers; colors group paths across series components. Not a fabrication drawing.')
    c.save();top.seek(0);page.merge_page(PdfReader(top).pages[0])
    page.compress_content_streams();writer.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
    output=ROOT/'docs/figures'/f"{spec['name']}.pdf"
    writer.add_metadata({'/Title':spec['title'],'/Subject':'Source-backed PCB routing and component map'})
    writer.write(output)
    doc=pypdfium2.PdfDocument(output);doc[0].render(scale=1.3).to_pil().save(output.with_suffix('.png'))
    return output

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('geometry');parser.add_argument('--silkscreen',required=True)
    args=parser.parse_args();data=json.loads(Path(args.geometry).read_text())
    assert hashlib.sha256((ROOT/data['source']).read_bytes()).hexdigest()==data['sha256']
    outputs=[make_view(data,args.silkscreen,s) for s in VIEWS]
    atlas=PdfWriter()
    for f in outputs:atlas.add_page(PdfReader(f).pages[0])
    atlas.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
    atlas.write(ROOT/'docs/figures/pcb_subcircuit_atlas.pdf')
    evidence={'source':data['source'],'sha256':data['sha256'],'kicad':data['kicad'],'views':[]}
    for s in VIEWS:
        nets={n for _,_,ns,_,_ in s['groups'] for n in ns}
        refs={r for _,_,_,rs,_ in s['groups'] for r in rs}
        evidence['views'].append(dict(name=s['name'],roi=s['roi'],nets=sorted(nets),components=sorted(refs),
             pads=[p for p in data['pads'] if p['ref'] in refs]))
    (ROOT/'hardware/PCB_SUBCIRCUIT_EVIDENCE.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print('Generated four maps and pcb_subcircuit_atlas.pdf; PCB unchanged.')

if __name__=='__main__':main()
