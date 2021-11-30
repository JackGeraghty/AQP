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
            info[(i, j)] = [x for x in ordering[i:j]]
            print((i,j))
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
                new_entry.append(ordering[j])
            contained_ranges.reverse()
            for r in contained_ranges:
                new_entry.append(seen_ranges[r])
                seen_ranges.pop(r, None)
            
            for j in range(current_entry[1], index_range[1]):
                
                def check_membership(id_, nested_structure):
                    for n in nested_structure:
                        if isinstance(n, list):
                           if check_membership(id_, n):
                                return True
                        elif n.n_id == id_:
                            return True
                    return False
                            
                
                if not check_membership(ordering[j].n_id, new_entry):
                    new_entry.append(ordering[j])
                
            seen_ranges[index_range] = new_entry
   
    final_range = list(seen_ranges.keys())[0]
    final_nested_structure = []
    for i in range(final_range[0]):
        final_nested_structure.append(ordering_[i])

    final_nested_structure.append(seen_ranges[final_range])
    
    for i in range(final_range[1], len(ordering_)):
        final_nested_structure.append(ordering_[i])
        
    def recur_print(nested_list, indent_level=0):
        for x in nested_list:
            
            if isinstance(x, list):
                print("INDENTING")
                indent_level += 1
                recur_print(x, indent_level)
                indent_level -= 1
                
            else:
                tab_str = indent_level * '\t'
                print(f'{tab_str}{x.id_}')
    recur_print(final_nested_structure)
    print(final_nested_structure)
    return final_nested_structure

# Generates a dot file from the nested structure created in build_visualization
def generate_dot_file(ordering: List[Node], graph_data: List[Node]):
    
    hex_str = '^#(?:[0-9a-fA-F]{3}){1,2}$'
    hex_pattern = re.compile(hex_str)
    dot = 'digraph {\n'

    def fn (nodes, indent_level=0):
        nonlocal dot
        indents = indent_level * '\t'

        for entry in nodes:
            if isinstance(entry, list):
                dot += f'\n{indents}subgraph cluster_{entry[0].n_id} {{\n label="{entry[0].id_}" \n'
                fn(entry, indent_level+1)
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
        return dot
    fn(graph_data)
    ## TODO: Look into how to use graph info to fix missing edges
    prev_entry = None
    edges = set()
    
    def add_edges(nested_structure):
        nonlocal dot
        nonlocal edges
        nonlocal prev_entry
        for entry in nested_structure:
            if isinstance(entry, list):
                # add edge from prev_entry to entry[0]
                outer_to_nested_edge = (entry[0].n_id, entry[1].n_id)
                if isinstance(entry[-1], list):
                    nested_to_outer_edges = [(entry[-1][-1].n_id, outer.n_id) for outer in entry[0].children] 
                else:
                    nested_to_outer_edges = [(entry[-1].n_id, outer.n_id) for outer in entry[0].children]
                
                if outer_to_nested_edge not in edges:    
                    dot += f'{outer_to_nested_edge[0]}->{outer_to_nested_edge[1]}\n'
                    edges.add(outer_to_nested_edge)
                
                add_edges(entry)
                
                for edge in nested_to_outer_edges:
                    if edge not in edges:    
                        dot += f'{edge[0]}->{edge[1]}\n'
                        edges.add(edge)

            else:
                if isinstance(entry, (LoopNode, EncapsulationNode)): 
                    continue
                for child_node in entry.children:
                    new_edge = (entry.n_id, child_node.n_id)
                    if new_edge not in edges:
                        dot += f'{new_edge[0]}->{new_edge[1]}\n'
                        edges.add(new_edge)
                        
            prev_entry = entry
    add_edges(graph_data)
    last_node = ordering[-1]
    if any(isinstance(x, list) for x in graph_data):    
        for i in range(len(graph_data)-1, 0, -1):
            if isinstance(graph_data[i], list):
                first_out_of_final_subgraph = graph_data[i + 1] if i+1 < len(graph_data) else None
       
    out_edges = [i[0] for i in edges]
    nodes_with_no_out_edge = [n for n in ordering if n.n_id not in out_edges and n != last_node]
    if first_out_of_final_subgraph:
        for node in nodes_with_no_out_edge:
            dot += f'{node.n_id}->{first_out_of_final_subgraph.n_id}\n'
    dot += '}'
    return dot