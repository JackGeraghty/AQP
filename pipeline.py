import argparse
import json
import logging
import sys
import networkx as nx

from pathlib import Path
from nodes.graphnode import build_graph, build_traversal_dfs, expand_graph
from networkx.drawing.nx_pydot import write_dot

VERSION = '0.5'
logging.basicConfig(format='%(asctime)s, %(levelname)s %(message)s', datefmt='%H:%M:%S')
LOGGER = logging.getLogger('pipeline')


def main() -> None:
    parser = init_argparser()
    args = parser.parse_args()
    LOGGER.setLevel(logging.DEBUG if args.debug else logging.INFO)
    if args.plot_call_graph and not args.graph_output_file:
        raise ValueError('If plotting call graph then the output file must also be specified')
        sys.exit(-1)
    
    call_graph = load_graph_from_file(args.graph_config_path)
    result = {}
    
    traversal_order = build_traversal_dfs(call_graph, [], args.root_node_id)
    LOGGER.debug("Pipeline Traversal Order: %s", traversal_order)    
    
    if args.plot_call_graph:
        expanded_graph = expand_graph(call_graph, args.root_node_id)
        expanded_name = args.graph_output_file + '_expanded.dot'
        for node in expanded_graph.nodes:
            draw_options = expanded_graph.nodes[node]['data'].draw_options
            if draw_options:
                expanded_graph.nodes[node].update(draw_options)
        write_dot(expanded_graph, expanded_name)
        write_dot(call_graph, args.graph_output_file + '.dot')    
        LOGGER.info('Graphs written to .dot files')
    
    for n_id in traversal_order:
        result = call_graph.nodes[n_id]['data'].execute(result)
    
    return


def load_graph_from_file(path_to_graph_config: str) -> nx.DiGraph:
    '''
    Builds the call_graph from the graph configuration file given to the 
    program via command-line

    Returns
    -------
    graph : nx.DiGraph
        The call_graph built from the config file

    '''
       
    try:    
        with open(Path(path_to_graph_config), 'rb') as file_data:
            data = json.load(file_data)
    except FileNotFoundError as err:
        LOGGER.warn('%s', err)
        sys.exit(-1)
    
    return build_graph(data)
            
        
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
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('--root_node_id', required=True)
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--graph_config_path', default='config/graph.json')
    optional.add_argument('--plot_call_graph', action='store_true', default=False)
    optional.add_argument('--graph_output_file', default='results/graph')
    optional.add_argument('--debug', action='store_true', default=False)
    optional.add_argument('-v', '--version', action='version', version=f'{parser.prog} version {VERSION}')
    return parser

if __name__ == '__main__':
    main()
