#!/usr/bin/env python

import sys
import os
from helpers import round_crty_point
#sys.path.append(os.path.join(sys.path[0],"..","..","kicad_mod")) # load kicad_mod path

# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
from KicadModTree import *


output_dir = os.getcwd()
_3dshapes = "Connectors_JST.3dshapes"+os.sep
ref_on_silk = False
fab_ref_inside = False
fab_line_width = 0.1
silk_line_width = 0.12
value_fontsize = [1,1]
value_fontwidth = 0.15
value_inside = False
silk_reference_fontsize=[1,1]
silk_reference_fontwidth=0.15
fab_reference_fontsize=[2,2]
fab_reference_fontwidth=0.3

CrtYd_offset = 0.5
CrtYd_linewidth = 0.05

pin1_marker_offset = 0.3
pin1_marker_linelen = 1.25
fab_pin1_marker_type = 1

pad_to_silk = 0.2
pad_size=[1.2, 1.7]

out_dir="Connectors_JST.pretty"+os.sep

if len(sys.argv) > 1:
    out_dir = sys.argv[1]
    if out_dir.endswith(".pretty"):
        out_dir += os.sep
    if not out_dir.endswith(".pretty"+os.sep):
        out_dir += ".pretty"+os.sep

    if os.path.isabs(out_dir) and os.path.isdir(out_dir):
        output_dir = out_dir
    else:
        output_dir = os.path.join(os.getcwd(),out_dir)

if len(sys.argv) > 2:
    if sys.argv[2] == "TERA":
        ref_on_silk = True
        fab_ref_inside = True
        fab_line_width = 0.05
        silk_line_width = 0.15
        _3dshapes = "tera_Connectors_JST.3dshapes"+os.sep
        value_fontsize = [0.6,0.6]
        value_fontwidth = 0.1
        fab_pin1_marker_type = 2
        value_inside = True
        fab_reference_fontsize=[0.6,0.6]
        fab_reference_fontwidth=0.1
    else:
        _3dshapes = sys.argv[2]
        if _3dshapes.endswith(".3dshapes"):
            _3dshapes += os.sep
        if not _3dshapes.endswith(".3dshapes"+os.sep):
            _3dshapes += ".3dshapes"+os.sep

if output_dir and not output_dir.endswith(os.sep):
    output_dir += os.sep

if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
    os.makedirs(output_dir)

# http://www.jst-mfg.com/product/pdf/eng/ePH.pdf
#JST_PH_S10B-PH-K_10x2.00mm_Straight
part = "S{n}B-PH-K" #JST part number format string

prefix = "JST_PH_"
suffix = "_{n:02}x{p:.2f}mm_Angled"

pitch = 2.00

# Connector Parameters
silk_to_part_offset = 0.1
x_min = -1.95
y_max = 6.25
y_min = y_max-6-1.6
y_main_min = y_max - 6

body_back_protrusion_width=0.7

silk_x_min = x_min - silk_to_part_offset
silk_y_min = y_min - silk_to_part_offset
silk_y_main_min = y_main_min - silk_to_part_offset
silk_y_max = y_max + silk_to_part_offset

for pincount in range (2,16+1):
    x_mid = (pincount-1)*pitch/2.0
    x_max = (pincount-1)*pitch + 1.95
    silk_x_max = x_max + silk_to_part_offset

    # Through-hole type shrouded header, Side entry type
    footprint_name = prefix + part.format(n=pincount) + suffix.format(n=pincount, p=pitch)

    kicad_mod = Footprint(footprint_name)
    description = "JST PH series connector, " + part.format(n=pincount) + ", side entry type, through hole"
    kicad_mod.setDescription(description)
    kicad_mod.setTags('connector jst ph')

    # set general values
    ref_pos_1=[1.5, silk_y_min-0.5-fab_reference_fontsize[0]/2.0]
    ref_pos_2=[x_mid, 2]

    kicad_mod.append(Text(type='reference', text='REF**', layer='F.Fab',
        at=(ref_pos_2 if fab_ref_inside else ref_pos_1),
        size=fab_reference_fontsize, thickness=fab_reference_fontwidth))

    if ref_on_silk:
        silk_ref_position = [1.5, silk_y_min-0.5-silk_reference_fontsize[0]/2.0]
        kicad_mod.append(Text(type='user', text='%R', at=silk_ref_position, layer='F.SilkS',
            size=silk_reference_fontsize, thickness=silk_reference_fontwidth))

    if value_inside:
        value_pos_y = y_max+-0.5-value_fontsize[0]/2.0
    else:
        value_pos_y = y_max+0.5+value_fontsize[0]/2.0

    kicad_mod.append(Text(type='value', text=footprint_name, at=[x_mid, value_pos_y], layer='F.Fab',
        size=value_fontsize, thickness=value_fontwidth))
    # create Silkscreen
    poly_big_cutout=[{'x':0.5, 'y':silk_y_max}
                              ,{'x':0.5, 'y':2}
                              ,{'x':x_max-2.45, 'y':2}
                              ,{'x':x_max-2.45, 'y':silk_y_max}]
    kicad_mod.append(PolygoneLine(polygone=poly_big_cutout, layer='F.SilkS', width=silk_line_width))

    tmp_x1=x_min+body_back_protrusion_width+silk_to_part_offset
    tmp_x2=x_max-body_back_protrusion_width-silk_to_part_offset
    poly_silk_outline= [
                    {'x':-pad_size[0]/2.0-pad_to_silk, 'y':silk_y_main_min},
                    {'x':tmp_x1, 'y':silk_y_main_min},
                    {'x':tmp_x1, 'y':silk_y_min},
                    {'x':silk_x_min, 'y':silk_y_min},
                    {'x':silk_x_min, 'y':silk_y_max},
                    {'x':silk_x_max, 'y':silk_y_max},
                    {'x':silk_x_max, 'y':silk_y_min},
                    {'x':tmp_x2, 'y':silk_y_min},
                    {'x':tmp_x2, 'y':silk_y_main_min},
                    {'x':(pincount-1)*pitch+pad_size[0]/2.0+pad_to_silk, 'y':silk_y_main_min}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_silk_outline, layer='F.SilkS', width=silk_line_width))

    kicad_mod.append(Line(start=[silk_x_min, silk_y_main_min], end=[tmp_x1, silk_y_main_min], layer='F.SilkS', width=silk_line_width))
    kicad_mod.append(Line(start=[silk_x_max, silk_y_main_min], end=[tmp_x2, silk_y_main_min], layer='F.SilkS', width=silk_line_width))

    kicad_mod.append(RectLine(start=[-1.3, 2.5], end=[-0.3, 4.1],
        layer='F.SilkS', width=silk_line_width))
    kicad_mod.append(RectLine(start=[(pincount-1)*pitch+1.3, 2.5], end=[(pincount-1)*pitch+0.3, 4.1],
        layer='F.SilkS', width=silk_line_width))

    kicad_mod.append(Line(start=[-0.3, 4.1], end=[-0.3, silk_y_max],
        layer='F.SilkS', width=silk_line_width))
    kicad_mod.append(Line(start=[-0.8, 4.1], end=[-0.8, silk_y_max],
        layer='F.SilkS', width=silk_line_width))

    # create Courtyard
    kicad_mod.append(RectLine(start=round_crty_point([x_min-CrtYd_offset, y_min-CrtYd_offset]),
        end=round_crty_point([x_max+CrtYd_offset, y_max+CrtYd_offset]),
        layer='F.CrtYd', width=CrtYd_linewidth))

    # Fab layer outline
    tmp_x1=x_min+body_back_protrusion_width
    tmp_x2=x_max-body_back_protrusion_width
    poly_fab_outline= [
                    {'x':tmp_x1, 'y':y_main_min},
                    {'x':tmp_x1, 'y':y_min},
                    {'x':x_min, 'y':y_min},
                    {'x':x_min, 'y':y_max},
                    {'x':x_max, 'y':y_max},
                    {'x':x_max, 'y':y_min},
                    {'x':tmp_x2, 'y':y_min},
                    {'x':tmp_x2, 'y':y_main_min},
                    {'x':tmp_x1, 'y':y_main_min}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_fab_outline, layer='F.Fab', width=fab_line_width))

    # create pads
    #add the pads
    kicad_mod.append(Pad(number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_RECT,
                        at=[0, 0], size=pad_size,
                        drill=0.7, layers=['*.Cu','*.Mask']))
    for p in range(1, pincount):
        Y = 0
        X = p * pitch

        num = p+1
        kicad_mod.append(Pad(number=num, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL,
                            at=[X, Y], size=pad_size,
                            drill=0.7, layers=['*.Cu','*.Mask']))


    # pin 1 marker
    poly_pin1_marker = [
        {'x':0, 'y':-1.2},
        {'x':-0.4, 'y':-1.6},
        {'x':0.4, 'y':-1.6},
        {'x':0, 'y':-1.2}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_pin1_marker, layer='F.SilkS', width=silk_line_width))
    if fab_pin1_marker_type == 1:
        kicad_mod.append(PolygoneLine(polygone=poly_pin1_marker, layer='F.Fab', width=fab_line_width))

    if fab_pin1_marker_type == 2:
        poly_pin1_marker_type2 = [
            {'x':-1, 'y':y_main_min},
            {'x':0, 'y':y_main_min+1},
            {'x':1, 'y':y_main_min}
        ]
        kicad_mod.append(PolygoneLine(polygone=poly_pin1_marker_type2, layer='F.Fab', width=fab_line_width))
    #Add a model
    kicad_mod.append(Model(filename=_3dshapes + footprint_name + ".wrl"))


    #filename
    filename = output_dir + footprint_name + ".kicad_mod"


    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)
