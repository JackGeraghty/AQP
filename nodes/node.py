import importlib
import logging
import drawoptions as dopt

LOGGER = logging.getLogger('pipeline')

class Node(object):
    
    def __init__(self, id_, children, draw_options, output_key='None', **kwargs):
        self.id_ = id_
        self.children = children
        self.output_key = output_key
        self.draw_options = draw_options if draw_options else dopt.DrawOptionsBuilder().draw_options
        self.type = '__node__'
        
        
    def execute(self, result: dict, **kwargs):
        LOGGER.info(f'Executing node {self.id_} | type={self.type_}')


class ViSQOLNode(Node):
    
    def __init__(self, id_, children, output_key='None', draw_options=None, **kwargs):
        options_builder = dopt.ViSQOLOptionsBuilder(draw_options)
        super().__init__(id_, children, options_builder.draw_options, output_key)
        

class AQPNode(Node):
    
    def __init__(self, id_, children, output_key='None', draw_options=None, **kwargs):
        options_builder = dopt.AQPOptionsBuilder(draw_options)
        super().__init__(id_, children, options_builder.draw_options, output_key)


def deserialize(data):
    module_name = 'nodes.' + data['module']
    class_ = getattr(importlib.import_module(module_name), data['class'])
    return class_(**data)

