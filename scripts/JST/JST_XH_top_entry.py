#!/usr/bin/env python

import sys
sys.path.append(r'''C:\kicad\fp-gen\kicad_mod''')

from kicad_mod import KicadMod, createNumberedPadsTHT

# http://www.jst-mfg.com/product/pdf/eng/ePH.pdf

pitch = 2.50

for pincount in [5]: #range(2,16):

    jst = "B{pincount:01}B-XH".format(pincount=pincount)
    
    # Through-hole type shrouded header, Top entry type
    footprint_name = "JST_XH_" + jst + "_{pincount:02}x2.50mm_Straight".format(pincount=pincount)

    kicad_mod = KicadMod(footprint_name)
    kicad_mod.setDescription("JST XH series connector, " + jst)
    kicad_mod.setTags('connector jst xh')

    # set general values
    kicad_mod.addText('reference', 'REF**', {'x':0, 'y':-5}, 'F.SilkS')
    kicad_mod.addText('value', footprint_name, {'x':0, 'y':4}, 'F.Fab')

    # create Silkscreen
    """
    kicad_mod.addRectLine({'x':-1.95, 'y':2.8}, {'x':(pincount-1)*2+1.95, 'y':-1.7}, 'F.SilkS', 0.15)

    kicad_mod.addPolygoneLine([{'x':0.5, 'y':-1.7}
                              ,{'x':0.5, 'y':-1.2}
                              ,{'x':-1.45, 'y':-1.2}
                              ,{'x':-1.45, 'y':2.3}
                              ,{'x':(pincount-1)*2+1.45, 'y':2.3}
                              ,{'x':(pincount-1)*2+1.45, 'y':-1.2}
                              ,{'x':(pincount-1)*2-0.5, 'y':-1.2}
                              ,{'x':(pincount-1)*2-0.5, 'y':-1.7}], 'F.SilkS', 0.15)

    kicad_mod.addLine({'x':-1.95, 'y':-0.5}, {'x':-1.45, 'y':-0.5}, 'F.SilkS', 0.15)
    kicad_mod.addLine({'x':-1.95, 'y':0.8}, {'x':-1.45, 'y':0.8}, 'F.SilkS', 0.15)

    kicad_mod.addLine({'x':(pincount-1)*2+1.45, 'y':-0.5}, {'x':(pincount-1)*2+1.95, 'y':-0.5}, 'F.SilkS', 0.15)
    kicad_mod.addLine({'x':(pincount-1)*2+1.45, 'y':0.8}, {'x':(pincount-1)*2+1.95, 'y':0.8}, 'F.SilkS', 0.15)

    kicad_mod.addPolygoneLine([{'x':-0.3, 'y':-1.7}
                              ,{'x':-0.3, 'y':-1.9}
                              ,{'x':-0.6, 'y':-1.9}
                              ,{'x':-0.6, 'y':-1.7}], 'F.SilkS', 0.15)
    kicad_mod.addLine({'x':-0.3, 'y':-1.8}, {'x':-0.6, 'y':-1.8}, 'F.SilkS', 0.15)
    
    #add pins

    for i in range(0, pincount-1):
        middle_x = 1+i*2
        start_x = middle_x-0.1
        end_x = middle_x+0.1
        kicad_mod.addPolygoneLine([{'x':start_x, 'y':2.3}
                                  ,{'x':start_x, 'y':1.8}
                                  ,{'x':end_x, 'y':1.8}
                                  ,{'x':end_x, 'y':2.3}], 'F.SilkS', 0.15)
        kicad_mod.addLine({'x':middle_x, 'y':2.3}, {'x':middle_x, 'y':1.8}, 'F.SilkS', 0.15)
        
    # create Courtyard
    kicad_mod.addRectLine({'x':-1.95-0.5, 'y':2.8+0.5}, {'x':(pincount-1)*2+1.95+0.5, 'y':-1.7-0.5}, 'F.CrtYd', 0.05)
    """
    
    drill = 1
    
    if (pincount > 2): drill = 0.9

    dia = 2
    
    # create pads
    createNumberedPadsTHT(kicad_mod, pincount, pitch, drill, {'x':2, 'y':2})

    # output kicad model
    f = open(footprint_name + ".kicad_mod","w")

    f.write(kicad_mod.__str__())

    f.close()
