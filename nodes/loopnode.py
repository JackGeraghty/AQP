"""Module containing the LoopNode, a node used to loop over a set of ndoes."""

import logging
import graphutils

from .node import AQPNode
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class LoopNode(AQPNode):
    """Node which loops over some iterable contained within the result dictionary and executes it's execution node using that iterable value."""
    
    def __init__(self, id_: str, output_key: str, node_data: dict,
                 iterable_key: str, start_node: str, key_blacklist: list=None,
                 keys_to_keep: list=None,
                 draw_options: dict=None, **kwargs):
        """Initialize a LoopNode, id_, output_key and draw_options are same as Node.
    
        Parameters
        ----------
        node_data : dict
            Dictionary containing the JSON definition of the nodes which this 
            node is to loop over.
        iterable_key : str
            Key used to obtain the iterable from the result dictionary.
        start_node : str
            ID for the root node of the graph created from node_data.
        key_blacklist : list, optional
            List used to prevent the declared keys from being passed into the
            subgraph. This is used to prevent duplication of dictionary values.
            The default is None.

        Returns
        -------
        None.

        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options, **kwargs)
        self.iterable_key = iterable_key
        self.nodes = graphutils.build_graph(node_data)
        self.execution_node = self.nodes[start_node]
        self.key_blacklist = key_blacklist if key_blacklist else []
        self.keys_to_keep = keys_to_keep
        self.type_ = 'LoopNode'
        

    def execute(self, result: dict, **kwargs):
        """Execute the LoopNode.
        
        Loops over each entry found using the iterable_key and executes the
        subgraph. The result dictionary passed to the subgraph contains a new
        key, 'iterable_item'. This sub-dictionary is then added to the results.
        
        At the end of the loop, the results dictionary assigned to the result 
        dictionary.

        Parameters
        ----------
        result : dict
            The result dictionary used throughout the pipeline.

        Returns
        -------
        result : dict
            The result dictionary.

        """
        super().execute(result)
        results = {}
        for i in result[self.iterable_key]:
            LOGGER.info("Running on iterable entry: %s", i)
            result_copy = {k: result[k] for k in result if k not in self.key_blacklist}
            result_copy['iterator_item'] = i
            graphutils.run_node(self.execution_node, result_copy)
            results[i] = result_copy
        result[self.output_key] = results
        return result