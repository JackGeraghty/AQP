from .node import AQPNode

class TupleTransformationNode(AQPNode):
    
    def __init__(self, id_, children, 
                 tuple_keys=['reference_file', 'degraded_keys'],
                 prepend_resources=True, 
                 draw_options=None, **kwargs):
        super().__init__(id_, children, draw_options=draw_options, **kwargs)
        self.tuple_keys = tuple_keys
        self.prepend_resources = prepend_resources
        self.type_ = "TupleTransformNode"
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        for i in range(len( list(zip(self.tuple_keys, kwargs['var'])))):
            file_path = f"resources/{kwargs['var'][i]}" if self.prepend_resources else kwargs['var'][i]
            result[self.tuple_keys[i]] = file_path
        return result