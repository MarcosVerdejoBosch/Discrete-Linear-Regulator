"""Read PCB geometry with KiCad's bundled Python/pcbnew; never save the source board.

Usage: <KiCad Python> extract_pcb_nets.py <output.json> [temporary-silkscreen-copy.kicad_pcb]
"""
import hashlib
import json
from pathlib import Path
import sys
import pcbnew

root = Path(__file__).resolve().parents[2]
source = root / 'hardware/kicad/Regulador.kicad_pcb'
board = pcbnew.LoadBoard(str(source))
def xy(point):
    return [pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)]

tracks = []
for item in board.GetTracks():
    row = dict(net=item.GetNetname(), layer=board.GetLayerName(item.GetLayer()),
               kind=item.GetClass(), start=xy(item.GetStart()),
               end=xy(item.GetEnd()), width=pcbnew.ToMM(
                   item.GetWidth(pcbnew.F_Cu) if isinstance(item, pcbnew.PCB_VIA)
                   else item.GetWidth()))
    if isinstance(item, pcbnew.PCB_ARC):
        row['mid'] = xy(item.GetMid())
    tracks.append(row)
pads = []
footprint_graphics = {}
silkscreen_refs = {}
for footprint in board.GetFootprints():
    for pad in footprint.Pads():
        pads.append(dict(ref=footprint.GetReference(), value=footprint.GetValue(),
                         pin=pad.GetNumber(), net=pad.GetNetname(), at=xy(pad.GetPosition())))
    ref=footprint.GetReference()
    texts=[g for g in footprint.GraphicalItems() if isinstance(g,pcbnew.PCB_TEXT)
           and g.GetLayer()==pcbnew.F_SilkS and g.GetShownText(False)==ref]
    field=footprint.Reference()
    anchor=texts[0] if texts else field
    silkscreen_refs[ref]=dict(at=xy(anchor.GetPosition()),angle=anchor.GetTextAngle().AsDegrees(),
                             visible=bool(texts) or field.IsVisible())
    # Only the optional temporary export copy loses duplicate reference text.
    if len(sys.argv)>2:
        for text in texts:text.SetText("")
        field.SetVisible(False)
    shapes=[g for g in footprint.GraphicalItems() if isinstance(g,pcbnew.PCB_SHAPE)]
    layer=pcbnew.F_SilkS
    graphics=[]
    for shape in shapes:
        if shape.GetLayer()!=layer:continue
        kind=int(shape.GetShape())
        row=dict(kind=kind,start=xy(shape.GetStart()),end=xy(shape.GetEnd()))
        if kind==pcbnew.SHAPE_T_ARC:row['mid']=xy(shape.GetArcMid())
        if kind==pcbnew.SHAPE_T_CIRCLE:
            row['center']=xy(shape.GetCenter());row['radius']=pcbnew.ToMM(shape.GetRadius())
        if kind==pcbnew.SHAPE_T_POLY:
            poly=shape.GetPolyShape()
            row['rings']=[[xy(poly.COutline(i).CPoint(k)) for k in range(poly.COutline(i).PointCount())]
                          for i in range(poly.OutlineCount())]
        graphics.append(row)
    footprint_graphics[footprint.GetReference()]=dict(layer=board.GetLayerName(layer),shapes=graphics)
zones = []
def chain_points(chain):
    return [xy(chain.CPoint(i)) for i in range(chain.PointCount())]
for zone in board.Zones():
    layer = zone.GetLayer()
    if layer not in [pcbnew.F_Cu, pcbnew.B_Cu]:
        continue
    filled = zone.GetFilledPolysList(layer)
    polygons = []
    for i in range(filled.OutlineCount()):
        polygons.append([chain_points(filled.COutline(i))] +
                        [chain_points(filled.CHole(i,h)) for h in range(filled.HoleCount(i))])
    zones.append(dict(net=zone.GetNetname(), layer=board.GetLayerName(layer), polygons=polygons))
result = dict(source='hardware/kicad/Regulador.kicad_pcb',
              sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              kicad=pcbnew.GetBuildVersion(), tracks=tracks, pads=pads,
              zones=zones,footprint_graphics=footprint_graphics,silkscreen_refs=silkscreen_refs)
Path(sys.argv[1]).write_text(json.dumps(result, indent=2), encoding='utf-8')
print('Read',len(tracks),'tracks/vias and',len(pads),'pads; board unchanged.')

if len(sys.argv)>2:
    assert Path(sys.argv[2]).resolve()!=source.resolve()
    pcbnew.SaveBoard(sys.argv[2],board)
