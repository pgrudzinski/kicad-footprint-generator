'''
kicad-footprint-generator is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kicad-footprint-generator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.

(C) 2016 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
'''

from KicadModTree.Point import *
from KicadModTree.nodes.Node import Node
from KicadModTree.nodes.base.Line import Line


class PolygoneLine(Node):
    def __init__(self, **kwargs):
        Node.__init__(self)
        
        self._initMirror(**kwargs)
        self._initPolygone(**kwargs)

        self.layer = kwargs.get('layer', 'F.SilkS')
        self.width = kwargs.get('width')
        

        self.virtual_childs = self._createChildNodes(self.polygone_line, **kwargs)

    def _initMirror(self, **kwargs):
    
        self.mirror = [None,None]
        self.mirror[0] = kwargs.get('x_mirror',None)
        self.mirror[1] = kwargs.get('y_mirror',None)

    def _initPolygone(self, **kwargs):
        self.polygone_line = kwargs['polygone']
        
        for point in self.polygone_line:
        
            if self.mirror[0] is not None:
                point['x'] = 2 * self.mirror[0] - point['x']
            if self.mirror[1] is not None:
                point['y'] = 2 * self.mirror[1] - point['y']
            
    def _createChildNodes(self, polygone_line, **kwargs):
        nodes = []

        for line_start, line_end in zip(polygone_line, polygone_line[1:]):
            new_node = Line(start=line_start, end=line_end, **kwargs)
            new_node._parent = self
            nodes.append(new_node)

        return nodes

    def getVirtualChilds(self):
        return self.virtual_childs

    def _getRenderTreeText(self):
        render_text = Node._getRenderTreeText(self)
        render_text += " ["

        node_strings = []
        for node in self.polygone_line:
            node_position = Point(node)
            node_strings.append("[x: {x}, y: {y}]".format(x=node_position.x,
                                                          y=node_position.y))

        if len(node_strings) <= 6:
            render_text += " ,".join(node_strings)
        else:
            # display only a few nodes of the beginning and the end of the polygone line
            render_text += " ,".join(node_strings[:3])
            render_text += " ,... ,"
            render_text += " ,".join(node_strings[-3:])

        render_text += "]"

        return render_text
