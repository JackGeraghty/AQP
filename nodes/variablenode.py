from .node import Node

class VariableNode(Node):
    
    def __init__(self, id_, output_key, children, variable_value, **kwargs):
        super().__init__(id_, output_key, children)
        self.variable_value = variable_value
        self.type_ = 'VariableNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        result[self.output_key] = self.variable_value
        return result