import logging
from .node import AQPNode, deserialize

LOGGER = logging.getLogger('pipeline')

class LoopNode(AQPNode):
    
    def __init__(self, id_, children, output_key, node_data, iterable_key, flatten_output=False, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.iterable_key = iterable_key
        node_data['id_'] = self.id_
        self.execution_node = deserialize(node_data)
        self.failed_iterations = []    
        self.type_ = 'LoopNode'
        self.flatten_output = flatten_output

        
    def execute(self, result, **kwargs):
        super().execute(result)
        results = {}
        for i in result[self.iterable_key]:
            LOGGER.warn("Running on iterable entry: %s", i)
            
            result_copy = result.copy()
            result_copy['iterator_key'] = i
            try :    
                result_copy = self.execution_node.execute(result_copy, var=i)
                results[i] = result_copy
            except:
                LOGGER.warn("FAILED ITERATION %s", i)
                self.failed_iterations.append(i)
                
        if self.flatten_output:
            result = {**result, **results}
            
        else:
            result[self.output_key] = results
        LOGGER.info("%s", self.failed_iterations)
        LOGGER.info("%s", len(self.failed_iterations))
        return result