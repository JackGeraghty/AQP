"""Module containing utility functions relating the creation and running of the pipeline."""

import importlib
import logging

from constants import LOGGER_NAME
from nodes.node import NestedNode, Node
from pathlib import Path
from typing import Dict, List, Tuple

LOGGER = logging.getLogger(LOGGER_NAME)

AVAILABLE_NODES = {path.name[:-len('.py')].lower(): str(path)[:-len('.py')].lower(
).replace('/', '.').replace('\\', '.') for path in Path('nodes/').rglob('*.py')}
LOGGER.debug("Available Nodes: %s", AVAILABLE_NODES)

# Global list of deserialized nodes
DESERIALIZED_NODES = []

# Global counter to ensure each node deserialized gets a unique int id
n_id = 0

def _deserialize(data: dict, node_id: str) -> Node:
    """Deserialize a dictionary, loaded from a json file to a Node
    
    parameters
    ----------
    data: dict
        Dictionary containing the definitions for each of the nodes and how
        they are connected to each other.
        
    returns
    -------
    node: Node
        Node deserialized from the dictionary definition.
    """
    type_ = data['type']
    LOGGER.info("Creating %s", node_id)
    module = AVAILABLE_NODES[type_.lower()]
    class_ = getattr(importlib.import_module(module), type_)
    node = class_(**data)
    node.set_n_id(data['n_id'])
    return node


def run_node(node: Node, result: dict, **kwargs):
    """IMPORTANT: Function responsible for running the entire pipeline.
    
    Takes in a node (usually a root node), and calls it's execute function. If
    the return value of calling execute is None, then it moves to the next 
    branch at the same level in the graph. 
    
    Operates using a version of Depth-First Search(DSF). It only deviates 
    from DFS when a None value is returned from a node's execute function. Each
    child node of the current node is added to the stack and evaluated in turn.
    
    This function can become recursive, if either a LoopNode or an 
    EncapsulationNode is used in the graph. Both of these nodes store an inner
    Node, which stores it's own children. They use this function to run each of
    the nodes contained within them.
    
    The result dictionary is the same one thoughout the entire function and any
    recursive functions. This results in it containing all the necessary 
    information for use when needed.
    

    Parameters
    ----------
    node : Node
        The first node to execute. Usually, the root node of the graph, or in
        the recursive case, the start_node of the inner graph.
    result : dict
        Dictionary containing the results of executing each node in the graph.

    Returns
    -------
    None.

    """
    stack = []
    stack.append(node)
    while len(stack) > 0:
        current_node = stack.pop()
        children = current_node.children
        if (r := current_node.execute(result, **kwargs)) is None:
            LOGGER.debug("None result, not continuing with this branch.")
            continue

        # If the execute function runs as intended, i.e. doesn't return None,
        # Then add each of the child nodes to the stack to be evaluated.
        for i in range(len(children)-1, -1, -1):
            stack.append(children[i])


def build_graph(graph_definition: dict) -> Dict[Node, str]:
    """
    Creates the graph using the provided graph definition. Does this by
    deserializing each node definition in the graph_definition. The children
    of each node are handled separately since the child node of a given node
    might not have been instantiated yet.
    
    Once all node have been initialized, the children of each node is updated
    by matching the string id_ of each node in the nodes dictionary to the 
    corresponding child nodes in the edges dictionary.
    
    Parameters
    ----------
    graph_definition : dict
        JSON representation of the graph loaded from a config file.

    Returns
    -------
    nodes : dict
        A dictionary containing all of the nodes
    """
    edges = {}
    nodes = {}
    global n_id
    for node_definition in graph_definition:
        graph_definition[node_definition]['id_'] = node_definition
        graph_definition[node_definition]['n_id'] = n_id
        n_id += 1
        DESERIALIZED_NODES.append(node_definition)
        nodes[node_definition] = _deserialize(graph_definition[node_definition], node_definition)
        edges[node_definition] = graph_definition[node_definition].get('children', [])

    for node_id in nodes:
        nodes[node_id].children = [nodes[n] for n in edges[node_id]]
    return nodes


def is_nested_node(node: Node) -> bool:
    """
        Simple function which wraps the isinstance call below. This function is 
        really just a rename that makes it more intuitive than isinstance(node, NestedNode)

        Parameters
        ----------
        node: Node
            The node to evaluate

        Returns
        -------
        is_nested_node: bool
            Indicates if the node is either a LoopNode or EncapsulationNode
    """
    return isinstance(node, NestedNode)


def check_for_cycles(start_node: Node) -> List[Node]:
    """
    Performs a check on the graph created from the json config for cycles. 
    The pipeline operates using a Directed Acylic Graph(DAG) so no cycles can exist

    Checks for cycles by performing a depth first search and maintaining a list of 
    visited nodes. If a node that is in the visited set appears again it is part 
    of a cyle. 

    Parameters
    ----------
    start_node : Node
        The node to start the dfs from

    Returns
    -------
        ordering: List[Node]
            A list containing the order in which nodes will be visited. Required for
            further validation of the graph. If a cycle is detected this function 
            returns None
        
    """
    stack = []
    stack.append(start_node)
    ordering = []
    visited = set()
    while len(stack) > 0:
        node = stack.pop()
        if node.n_id in visited:
            LOGGER.error("Cycle Detected, node with id %s is referenced to create a cycle", node.id_)            
            return None
        visited.add(node.n_id)
        ordering.append(node)
        children = node.children

        # If the current node is a nested node then append all the children first
        # then append the nodes' execution node. This ensures proper order since
        # the most recent element on the stack gets evaluated first, LIFO
        if is_nested_node(node):
            for child_node in children:
                stack.append(child_node)    
            stack.append(node.execution_node)
        else:
            for i in range(len(children)-1, -1, -1):
                stack.append(children[i])       

    return ordering


def has_unreachable_nodes(ordering: List[Node]) -> bool:
    """
    Performs a check for unreachable nodes in the graph. Unreachable nodes
    are likely not intended and can lead to time lost to debugging why the 
    graph pipeline isn't working as intended.

    Determines unreachable nodes by utilizing the ordering of nodes
    returned from the check_for_cycles function and an auxillary set
    created during node deserialization. It loops over each node that 
    was deserialized and checks to see if that node is within the 
    execution order of the nodes. If it's not there then it has been
    deserialized but is not reachable.

    Parameters
    ----------
    ordering: List[Node]
        List containing the order in which all nodes will be executed

    Returns
    -------
    has_unreachable_nodes: bool
        Boolean indicating whether or not there is an unreachable node
    """
    ordering_ids = [i.id_ for i in ordering]
    unreachable_nodes = set()
    for deserialized_node in DESERIALIZED_NODES:
        if deserialized_node not in ordering_ids:
            unreachable_nodes.add(deserialized_node)

    if len(unreachable_nodes) > 0:
        LOGGER.error("Found unreachable nodes %s", unreachable_nodes)
    return len(unreachable_nodes) != 0 


def validate_graph(root_node: Node) -> Tuple[bool, List[Node]]:
    """
    Checks the deserialized graph for cycles and unreachable nodes. Does
    this by running the check_for_cycles function followed by the 
    has_unreachable_nodes function.

    Parameters
    ----------
    root_node: Node
        The root node of the graph

    Returns
    -------
    validation_info: Tuple[bool, List[Node]]
        A tuple where the first element is a boolean indicating whether the 
        graph has unreachable nodes. This is negated to match up with name of 
        the function.

        The second element is then the execution order of the pipeline.
    """
    if (ordering := check_for_cycles(root_node)) is None:
        return False
    return not has_unreachable_nodes(ordering), ordering
