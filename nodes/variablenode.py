"""Module containing the VariableNode, used to assign a constant value to the result dictionary."""

from .node import AQPNode

class VariableNode(AQPNode):
    """VariableNode is used to assign a constant value to the result dictionary when it's execute function is called."""
    
    def __init__(self, id_: str, output_key: str, 
                 variable_value: object, draw_options: dict=None,**kwargs):
        super().__init__(id_, output_key=output_key, draw_options=draw_options)
        self.variable_value = variable_value
        self.type_ = 'VariableNode'
    
    
    def execute(self, result: dict, **kwargs):
        """Execute the VariableNode and assign the stored value to the result dict."""
        super().execute(result)
        result[self.output_key] = self.variable_value
        return result