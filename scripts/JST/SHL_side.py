#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(sys.path[0],"..","..","kicad_mod"))

#import argparse
from kicad_mod import KicadMod, createNumberedPadsSMD

#parser = argparse.ArgumentParser()
#parser.add_argument('pincount', help='number of pins of the jst connector', type=int, nargs=1)
#parser.add_argument('-v', '--verbose', help='show extra information while generating the footprint', action='store_true') #TODO
#args = parser.parse_args()

# http://www.jst-mfg.com/product/pdf/eng/eSHL.pdf

#pincount = int(args.pincount[0])

for pincount in [2,5,6,7,8,10,11,12,14,16,20,22,26,30]:

    pad_spacing = 1
    start_pos_x = -(pincount-1)*pad_spacing/2
    end_pos_x = (pincount-1)*pad_spacing/2

    pad_w = 0.6
    pad_h = 1.4

    B = 2.8 + pincount
    A = (pincount - 1) * 1.0

    jst_name = "SM{pincount:02}B-SHLS-TF".format(pincount=pincount)

    # SMT type shrouded header, Side entry type (normal type)
    footprint_name = "JST_SHL_" + jst_name + "_{pincount:02}x1.00mm_Angled".format(pincount=pincount)

    print(footprint_name)
    kicad_mod = KicadMod(footprint_name)
    kicad_mod.setDescription("JST SHL series connector, " + jst_name) 
    kicad_mod.setAttribute('smd')
    kicad_mod.setTags('connector jst SHL SMT side horizontal entry 1.0mm pitch')

    kicad_mod.setCenterPos({'x':0, 'y':-3.1125})

    # set general values
    kicad_mod.addText('reference', 'REF**', {'x':0, 'y':-6.5}, 'F.SilkS')
    #kicad_mod.addText('user', '%R', {'x':0, 'y':-6.5}, 'F.Fab')
    kicad_mod.addText('value', footprint_name, {'x':0, 'y':1.5}, 'F.Fab')

    #create outline
    # create Courtyard
    # output kicad model

    #create pads
    createNumberedPadsSMD(kicad_mod, pincount, pad_spacing, {'x':pad_w,'y':pad_h}, -4.675)

    #add mounting pads (no number)
    mpad_w = 1.0
    mpad_h = 2.0
    mpad_x = (B/2) - (mpad_w/2)
    mpad_y = -0.7 - 1.7/2

    kicad_mod.addPad('""', 'smd', 'rect', {'x':mpad_x, 'y':mpad_y}, {'x':mpad_w, 'y':mpad_h}, 0, ['F.Cu', 'F.Paste', 'F.Mask'])
    kicad_mod.addPad('""', 'smd', 'rect', {'x':-mpad_x, 'y':mpad_y}, {'x':mpad_w, 'y':mpad_h}, 0, ['F.Cu', 'F.Paste', 'F.Mask'])

    #offset
    o = 0.15
    
    #add bottom line
    kicad_mod.addPolygoneLine([{'x':-B/2-o,'y':-0.1},
                             {'x':-B/2-o,'y':0.15},
                             {'x':B/2+o,'y':0.15},
                             {'x':B/2+o,'y':-0.1}])
                             
    #add left line
    kicad_mod.addPolygoneLine([{'x':-B/2-o,'y':-3.1},
                                {'x':-B/2-o,'y':-4.45},
                                {'x':-A/2-pad_w/2-0.4,'y':-4.45},
                                {'x':-A/2-pad_w/2-0.4,'y':-5.45}
                                ])

    #add right line
    kicad_mod.addPolygoneLine([{'x':B/2+o,'y':-3.1},
                                {'x':B/2+o,'y':-4.45},
                                {'x':A/2+pad_w/2+0.5,'y':-4.45}])

    #add connector outline to F.Fab
    y1 = -4.3
    y2 = y1 + 4.3

    kicad_mod.addRectLine(
        {'x': -B/2,'y': y1},
        {'x': B/2,'y': y2},
        'F.Fab', 0.15
    )
    
    x1 = -B/2 + 1   
                              
    y1 = -5
    
    marker = [
        {'x':x1,'y':y1},
        {'x':x1-0.5,'y':y1-0.25},
        {'x':x1-0.5,'y':y1+0.25},
        {'x':x1,'y':y1}
        ]

    #add designator for pin #1
    kicad_mod.addPolygoneLine(marker)
    kicad_mod.addPolygoneLine(marker,layer='F.Fab')
                              
    #add courtyard
    
    #courtyard corners
    cx1 = -B/2 - 0.5
    cx2 =  B/2 + 0.5
    
    cy1 = -5.8
    cy2 = 0.6
    
    #make sure they lie on an 0.05mm grid
    
    cx1 = int(cx1/0.05) * 0.05
    cx2 = int(cx2/0.05) * 0.05
    
    cy1 = int(cy1/0.05) * 0.05 - 0.0625
    cy2 = int(cy2/0.05) * 0.05 + 0.0375
    
    kicad_mod.addRectLine({'x':cx1,'y':cy1},{'x':cx2,'y':cy2},'F.CrtYd',0.05)

    f = open(footprint_name + ".kicad_mod","w")

    f.write(kicad_mod.__str__())

    f.close()
