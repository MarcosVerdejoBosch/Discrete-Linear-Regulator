"""Generate four read-only PCB subcircuit maps and a companion routing atlas.

Run after extract_pcb_nets.py and a KiCad F.Silkscreen/Edge.Cuts PDF export
with --exclude-refdes, so selected bold references are not duplicated:
python generate_pcb_subcircuits.py geometry.json --silkscreen silkscreen.pdf
"""
import argparse
import hashlib
import io
import json
import math
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
      footer=''),
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
    scale=min(640/(x1-x0),370/(y1-y0))
    px=20+(640-(x1-x0)*scale)/2;py=200+(370-(y1-y0)*scale)/2
    def pt(p): return px+(p[0]-x0)*scale, py+(y1-p[1])*scale
    net_colors={n:color for _,color,nets,_,_ in spec['groups'] for n in nets}
    component_colors={r:color for _,color,_,refs,_ in spec['groups'] for r in refs}
    def clip(c):
        path=c.beginPath();path.rect(px,py,(x1-x0)*scale,(y1-y0)*scale)
        c.clipPath(path,stroke=0,fill=0)
    front_only=spec['name']=='pcb_power_path'
    def copper(c,selected):
        for z in data['zones']:
            if front_only and z['layer']!='F.Cu':continue
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
            if front_only and t['layer']!='F.Cu' and t['kind']!='PCB_VIA':continue
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
    # Use actual front-silkscreen strokes, never an invented body envelope.
    obstacles=[]
    for t in data['tracks']:
        if t['net'] not in net_colors: continue
        points=arc_points(t) if t['kind']=='PCB_ARC' else [t['start'],t['end']]
        for a,b in zip(points,points[1:]):
            ax,ay=pt(a);bx,by=pt(b)
            count=max(1,int(math.hypot(bx-ax,by-ay)/3))
            obstacles.extend((ax+(bx-ax)*i/count,ay+(by-ay)*i/count) for i in range(count+1))
    for fp in data['footprint_graphics'].values():
        for shape in fp['shapes']:
            points=arc_points(shape) if shape['kind']==2 else [shape['start'],shape['end']]
            for a,b in zip(points,points[1:]):
                ax,ay=pt(a);bx,by=pt(b);count=max(1,int(math.hypot(bx-ax,by-ay)/3))
                obstacles.extend((ax+(bx-ax)*i/count,ay+(by-ay)*i/count) for i in range(count+1))
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
        cx=left+ww/2;cy=bottom+hh/2
        sx,sy=pt(data['silkscreen_refs'][ref]['at'])
        candidates=[]
        for radius in (14,22,32,44,58,74):
            for angle in range(0,360,30):
                x=cx+math.cos(math.radians(angle))*radius-label_w/2
                y=cy+math.sin(math.radians(angle))*radius-7
                box=(x,y,x+label_w,y+14)
                if x<21 or x+label_w>658 or y<201 or y+14>578:continue
                if any(overlaps(box,b) for b in occupied):continue
                hits=sum(x-3<ox<x+label_w+3 and y-3<oy<y+17 for ox,oy in obstacles)
                candidates.append((hits*120+math.hypot(x+label_w/2-sx,y+7-sy),x,y))
        assert candidates,ref
        _,lx,ly=min(candidates)
        # Keep the PCB's own silkscreen reference position whenever readable.
        native=(sx-label_w/2,sy-5)
        nx,ny=native
        if 21<nx and nx+label_w<658 and 201<ny<564 and not any(
                nx-4<ox<nx+label_w+4 and ny-4<oy<ny+18 for ox,oy in obstacles) and not any(
                overlaps((nx,ny,nx+label_w,ny+14),r) for r in occupied):
            lx,ly=native
        if spec['name']=='pcb_current_sense' and ref=='R35':lx,ly=150,270
        if front_only:
            if ref=='INPUT':lx+=18
            elif ref=='Rsns':lx=left+ww+8
        occupied.append((lx,ly,lx+label_w,ly+14))
        # A fine leader connects displaced text to its actual footprint center.
        ex=max(lx,min(cx,lx+label_w));ey=max(ly,min(cy,ly+14))
        leader=math.hypot(lx+label_w/2-sx,ly+5-sy)>8 and math.hypot(ex-cx,ey-cy)>18
        if front_only:leader=ref in ('INPUT','OUTPUT')
        if leader:
            c.setStrokeColor(HexColor(color));c.setStrokeAlpha(.95 if front_only else .55);c.setLineWidth(1.15 if front_only else .65)
            # Short orthogonal callout with a horizontal text-side landing.
            knee=ex-7 if ex>cx else ex+7
            dx=knee-cx;dy=ey-cy
            ratio=min(ww/2/max(abs(dx),.01),hh/2/max(abs(dy),.01),1)
            tx=cx+dx*ratio;ty=cy+dy*ratio
            path=c.beginPath();path.moveTo(tx,ty);path.lineTo(knee,ey);path.lineTo(ex,ey)
            c.drawPath(path);c.setStrokeAlpha(1)
        c.setFillColor(HexColor(color));c.drawString(lx+3,ly+2,label)
    c.setFillColor(HexColor('#233440'));c.setFont('Helvetica',21)
    c.drawString(20,613,spec['title'])
    c.setFont('Helvetica',12)
    c.drawString(20,591,'Actual KiCad copper + component highlights | '+
                 ('Top copper and front silkscreen' if front_only else 'Top-side projection of both outer layers'))
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
        c.drawString(20,177-15*i,line)
    # Orthogonal functional diagrams occupy their own band below the PCB view.
    def box(x,y,width,label,color):
        c.setStrokeColor(HexColor(color));c.setFillColor(HexColor('#F8FAFB'));c.setLineWidth(.9)
        c.roundRect(x,y,width,28,3,stroke=1,fill=1)
        c.setFillColor(HexColor(color));c.setFont('Helvetica-Bold',11)
        c.drawCentredString(x+width/2,y+10,label)
        return (x,y,width)
    def arrow(points,color='#657785'):
        c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(.9)
        path=c.beginPath();path.moveTo(*points[0])
        for point in points[1:]:path.lineTo(*point)
        c.drawPath(path)
        x,y=points[-1];a,b=points[-2];angle=math.atan2(y-b,x-a)
        path=c.beginPath();path.moveTo(x,y)
        for turn in (-.5,.5):path.lineTo(x-5*math.cos(angle+turn),y-5*math.sin(angle+turn))
        path.close();c.drawPath(path,stroke=0,fill=1)
    def row(labels,colors,y=78,x=20,width=960):
        gap=25;bw=(width-gap*(len(labels)-1))/len(labels)
        blocks=[box(x+i*(bw+gap),y,bw,label,colors[i]) for i,label in enumerate(labels)]
        for first,second in zip(blocks,blocks[1:]):arrow([(first[0]+bw,y+14),(second[0],y+14)])
        return blocks
    c.saveState();c.translate(0,30)
    name=spec['name']
    if name=='pcb_power_path':
        row(spec['flow'],['#657785',RED,RED,TEAL,PURPLE,PURPLE,BLUE,'#657785'])
        arrow([(929,78),(929,48),(70,48),(70,78)])
        c.setFillColor(HexColor('#657785'));c.setFont('Helvetica',11)
        c.drawCentredString(500,31,'GND return: load / OUTPUT pin 2 to INPUT pin 2 / supply')
    elif name=='pcb_current_sense':
        blocks=row(['Rsns','R33-R36 / U4A','R39','U4B','R42 / D5','EA node'],[ORANGE,ORANGE,BLUE,BLUE,GREEN,GREEN])
        box(236,32,210,'R40 / RV13 -> U4C',PURPLE)
        bx,by,bw=blocks[3]
        arrow([(446,46),(bx+bw/2,46),(bx+bw/2,78)],PURPLE)
        c.setFillColor(HexColor(PURPLE));c.setFont('Helvetica',10);c.drawString(461,32,'Limit reference')
    elif name=='pcb_enable_control':
        for label,y in [('UVLO valid',86),('OVLO valid',54),('Delay elapsed',22)]:
            box(20,y,115,label,ORANGE)
            arrow([(135,y+14),(153,y+14),(153,68),(178,68)],ORANGE)
        row(['Q25-Q27 / Q23','R20 / Q6','R17 / Q4A','R21 / pass base'],[TEAL,PURPLE,PURPLE,BLUE],54,178,802)
        c.setFillColor(HexColor('#657785'));c.setFont('Helvetica',10)
        for x,text in [(269,'AND permission'),(477,'Gate control'),(892,'Pass-base drive')]:
            c.drawCentredString(x,31,text)
    else:
        row(['VEE','Q4B: series switch','VCTRL / C12'],[ORANGE,RED,TEAL],78,100,800)
        box(385,30,230,'C11 / Q15 -> Q14',PURPLE)
        arrow([(783,78),(783,44),(615,44)],PURPLE)
        arrow([(385,44),(345,44),(345,68),(500,68),(500,78)],PURPLE)
        c.setFillColor(HexColor(PURPLE));c.setFont('Helvetica',10)
        c.drawString(628,29,'Ramp feedback');c.drawString(260,29,'Gate control')
    c.restoreState()
    c.setFillColor(HexColor('#657785'));c.setFont('Helvetica',10)
    c.drawString(20,18,'Ground fills omitted. Pad centers are schematic markers; colors group paths across series components. Not a fabrication drawing.')
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
