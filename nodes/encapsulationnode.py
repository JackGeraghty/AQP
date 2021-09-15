"""Module containing the EncapsulationNode. A node used to encapsulate a set of nodes."""

import logging
import sys
import json
import graphutils

from .node import AQPNode
from pathlib import Path
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class EncapsulationNode(AQPNode):
    """An EncapsulationNode is used to group a set of nodes together.
    
    These nodes are then executed as a single operation. 
    
    Example: encapsulating most of the 
    visqol functionality to avoid having to declare the full config repeatedly.
    """
    
    def __init__(self, id_: str, start_node: str,
                 node_data: dict=None, path_to_node_config: str=None,
                 draw_options: dict=None, **kwargs):
        """Initialize an EncapsulationNode.

        Parameters
        ----------
        start_node : str
            The root node of the encapsulated graph.
        node_data: dict
            Dictionary containing the node definition to be encapsulated by 
            this node. Cannot be set if path_to_config is set.
        path_to_node_config : str
            Path to the config file containing the full graph definition to use.
            Cannot be set if node_data is set.
        """
        super().__init__(id_, draw_options=draw_options, **kwargs)
        if (node_data and path_to_node_config) or (node_data is None and path_to_node_config is None):
            raise ValueError('One of node_data or path_to_node_config must be set. Not neither and not both.')
            sys.exit(-2)
            
        if path_to_node_config:  
            try:
                with open(Path(path_to_node_config), 'rb') as data:
                    node_data = json.load(data)
            except (FileNotFoundError) as err:
                LOGGER.error(err)
                sys.exit(-1)
        self.nodes = graphutils.build_graph(node_data)
        self.execution_node = self.nodes[start_node]
        self.type_ = 'EncapsulationNode'


    def execute(self, result: dict, **kwargs):
        """Execute each node in the encapsulated graph.
        
        Runs each node contained in the stored execution node. Starting with 
        the execution_node and working it's way through the children of that 
        node.
        """
        super().execute(result, **kwargs)
        graphutils.run_node(self.execution_node, result, **kwargs)
        return result
