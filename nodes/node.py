import importlib
from dataclasses import dataclass, field

@dataclass
class Node(object):

    type_: str = '_node_'
    id_: int = -1
    children: set = field(default_factory=set)
    
    def __getstate__(self):
        return {'type_': self.name, 'id_': self.id_, 'children': self.children}


    def __setstate__(self, state):
        self.id_ = state['id_']
        

    @classmethod
    def serialize(self):
        pass


    @classmethod
    def deserialize(cls, json_str):
        pass


    def execute(self, result: dict):
        print(f'Executing node {self.id_} | type={self.type_}')
        

    def get_fullname(o):
        klass = o.__class__
        module = klass.__module__
        if module == 'builtins':
            return klass.__qualname__ # avoid outputs like 'builtins.str'
        return module, klass.__qualname__


    def set_children(self, children):
        self.children = children
        
        
def deserialize(data):
    module_name = 'nodes.' + data['module']
    klass = getattr(importlib.import_module(module_name), data['class_name'])
    return klass.deserialize(data)

