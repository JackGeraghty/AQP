"""Module containing the SinkNode. A Node used to gather multiple branches before allowing it's child node to be executed."""
from .node import AQPNode

class SinkNode(AQPNode):
    """SinkNode forces the traversal of the pipeline to switch branch until the number of expected results has been seen."""
    
    def __init__(self, id_: str, num_expected_results: int, 
                 draw_options: dict=None, **kwargs):
        """Initialize a SinkNode.

        Parameters
        ----------
        num_expected_results : int
            The number of result required to be seen before allowing the 
            children of this node to be executed.

        """
        super().__init__(id_, draw_options=draw_options, **kwargs)
        self.num_expected_results = num_expected_results
        self.counter = 0
        self.type_ = 'SinkNode'
       

    def execute(self, result: dict, **kwargs):
        """Execute the SinkNode.
        
        Will return None until the number of expected results is equal to the 
        number of results seen. Then returns the result dict.
        """
        super().execute(result, **kwargs)
        self.counter += 1
        return result if self.counter == self.num_expected_results else None