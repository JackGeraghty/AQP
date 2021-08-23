from .node import Node

class VariableNode(Node):
    
    def __init__(self, id_, children, output_key, variable_value, draw_options=None,**kwargs):
        super().__init__(id_, children, output_key=output_key, draw_options=draw_options)
        self.variable_value = variable_value
        self.type_ = 'VariableNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        result[self.output_key] = self.variable_value
        return result