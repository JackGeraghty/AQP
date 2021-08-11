from .node import AQPNode

class IdentityNode(AQPNode):
    '''
        Identity node represents a node which performs no action on the previous
        result and simply passes the result along. 
        
        USE CASE: Testing graph structure
    '''
    def __init__(self, id_, children, output_key='None', draw_options=None, **kwargs):
        if draw_options:
            draw_options['shape'] = 'oval'
        super().__init__(id_, children, draw_options=draw_options, **kwargs)
        self.type_ = 'IdentityNode'


    def execute(self, result):
        super().execute(result)
        return result