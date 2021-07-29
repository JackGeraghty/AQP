from .node import Node

class IdentityNode(Node):
    '''
        Identity node represents a node which performs no action on the previous
        result and simply passes the result along. 
        
        USE CASE: Testing graph structure
    '''
    def __init__(self, id_, children, output_key='None', **kwargs):
        super().__init__(id_, children, output_key)
        self.type_ = 'IdentityNode'


    def execute(self, result):
        super().execute(result)
        return result