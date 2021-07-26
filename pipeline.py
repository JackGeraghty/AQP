import argparse
import json
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path
from nodes.node import deserialize

VERSION = '0.1'

def main() -> None:
    parser = init_argparser()
    args = parser.parse_args()
    call_graph = build_graph(args.graph_config_path)
    
    if args.plot_call_graph:    
        nx.draw_planar(call_graph, with_labels=True)
        plt.draw()

    result = {
            'ref_signal_path': 'resources/ref.wav',
            'deg_signal_path': 'resources/deg.wav',
    }

    traversal_order = build_traversal_dfs(call_graph, [], 0)
    for n_id in traversal_order:
        result = call_graph.nodes[n_id]['data'].execute(result)
        
    return


def build_traversal_dfs(graph: nx.DiGraph, traversal_list: list[int], node: int) -> list[int]:
    '''
    Slightly modified depth first search(dfs). Difference being regular dfs 
    marks nodes as visited so in the situation where a two nodes of different
    branches point to a shared node, that shared node will only get visited once.
    
    The pipeline doesn't want this functionality, in that situation, the shared
    node should be visited twice.
    
    Traversal list is build using recursion. Stopping condition is a node is
    reached that has no children.

    Parameters
    ----------
    graph : nx.DiGraph
        The graph representing the pipeline.
    traversal_list : list[int]
        A list used to store the traversal order. 
    node : int
        The current node index being evaluated.

    Returns
    -------
    traversal_list[int]
        A list containing the traversal order of the graph.

    '''
    traversal_list.append(node)
    children = graph.nodes[node]['data'].children
    for n in children:
        build_traversal_dfs(graph, traversal_list, n)
    
    return traversal_list
    

def build_graph(path_to_graph_config: str) -> nx.DiGraph:
    '''
    Builds the call_graph from the graph configuration file given to the 
    program via command-line

    Returns
    -------
    graph : nx.DiGraph
        The call_graph built from the config file

    '''
    edges = []
    graph = nx.DiGraph()
    with open(Path(path_to_graph_config), 'rb') as file_data:
        data = json.load(file_data)
        for node in data:
            node_id = data[node]['id_']
            adjacent_nodes = data[node].pop('adjacent_nodes')
            graph.add_node(node_id, data=deserialize(data[node]) )
            if len(adjacent_nodes) > 0:
                graph.nodes[node_id]['data'].children.update(adjacent_nodes)
                edges.extend([(node_id, other_id) for other_id in adjacent_nodes])
    graph.add_edges_from(edges)
    return graph


def init_argparser() -> argparse.ArgumentParser:
    """
        Creates an argument parser with all of the possible
        command line arguments that can be passed to AQP

        Returns
        -------
        parser: argparse.ArgumentParser
            Parser to be used to parse arguments
    """

    parser = argparse.ArgumentParser(usage="%(prog)s",description="AQP")
    
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--graph_config_path', default='config/graph.json')
    optional.add_argument('--plot_call_graph', action='store_true', default=False)
    optional.add_argument('-v', '--version', action='version', version=f'{parser.prog} version {VERSION}')
    return parser

if __name__ == '__main__':
    main()
