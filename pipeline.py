"""Main script for running the pipeline.

This script takes in the command line arguments, builds the execution graph of
the pipeline, and then executes the pipeline.

Command Line Args:
    Required:
        --root_node_id: id for the first node to be executed in the graph.
        
    Optional:
        --graph_config_path: path to the JSON file containing the definition 
        of the graph.
        
        --plot_graph: If used a .dot file will be generated for the execution 
        graph and an expanded version of the execution graph if applicable.

        --graph_output_file: Path to directory to store the generated .dot 
        files in.
        
        --debug: Enables debug level logging.
        
        --version: displays the version info.
"""
# /usr/bin/env python3.9

import argparse
import json
import logging
import sys
import graphutils
import graphvis
import time
import subprocess

from shutil import which
from pathlib import Path
from constants import LOGGER_NAME

VERSION = '1.1.0'
logging.basicConfig(
    format='%(asctime)s, %(levelname)s %(message)s', datefmt='%H:%M:%S')
LOGGER = logging.getLogger(LOGGER_NAME)


def main() -> None:
    """Create, plot and run the pipeline."""
    parser = init_argparser()
    args = parser.parse_args()
    LOGGER.setLevel(logging.DEBUG if args.debug else logging.INFO)
    if args.plot_graph and not args.graph_output_file:
        raise ValueError(
            'If plotting call graph then the output file must also be specified')

    try:
        with open(Path(args.graph_config_path), 'rb') as data:
            nodes = graphutils.build_graph(json.load(data))
            root_node = nodes[args.root_node_id]
            LOGGER.info('Performing validation checks')
            valid, ordering = graphutils.validate_graph(root_node)
            # Exit if not valid
            if not valid:
                LOGGER.error('Failed validation')
                sys.exit(1)
            LOGGER.info('Passed validation')
    except FileNotFoundError as err:
        LOGGER.error(err)
        sys.exit(1)

    if args.plot_graph:
        dot = graphvis.generate_dot_file(ordering)
        try:
            with open(args.graph_output_file + '.dot', 'w+') as f:
               LOGGER.info(f'Succesfully opened {args.graph_output_file}.dot')
               f.write(dot)
        except FileNotFoundError as err:
            LOGGER.error(err)

        if which('dot'):
            LOGGER.info('Found the dot command, creating svg and png output for dot file')
            svg_dot_command = f'dot -Tsvg {args.graph_output_file}.dot -o {args.graph_output_file}.svg'
            subprocess.call(svg_dot_command, shell=True)
            png_dot_command = f'dot -Tpng {args.graph_output_file}.dot -o {args.graph_output_file}.png'
            subprocess.call(png_dot_command, shell=True)
            LOGGER.info('Finished creating output iamges from dot file')

    # If we're just performing validation then exit with an ok status code
    if args.validate:
        LOGGER.info('Just performing validation, exitting early')
        sys.exit(0)

    result = {}
    start_time = time.time()
    LOGGER.info("Running pipeline...")
    graphutils.run_node(root_node, result)
    LOGGER.info("Finished running pipeline.")
    end_time = time.time()
    LOGGER.info(f'Elapsed time: {end_time - start_time}')
    

def init_argparser() -> argparse.ArgumentParser:
    """Initialize an argument parser with all of the possible command line arguments that can be passed to AQP.

    Returns
    -------
    parser: argparse.ArgumentParser
        Parser to be used to parse arguments
    """
    parser = argparse.ArgumentParser(usage="%(prog)s", description="AQP")
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('--root_node_id', required=True)
    required.add_argument('--graph_config_path', required=True)
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--plot_graph',action='store_true', default=False)
    optional.add_argument('--graph_output_file', default='results/graph')
    optional.add_argument('--debug', action='store_true', default=False)
    optional.add_argument('--validate', action='store_true', default=False)
    optional.add_argument('-v', '--version', action='version',
                          version=f'{parser.prog} version {VERSION}')
    return parser


if __name__ == '__main__':
    main()
