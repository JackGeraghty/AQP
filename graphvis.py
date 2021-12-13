import re
import json
import logging
import graphutils

from constants import LOGGER_NAME, DOT_CONFIG
from nodes.node import Node
from typing import List, Tuple

LOGGER = logging.getLogger(LOGGER_NAME)

def _build_visualization_data(ordering: List[Tuple[str, Node]]) -> List:
    """
    Function which generates the required data structure for creating the .dot file 
    output of the pipeline. Creates a nested list structure which indicates when 
    a subgraph/cluster needs to be drawn in the pipeline diagram. Also contains 
    the other information (draw_options, labels, etc.) for drawing the nodes.

    Parameters
    ----------
    ordering: List[Tuple [str, Node]]
        A list containing the order in which each node will be traversed during pipeline 
        execution
    
    Returns
    -------
    nested_structure: List
        A nested list containing the information required for visualization of the 
        pipeline
    """


    # is r_two within r_one
    # start indexes cannot be the same but can have the same end index
    def within_range(r_one: Tuple[int, int], r_two: Tuple[int, int]) -> bool:
        """
        Helper function to determine if one range is contained within another
        
        Parameters
        ----------
        r_one: Tuple[int, int]
            The first range
        r_two: Tuple[int, int]
            The second range

        Returns 
        -------
        within_range: bool
            A boolean indicating if r_two is contained within r_one
        """
        return  r_two[1] <= r_one[1] and r_two[0] > r_one[0]
    
    def check_membership(id_: int, nested_structure: List) -> bool:
        """
        Helper function to check to see if an id is contained within a nested list
        
        Parameters
        ----------
        id_: int
            The id to check for membership in the nested list
        nested_structure: List
            The list with nested data to check if id_ is a member of

        Returns
        -------
        check_membership: bool
            A boolean indicating if the given id is contained anywhere in the list with 
            nested data
        """
        for n in nested_structure:
            if isinstance(n, list):
                if check_membership(id_, n):
                    return True
            elif n.n_id == id_:
                return True
        return False
    
    info = {}
    prev = None

    # Step 1 - Find the ranges
    # Find the start and end indexes of every nested node
    # e.g. nodes = [identity, LoopNode, identity, end_loop, Output]
    # In the example a 2-tuple would be created with values 1 (for LoopNode) and 3 for end_loop
    #
    # Then use this 2-tuple as a dict key for the actually node range
    # (1,3): [LoopNode, identity, end_loop]
    # 
    # From this step we now have a dictionary with the start and end index of all nested ranges as keys and the values are 
    # the nested range themselves.

    for i in range(len(ordering)):
        current = ordering[i]

        if graphutils.is_nested_node(current):
            # Need to maintain a reference to the previous node
            # This required to handle the case of a nested Loop/Encapsulation Node
            # which doesn't have any children
            next_node = current.children[0] if current.children else prev.children[0]
            
            # When a NestedNode is found, loop from the current index until we find 
            # the child node of the current node in the ordering list. This will be 
            # located at the end of whatever nodes are encapsulated by the NestedNode
            for j in  range(i, len(ordering)):
                if ordering[j].n_id == next_node.n_id:
                    break
            info[(i, j)] = [x for x in ordering[i:j]]
            prev = current

    # Step 2 - Collapse/Merge the ranges
    # 
    # The idea behind this section of the algorithm is based off of the some properties of 
    # the ranges that were just created.
    #
    # Firstly, they're start indexes are monotonic. The first element in each tuple is strictly
    # less than the next start index
    #
    # Secondly, starting from end of the keys, the second element in each tuple is less than
    # or equal to the key below it. 
    # 
    # Thirdly, dictionary preserve the order in which keys are added
    #
    # Using these properties, it is possible to start at the end of keys and work backwards. For 
    # each tuple, check to see if any of the other ranges(that we've already evaluated) are contained within it. 
    # e.g. the range (2,4) is contained within the range (1,4) but not the other way around.
    #
    # If there is no contained ranges and we haven't seen the current range before, then just
    # add it to a dictionary with the nodes that are within that range.
    #
    # If there is contained ranges then a new dict value needs to be created. This new value
    # is comprised of the range that has already been evaluated, plus the nodes that are on
    # either side of the previously seen range of nodes.
    # e.g. nodes = [identity, encap, identity, LoopNode, identity, end_loop, Output]
    # gets ranges of (1,5): [encap, identity, LoopNode, identity, end_loop] and (3,5): [LoopNode, identity, end_loop]
    # The range (3,5) will be evaluated first. It's range and values will be put into the seen_ranges dictionary
    # Then when evaluating (1,5), the contained_ranges will list will contain the previously evaluated range (3,5)
    # The values missing from the seen_range dict are prepended (or appended, if needed) and the current range (1,5) is added
    # to the seen_ranges dict and then previous range (3,5) is removed.
    #
    # This process repeats until all ranges are collapsed to a single range which maps to a list with several nested sublists
    # Any time a new list is encountered in this list indicates a new cluster/subgraph of nodes
    #
    # Step 3 - Finalize the nested structure
    # With the subgraphs/clusters handled, the list needs to be finalized with the non-nested node information. These nodes 
    # usually the nodes before any encapsulation/loop node is reached and the nodes that are at the end of the pipeline
    # and not contained within any encapsualtion/loop node. 

    seen_ranges = {}
    indexes = [x for x in info]
    for i in range(len(indexes)-1, -1, -1):
        index_range = indexes[i]
        nodes_in_range = info[index_range]
        contained_ranges = [k for k in seen_ranges if within_range(index_range, k)]
        
        if len(contained_ranges) == 0 and index_range not in seen_ranges:
            seen_ranges[index_range] = nodes_in_range
        else:
            entry = contained_ranges[-1]
            
            current_start_index = index_range[0]
            amount_to_prepend =  entry[0] - current_start_index
            new_entry = []
            
            # Prepend nodes to the new list
            for j in range(current_start_index, current_start_index + amount_to_prepend):
                new_entry.append(ordering[j])

            # Need to reverse so that data gets added in the right order when popping
            contained_ranges.reverse()
            for r in contained_ranges:
                new_entry.append(seen_ranges[r])
                seen_ranges.pop(r, None)
            
            # Append the remaining data on the right side of the nested data
            for j in range(entry[1], index_range[1]):
                if not check_membership(ordering[j].n_id, new_entry):
                    new_entry.append(ordering[j])
            
            # Update the seen_ranges dict
            seen_ranges[index_range] = new_entry
   
    final_range = list(seen_ranges.keys())[0]
    final_nested_structure = []

    # Prepend nodes not contained within a nested node
    for i in range(final_range[0]):
        final_nested_structure.append(ordering[i])

    final_nested_structure.append(seen_ranges[final_range])
    
    # Append nodes not contained within a nested node.
    for i in range(final_range[1], len(ordering)):
        final_nested_structure.append(ordering[i])

    LOGGER.debug("Final Structure: %s", final_nested_structure)
    return final_nested_structure


def generate_dot_file(ordering: List[Node]) -> str:
    """
    Generates a dot representation of the pipeline. This visualization
    contains subgraph where appropriate, the connections between
    nodes, and the draw options for those nodes.

    Parameters
    ----------
    ordering: List
        A list containing the order in which each node will be traversed during pipeline 
        execution
    
    Returns
    -------
    A str representing the dot file contents. 
    """

    # Open up the default dot configuration file. Usually empty.
    # Useful for properties such as rankdir etc.
    try:
        with open(DOT_CONFIG, 'r') as dot_config: 
            parsed_config = json.load(dot_config)
    except FileNotFoundError as err:
        LOGGER.error(f'Failed to open config/dot_config.json {err}')
        parsed_config = {}
        
    # Get the nested structure required
    graph_data: List[Node] = _build_visualization_data(ordering)

    # Pattern to match any 6 or 8 character hex code so regular hex colour or
    # hex colour with an alpha component

    hex_str = '^#(?:[0-9a-fA-F]{2}){3,4}$'
    hex_pattern = re.compile(hex_str)

    # str which will be the contents of the dot file
    dot = 'digraph {\n'

    # Add all the dot config information
    for k,v in parsed_config.items():
        dot += f'\t{k}="{v}";\n'


    def create_nodes_and_clusters(nodes: List, indent_level: int=0) -> str:
        """
        Recursive function used to add in all the node information and the 
        subgraph/cluster information. Anytime a list is encountered in the
        nested structure, call this function and have it add the information

        Parameters
        ----------
        nodes: List
            A list of the nodes to add to the dot file. This is likely a 
            subset of the nodes if there is any level of nesting.
        indet_level: int
            Interger used to add tabs to the str. Purely for aesthetic purposes
            in the output file
        """
        nonlocal dot
        indents = indent_level * '\t'

        # For each entry:
        #   If it is a list, then add in the subgraph cluster_ string and then
        #   use this function recursively to handle the nodes contained within 
        #   the list
        #
        #   otherwise, add the draw_options and label information for the node 
        #   to the dot str.
        for entry in nodes:
            if isinstance(entry, list):
                dot += f'\n{indents}subgraph cluster_{entry[0].n_id} {{ \n'
                create_nodes_and_clusters(entry, indent_level+1)
                dot += f'\n{indents} }}\n'
            else:
                opts = []
                for opt in entry.draw_options:
                    if hex_pattern.match(entry.draw_options[opt]):
                        opts.append(f'{opt}=\"{entry.draw_options[opt]}\"')
                    else:
                        opts.append(f'{opt}={entry.draw_options[opt]}')
        
                opts.append(f'label=\"{entry.id_}\"')
                opts_str = ', '.join(opts)
                node_definition: str = f'{indents}{entry.n_id} [{opts_str}]\n'
                dot += node_definition

    create_nodes_and_clusters(graph_data)

    prev_entry = None
    edges = set()
    
    def create_main_edges(nested_structure: List):
        """
        Recursive function to add in all the edge information to the dot str

        The function needs to handle the special cases of indirectly connected 
        nodes. These are nodes that aren't connected in the pipeline, but are 
        intuitively connected in real-life. i.e. the last nodes in a nested node
        aren't directly connected to the child node(s) of the nested node in the
        pipeline.But it makes sense to have an edge between them to avoid having 
        a disjoint graph/an edge going from the nested node to the child node. 

        The standard case for this function though deals with regular nodes and
        simple adds an edge between them in the dot str.
        """
        nonlocal dot
        nonlocal edges
        nonlocal prev_entry
        for entry in nested_structure:
            if isinstance(entry, list):
                outer_to_nested_edge = (entry[0].n_id, entry[1].n_id)
                if isinstance(entry[-1], list):
                    nested_to_outer_edges = [(entry[-1][-1].n_id, outer.n_id) for outer in entry[0].children] 
                else:
                    nested_to_outer_edges = [(entry[-1].n_id, outer.n_id) for outer in entry[0].children]
                
                if outer_to_nested_edge not in edges:    
                    edges.add(outer_to_nested_edge)
                
                create_main_edges(entry)
                
                for edge in nested_to_outer_edges:
                    if edge not in edges:    
                        edges.add(edge)
            else:
                if graphutils.is_nested_node(entry): 
                    continue
                for child_node in entry.children:
                    new_edge = (entry.n_id, child_node.n_id)
                    if new_edge not in edges:
                        edges.add(new_edge)
                        
            prev_entry = entry
    create_main_edges(graph_data)

    last_node = ordering[-1]
    
    # Find first non-nested node after all nested components
    if any(isinstance(entry, list) for entry in graph_data):    
        for i in range(len(graph_data)-1, 0, -1):
            if isinstance(graph_data[i], list):
                first_out_of_final_subgraph = graph_data[i + 1] if i+1 < len(graph_data) else None
    # Create the edges for nested leaf nodes to the first node out of the nested components
    out_edges = [i[0] for i in edges]
    nodes_with_no_out_edge = [n for n in ordering if n.n_id not in out_edges and n != last_node and not graphutils.is_nested_node(n)]
    if first_out_of_final_subgraph:
        for node in nodes_with_no_out_edge:
            edges.add((node.n_id, first_out_of_final_subgraph.n_id))
    
    # Add all the edges
    for edge in edges:
        dot += f'{edge[0]}->{edge[1]}\n'
    
    dot += '}'
    return dot