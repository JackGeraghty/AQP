import importlib
import logging

class Node(object):
    
    def __init__(self, id_, children, output_key='None', draw_options=None):
        self.id_ = id_
        self.children = children
        self.output_key = output_key
        self.draw_options = None
        self.type = '__node__'
        self.LOGGER = logging.getLogger('pipeline')
        

    def execute(self, result: dict, **kwargs):
        print(f'Executing node {self.id_} | type={self.type_}')
        
        
def deserialize(data):
    module_name = 'nodes.' + data['module']
    class_ = getattr(importlib.import_module(module_name), data['class'])
    return class_(**data)

