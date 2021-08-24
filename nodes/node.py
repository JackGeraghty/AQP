import importlib
import logging
import drawoptions as dopt

from pathlib import Path

LOGGER = logging.getLogger('pipeline')
        

AVAILABLE_NODES = {path.name[:-len('.py')].lower():str(path)[:-len('.py')].lower().replace('/', '.') for path in Path('nodes/').rglob('*.py')}
LOGGER.info("Available Nodes: %s", AVAILABLE_NODES)

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
    type_ = data['type']
    module = AVAILABLE_NODES[type_.lower()]
    class_ = getattr(importlib.import_module(module), type_)
    return class_(**data)

