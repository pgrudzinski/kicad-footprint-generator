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

from KicadModTree.FileHandler import FileHandler
from KicadModTree.util.kicad_util import *
from KicadModTree.nodes.base.Pad import Pad  # TODO: why .KicadModTree is not enough?


DEFAULT_LAYER_WIDTH = {'F.SilkS': 0.12,
                       'B.SilkS': 0.12,
                       'F.Fab': 0.10,
                       'B.Fab': 0.10,
                       'F.CrtYd': 0.05,
                       'B.CrtYd': 0.05}

DEFAULT_WIDTH = 0.15


def get_layer_width(layer, width=None):
    if width is not None:
        return width
    else:
        return DEFAULT_LAYER_WIDTH.get(layer, DEFAULT_WIDTH)


class KicadFileHandler(FileHandler):
    def __init__(self, kicad_mod):
        FileHandler.__init__(self, kicad_mod)

    def serialize(self):
        serial_string = "(module {name} (layer F.Cu) (tedit {timestamp})\n".format(name=self.kicad_mod.name,
                                                                                   timestamp=formatTimestamp())

        if self.kicad_mod.description:
            serial_string += '  (descr "{description}")\n'.format(description=self.kicad_mod.description)

        if self.kicad_mod.tags:
            serial_string += '  (tags "{tags}")\n'.format(tags=self.kicad_mod.tags)

        if self.kicad_mod.attribute:
            serial_string += '  (attr {attr})\n'.format(attr=self.kicad_mod.attribute)

        serial_string += self.serializeTree()

        serial_string += ")"

        return serial_string

    def serializeTree(self):
        nodes = self.kicad_mod.serialize()

        grouped_nodes = {}

        for single_node in nodes:
            node_type = single_node.__class__.__name__

            current_nodes = grouped_nodes.get(node_type, [])
            current_nodes.append(single_node)

            grouped_nodes[node_type] = current_nodes

        serial_tree = ""

        # serialize initial text nodes
        if 'Text' in grouped_nodes:
            reference_nodes = list(filter(lambda node: node.type == 'reference', grouped_nodes['Text']))
            for node in reference_nodes:
                value_serialized = self.serialize_Text(node)
                if value_serialized:
                    value_serialized = value_serialized.replace('\n', '\n  ') + "\n"
                    serial_tree += "  " + value_serialized
                grouped_nodes['Text'].remove(node)

            value_nodes = list(filter(lambda node: node.type == 'value', grouped_nodes['Text']))
            for node in value_nodes:
                value_serialized = self.serialize_Text(node)
                if value_serialized:
                    value_serialized = value_serialized.replace('\n', '\n  ') + "\n"
                    serial_tree += "  " + value_serialized
                grouped_nodes['Text'].remove(node)

        for key, value in sorted(grouped_nodes.items()):
            # check if key is a base node, except Model
            if key not in {'Arc', 'Circle', 'Line', 'Pad', 'Text'}:
                continue

            # render base nodes
            for node in value:
                value_serialized = self._callSerialize(node)
                if value_serialized:
                    value_serialized = value_serialized.replace('\n', '\n  ') + "\n"
                    serial_tree += "  " + value_serialized

        # serialize 3D Models at the end
        if grouped_nodes.get('Model'):
            for node in grouped_nodes.get('Model'):
                value_serialized = self.serialize_Model(node)
                if value_serialized:
                    serial_tree += "  " + value_serialized.replace('\n', '\n  ') + "\n"

        return serial_tree

    def _callSerialize(self, node):
        '''
        call the corresponding method to serialize the node
        '''
        method_type = node.__class__.__name__
        method_name = "serialize_{0}".format(method_type)
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            exception_string = "{name} (node) not found, cannot serialized the node of type {type}"
            raise NotImplementedError(exception_string.format(name=method_name, type=method_type))

    def serialize_Arc(self, node):
        render_strings = ['fp_arc']
        # in KiCAD, some file attributes of Arc are named not in the way of their real meaning
        render_strings.append(node.getRealPosition(node.center_pos).render('(start {x} {y})'))
        render_strings.append(node.getRealPosition(node.start_pos).render('(end {x} {y})'))
        render_strings.append('(angle {angle:.1f})'.format(angle=node.angle))
        render_strings.append('(layer {layer})'.format(layer=node.layer))
        render_strings.append('(width {width})'.format(width=get_layer_width(node.layer, node.width)))

        return '({})'.format(' '.join(render_strings))

    def serialize_Circle(self, node):
        render_strings = ['fp_circle']
        render_strings.append(node.getRealPosition(node.center_pos).render('(center {x} {y})'))
        render_strings.append(node.getRealPosition(node.end_pos).render('(end {x} {y})'))
        render_strings.append('(layer {layer})'.format(layer=node.layer))
        render_strings.append('(width {width})'.format(width=get_layer_width(node.layer, node.width)))

        return '({})'.format(' '.join(render_strings))

    def serialize_Line(self, node):
        render_strings = ['fp_line']
        render_strings.append(node.getRealPosition(node.start_pos).render('(start {x} {y})'))
        render_strings.append(node.getRealPosition(node.end_pos).render('(end {x} {y})'))
        render_strings.append('(layer {layer})'.format(layer=node.layer))
        render_strings.append('(width {width})'.format(width=get_layer_width(node.layer, node.width)))

        return '({})'.format(' '.join(render_strings))

    def serialize_Text(self, node):
        render_strings1 = ['fp_text']
        render_strings1.append(lispString(node.type))
        render_strings1.append(lispString(node.text))

        at_real_position, real_rotation = node.getRealPosition(node.at, node.rotation)
        if real_rotation:
            render_strings1.append(at_real_position.render('(at {{x}} {{y}} {r})'.format(r=real_rotation)))
        else:
            render_strings1.append(at_real_position.render('(at {x} {y})'))

        render_strings1.append('(layer {layer})'.format(layer=node.layer))
        if node.hide:
            render_strings1.append('hide')
        render_strings_font = ['font']
        render_strings_font.append(node.size.render('(size {x} {y})'))
        render_strings_font.append('(thickness {thickness})'.format(thickness=node.thickness))

        render_strings2 = ['effects']
        render_strings2.append('({})'.format(' '.join(render_strings_font)))

        return "({str1}\n  {str2}\n)".format(str1=' '.join(render_strings1),
                                             str2='({})'.format(' '.join(render_strings2)))

    def serialize_Model(self, node):
        render_string = "(model {filename}\n".format(filename=node.filename)
        # TODO: apply position from parent nodes (missing z)
        render_string += "  (at {at})\n".format(at=node.at.render('(xyz {x} {y} {z})'))
        # TODO: apply scale from parent nodes
        render_string += "  (scale {scale})\n".format(scale=node.scale.render('(xyz {x} {y} {z})'))
        # TODO: apply rotation from parent nodes
        render_string += "  (rotate {rotate})\n".format(rotate=node.rotate.render('(xyz {x} {y} {z})'))
        render_string += ")"

        return render_string

    def serialize_Pad(self, node):
        render_strings = ['pad']
        render_strings.append(lispString(node.number))
        render_strings.append(lispString(node.type))
        render_strings.append(lispString(node.shape))

        position, rotation = node.getRealPosition(node.at, node.rotation)
        if not rotation % 360 == 0:
            render_strings.append(node.getRealPosition(node.at).render('(at {{x}} {{y}} {r})'.format(r=rotation)))
        else:
            render_strings.append(node.getRealPosition(node.at).render('(at {x} {y})'))

        render_strings.append(node.size.render('(size {x} {y})'))
        if node.type in [Pad.TYPE_THT, Pad.TYPE_NPTH]:
            if node.drill.x == node.drill.y:
                render_strings.append('(drill {})'.format(node.drill.x))
            else:
                render_strings.append(node.drill.render('(drill oval {x} {y})'))
        render_strings.append('(layers {})'.format(' '.join(node.layers)))

        return '({})'.format(' '.join(render_strings))

    def _callUnserialize(self, lisp_obj):
        '''
        call the corresponding method to serialize the node
        '''
        method_type = lisp_obj[0]
        method_name = "unserialize_{0}".format(method_type)
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            exception_string = "{name}(node) not found, cannot unserialized the node of type {type}"
            raise NotImplementedError(exception_string.format(name=method_name, type=method_type))

    def unserialize_fp_arc(self, node):
        raise NotImplementedError()
        return Arc()

    def unserialize_fp_circle(self, node):
        raise NotImplementedError()
        return Circle()

    def unserialize_fp_line(self, node):
        raise NotImplementedError()
        return Line()

    def unserialize_fp_text(self, node):
        raise NotImplementedError()
        return Text()

    def unserialize_model(self, node):
        raise NotImplementedError()
        return Model()

    def unserialize_pad(self, node):
        raise NotImplementedError()
        return Pad()
