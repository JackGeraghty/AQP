import logging
from .node import AQPNode, deserialize

LOGGER = logging.getLogger('pipeline')

class LoopNode(AQPNode):
    
    def __init__(self, id_, children, output_key, node_data, iterable_key, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.iterable_key = iterable_key
        node_data['id_'] = self.id_
        self.execution_node = deserialize(node_data)
        self.type_ = 'LoopNode'

        
    def execute(self, result, **kwargs):
        super().execute(result)
        results = {}
        for i in result[self.iterable_key]:
            LOGGER.info("Running on iterable entry: %s", i)
            result_copy = result.copy()
            result_copy['iterator_key'] = i
            result_copy = self.execution_node.execute(result_copy, var=i)
            results[i] = result_copy
        result[self.output_key] = results
        return result