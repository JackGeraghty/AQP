"""Module containg the abstract Node implementations."""

import logging
import drawoptions as dopt

from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class Node(object):
    """Base abstract implementation of the Node class.
    
    Contains the information common to all(Most) Nodes:
        id_: string id of the node, used for connecting nodes together.
        output_key: Used for storing the result back to the results dictionary.
        draw_options: Used for generating the .dot file output of the execution
        graph.
    """

    def __init__(self, id_: str, output_key: str, draw_options: dict, **kwargs):
        """Init function of all nodes.
        
        Common initialization of all nodes.

        Parameters
        ----------
        id_ : str
            String id of the node. Used for connecting nodes and printing info.
        output_key : str, optional
            Key used for assigned the result of the execute function to the 
            results dictionary. The default is None, for when no value is 
            assigned to the dictionary.
        draw_options : dict, optional
            Options for drawing a node when creating the .dot file of the 
            execution graph. Passed a dictionary containing the desired options.
            The default is None.

        Returns
        -------
        None.

        """
        self.id_ = id_
        self.output_key = output_key
        self.draw_options = draw_options
        self.type = '__node__'


    def execute(self, result: dict, **kwargs):
        """Encapsulate the logic of a given node, whether it's loading a signal, or creating spectrograms etc.

        Parameters
        ----------
        result : dict
            The results dictionary passed throughout the entire pipeline. 
        **kwargs : dict
            Used to provide any additonal keyword args to the execute function.

        Returns
        -------
        None.

        """
        LOGGER.debug(f'Executing node {self.id_} | type={self.type_}')


    def is_leaf(self):
        """Check whether or not this node is a leaf node, i.e. no children."""
        return len(self.children) == 0


class AQPNode(Node):
    """Class for the core nodes of the pipeline, that should be reusable regardless of the quality metric being tested.
        
    Only difference between this and the base Node class is this class 
    contains specific drawing options for producing a graph. These options
    are overridable and are just used to differentiate between nodes.
    """
    
    def __init__(self, id_: str,  output_key: str=None, draw_options: dict=None, **kwargs):
        super().__init__(id_, output_key=output_key, draw_options=dopt.create_full_options(dopt.DRAW_OPTIONS['AQP'], draw_options))


class ViSQOLNode(Node):
    """Class for the ViSQOL nodes of the pipeline, e.g. ViSQOLStructuresNode.
        
    Only difference between this and the base Node class is this class 
    contains specific drawing options for producing a graph. These options
    are overridable and are just used to differentiate between nodes.
    """
    
    def __init__(self, id_, output_key=None, draw_options=None, **kwargs):
        super().__init__(id_, output_key=output_key, draw_options=dopt.create_full_options(dopt.DRAW_OPTIONS['ViSQOL'], draw_options))
        
        
class PESQNode(Node):
    """Class for the PESQ node(s) of the pipeline.
    
    Only difference between this and the base Node class is this class 
    contains specific drawing options for producing a graph. These options
    are overridable and are just used to differentiate between nodes.
    """
    
    def __init__(self, id_: str, output_key: str=None, draw_options: dict=None, **kwargs):
        super().__init__(id_, output_key=output_key, draw_options=dopt.create_full_options(dopt.DRAW_OPTIONS['PESQ'], draw_options))


class WarpQNode(Node):
    """Class for the WARP-Q node(s) of the pipeline.
    
    Only difference between this and the base Node class is this class 
    contains specific drawing options for producing a graph. These options
    are overridable and are just used to differentiate between nodes.
    """
    
    def __init__(self, id_: str, output_key: str=None, draw_options: dict=None, **kwargs):
        super().__init__(id_, output_key=output_key, draw_options=dopt.create_full_options(dopt.DRAW_OPTIONS['WARP-Q'], draw_options))