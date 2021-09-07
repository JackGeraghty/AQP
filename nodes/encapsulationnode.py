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
    
    def __init__(self, id_: str, start_node: str, path_to_node_config: str,
                 draw_options: dict=None, **kwargs):
        """Initialize an EncapsulationNode.

        Parameters
        ----------
        start_node : str
            The root node of the encapsulated graph.
        path_to_node_config : str
            Path to the config file containing the full graph definition to use.
        """
        super().__init__(id_, draw_options=draw_options, **kwargs)
        try:
            with open(Path(path_to_node_config), 'rb') as data:
                self.execution_node = graphutils.build_graph(json.load(data), start_node)
        except (FileNotFoundError) as err:
            LOGGER.error(err)
            sys.exit(-1)
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
