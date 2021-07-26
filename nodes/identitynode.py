import json
from dataclasses import dataclass, field
from .node import Node

@dataclass
class IdentityNode(Node):
    '''
        Identity node represents a node which performs no action on the previous
        result and simply passes the result along. 
        
        USE CASE: Testing graph structure
    '''
    EXPECTED_INPUT_KEYS: tuple = field(default_factory=tuple)
    EXPECTED_OUTPUT_KEYS: tuple = field(default_factory=tuple)
    
    type_: str = 'IdentityNode'
    
    
    def __getstate__(self):
        state = super().__getstate__()
        state['type_'] = self.type_
        module, name = super().get_fullname()
        state['class_name'] = name
        state['module'] = module
        return state
    
    
    def __setstate__(self, state):
        super().__setstate__(state)
        
    
    def serialize(self):
        return json.dumps(self.__getstate__())

    
    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.__setstate__(data)
        return obj
    
    
    def execute(self, result):
        super().execute(result)
        return result
    