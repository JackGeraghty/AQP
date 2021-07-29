import networkx as nx
from .node import Node, deserialize
from .loopnode import LoopNode


class GraphNode(Node):
    
    def __init__(self, id_, children, subgraph, sub_root_id, **kwargs):
        super().__init__(id_, children)
        self.graph = build_graph(subgraph)
        self.sub_root_id = sub_root_id
        self.traversal_order = build_traversal_dfs(self.graph, [], self.sub_root_id)
        self.type_ = "GraphNode"
        
        
    def execute(self, result, **kwargs):
        super().execute(result)
        for n_id in self.traversal_order:
            result = self.graph.nodes[n_id]['data'].execute(result, **kwargs)     
        return result
    
    
def build_traversal_dfs(graph: nx.DiGraph, traversal_list, node):
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
    
    
def build_graph(graph_definition: dict):
    edges = []
    graph = nx.DiGraph()
    for node in graph_definition:
        graph_definition[node]['id_'] = node
        adjacent_nodes = graph_definition[node]['children']
        
        graph.add_node(node, data=deserialize(graph_definition[node]))
        if len(adjacent_nodes) > 0:
            edges.extend([(node, other_id) for other_id in adjacent_nodes])
    graph.add_edges_from(edges)
    return graph


def build_expanded_traversal(graph,traversal_list, root):
    traversal_list.append(root)
    current_node = graph.nodes[root]

    if isinstance(current_node['data'], LoopNode) and isinstance(current_node['data'].execution_node, GraphNode):
        graph_node = current_node['data'].execution_node
        build_expanded_traversal(graph_node.graph, traversal_list, graph_node.sub_root_id)

    if isinstance(current_node['data'], GraphNode):
        build_expanded_traversal(current_node['data'].graph, traversal_list, current_node['data'].sub_root_id)
        
    children = current_node['data'].children
    for n_id in children:
        build_expanded_traversal(graph, traversal_list, n_id)
        
    return traversal_list