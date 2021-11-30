"""Module containing utility functions relating the creation and running of the pipeline."""

import importlib
import logging

from nodes.node import Node
from nodes.loopnode import LoopNode
from nodes.encapsulationnode import EncapsulationNode
from pathlib import Path
from typing import Dict
LOGGER_NAME = 'pipeline'
LOGGER = logging.getLogger(LOGGER_NAME)

AVAILABLE_NODES = {path.name[:-len('.py')].lower(): str(path)[:-len('.py')].lower(
).replace('/', '.').replace('\\', '.') for path in Path('nodes/').rglob('*.py')}
LOGGER.debug("Available Nodes: %s", AVAILABLE_NODES)


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


DESERIALIZED_NODES = []
n_id = 0

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


def check_for_cycles(start_node):
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

        if isinstance(node, (LoopNode, EncapsulationNode)):
            for c in children:
                stack.append(c)    
            stack.append(node.execution_node)
        else:
            for i in range(len(children)-1, -1, -1):
                stack.append(children[i])       

    return ordering


def has_unreachable_nodes(ordering):
    ordering_ids = [i.id_ for i in ordering]
    for deserialized_node in DESERIALIZED_NODES:
        if deserialized_node not in ordering_ids:
            LOGGER.error("Found unreachable node %s", deserialized_node)
            return True
    return False


def validate_graph(root_node):
    if (ordering := check_for_cycles(root_node)) is None:
        return False
    return not has_unreachable_nodes(ordering), ordering
