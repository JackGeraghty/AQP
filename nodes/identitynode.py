"""Module containing the IdentityNode class. A node which does nothing."""
from .node import AQPNode

class IdentityNode(AQPNode):
    """Identity node represents a node which performs no action on the previous result and simply passes the result along.
        
    USE CASE: Testing graph structure or inspecting the result dictionary.
    """
    
    def __init__(self, id_: str, output_key: str=None, 
                 draw_options: dict=None, **kwargs):
        """Initialize an IdentityNode."""
        if draw_options:
            draw_options['shape'] = 'oval'
        super().__init__(id_, draw_options=draw_options, **kwargs)
        self.type_ = 'IdentityNode'


    def execute(self, result: dict, **kwargs):
        """Do Nothing."""
        super().execute(result)
        return result