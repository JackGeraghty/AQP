import re
from nodes.node import Node
from nodes.loopnode import LoopNode
from nodes.encapsulationnode import EncapsulationNode
from typing import List, Tuple


def build_visualization(ordering_: List[Tuple[str, Node]]):
    ordering = list(ordering_)
       
    
    # is r_two within r_one
    # start indexes cannot be the same but can have the same end index
    def within_range(r_one, r_two):
        return  r_two[1] <= r_one[1] and r_two[0] > r_one[0]
    
    info = {}
    prev = None

    for i in range(len(ordering_)):
        current = ordering_[i]

        if isinstance(current, (LoopNode, EncapsulationNode)):
            # Need to maintain a reference to the previous node
            # This required to handle the case of a nested Loop/Encapsulation Node
            # which doesn't have any children
            next_node = current.children[0] if current.children else prev.children[0]
            
            for j in  range(i, len(ordering_)):
                if ordering[j].n_id == next_node.n_id:
                    print(f'Found the next node {j - i} places on from the current node')
                    break
            info[(i, j)] = [x.id_ for x in ordering[i:j]]
            prev = current

    seen_ranges = {}            
    indexes = [x for x in info]
    for i in range(len(indexes)-1, -1, -1):
        index_range = indexes[i]
        nodes_in_range = info[index_range]
        contained_ranges = [k for k in seen_ranges if within_range(index_range, k)]
        if len(contained_ranges) == 0 and index_range not in seen_ranges:
            seen_ranges[index_range] = nodes_in_range
        else:
            current_entry = contained_ranges[-1]
            
            current_start_index = index_range[0]
            amount_to_prepend =  current_entry[0] - current_start_index
            new_entry = []
            
            for j in range(current_start_index, current_start_index + amount_to_prepend):
                new_entry.append(ordering[j].id_)
            contained_ranges.reverse()
            for r in contained_ranges:
                new_entry.append(seen_ranges[r])
                seen_ranges.pop(r, None)
            seen_ranges[index_range] = new_entry
   
    final_range = list(seen_ranges.keys())[0]
    final_nested_structure = []
    for i in range(final_range[0]):
        final_nested_structure.append(ordering_[i].id_)

    final_nested_structure.append(seen_ranges[final_range])
    
    for i in range(final_range[1], len(ordering_)):
        final_nested_structure.append(ordering_[i].id_)
        
    def recur_print(nested_list, indent_level=0):
        for x in nested_list:
            
            if isinstance(x, list):
                print("INDENTING")
                indent_level += 1
                recur_print(x, indent_level)
                indent_level -= 1
                
            else:
                tab_str = indent_level * '\t'
                print(f'{tab_str}{x}')
    recur_print(final_nested_structure)
    print(final_nested_structure)
    return final_nested_structure

# Generates a dot file from the nested structure created in build_visualization
def generate_dot_file(ordering: List[Node], graph_data: List[Node]):
    
    hex_str = '^#(?:[0-9a-fA-F]{3}){1,2}$'
    hex_pattern = re.compile(hex_str)
        
    dot = 'digraph {'
    for node in ordering:
        opts = []
        for opt in node.draw_options:
            if hex_pattern.match(node.draw_options[opt]):
                opts.append(f'{opt}=\"{node.draw_options[opt]}\"')
            else:
                opts.append(f'{opt}={node.draw_options[opt]}')

        opts.append(f'label={node.id_}')
        opts_str = ', '.join(opts)
        node_definition: str = f'{node.n_id} [{opts_str}]\n'
        dot += node_definition
        
        
    ## TODO: Look into how to use graph info to fix missing edges
    for node in ordering:
            
        for child_node in node.children:
            dot += f'{node.n_id}->{child_node.n_id};\n'
            

    dot += '}'
    return dot