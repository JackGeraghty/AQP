from .node import Node
from nodes.graphnode import GraphNode

class ComparisonNode(Node):
    
    def __init__(self, id_: int, children: list, output_key: str,
                 node_data: dict, dataset_one_key: str, dataset_two_key: str,**kwargs):
        super().__init__(id_, children, output_key)
        self.execution_node = GraphNode(**node_data)
        self.dataset_one_key = dataset_one_key
        self.dataset_two_key = dataset_two_key
        self.type_ = 'ComparisonNode'
        

    def execute(self, result):
        '''
        Loop over corresponding entries in the two datasets. For each entry
        extract a value from each dataset using the keys provided to this node.
        
        Use the two extracted values as the input to the sub-graph. The result 
        of the sub-graph is then inserted into a temporary dictionary using
        a key built based on the current entry.
        
        Finally assign this temporary dictionary to the global results dictionary
        and continue

        Parameters
        ----------
        result : TYPE
            DESCRIPTION.

        Returns
        -------
        result : TYPE
            DESCRIPTION.

        '''
        super().execute(result)
        dataset_one = result[self.dataset_one_key]
        dataset_two = result[self.dataset_two_key]
        results = {}
        for ref, deg in zip(dataset_one, dataset_two):
            print("See this twice")
            res = {self.dataset_one_key: ref, self.dataset_two_key: deg}
            graph_result = self.execution_node.execute(res)
            results_key = ref + '__' + deg
            results[results_key] = graph_result
        result[self.output_key] = results
        return result
            
            
        