import networkx as nx
from .node import AQPNode, deserialize
from .loopnode import LoopNode

class GraphNode(AQPNode):
    
    def __init__(self, id_, children, subgraph, sub_root_id, draw_options=None, **kwargs):
        super().__init__(id_, children, draw_options=draw_options)
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
        node_ = deserialize(graph_definition[node])
        graph.add_node(node, data=node_)
    
        if len(adjacent_nodes) > 0:
            edges.extend([(node, other_id) for other_id in adjacent_nodes])
    graph.add_edges_from(edges)
    return graph


def expand_graph(graph, node, expanded_graph=nx.DiGraph(), edge_list=[]):
    current_node = graph.nodes[node]
    
    expanded_graph.add_node(node, data=current_node['data'])
    edge_list.extend( [e for e in graph.out_edges(node)])
    
    if isinstance(current_node['data'], LoopNode) and isinstance(current_node['data'].execution_node, GraphNode):
        edges_to_rework = [ e for e in graph.out_edges(node)]
        
        graph_node = current_node['data'].execution_node
        
        for i in range(len(edges_to_rework)): 
            edge_list.pop()
        
        # Add an edge between the loop node and the first node of the subgraph
        edge_list.append((node, graph_node.sub_root_id))
        expand_graph(graph_node.graph, graph_node.sub_root_id, expanded_graph)

        # Create an edge between the last node of the subgraph and the children
        # of the loop node
        last_loop_node = edge_list[-1][1]
        for edge in edges_to_rework:
            edge_list.append((last_loop_node, edge[1]))
            
    if isinstance(current_node['data'], GraphNode):
        expand_graph(current_node['data'].graph, current_node['data'].sub_root_id, expanded_graph)
    
    for child_node in current_node['data'].children:
        expand_graph(graph, child_node, expanded_graph)
    
    expanded_graph.add_edges_from(edge_list)
    return expanded_graph