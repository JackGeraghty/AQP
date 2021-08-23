from .node import AQPNode

def zip_lists_to_tuple(file_names):
    l_one = file_names[0]
    l_two = file_names[1]
    l = []
    for i in range(len(l_one)):
        l.append((l_one[i], l_two[i]))
    return l

functions = {
        "zip_lists_to_tuple":  zip_lists_to_tuple
    }


class TransformNode(AQPNode):
    
    def __init__(self, id_, children, output_key, transform_name, target_key, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key=output_key, draw_options=draw_options)
        self.function = functions[transform_name]
        self.target_key = target_key
        self.type_ = "TransformNode"
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        x = self.function(result[self.target_key])
        result[self.output_key] = x
        return result
    
