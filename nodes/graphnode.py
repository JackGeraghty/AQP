import matplotlib.pyplot as plt

from .node import AQPNode

class GraphNode(AQPNode):
    
    def __init__(self, id_, df_key, x_data_keys, y_data_key, labels, **kwargs):
        super().__init__(id_)
        self.df_key = df_key
        self.x_data_keys = x_data_keys
        self.y_data_key = y_data_key
        self.labels = labels
        self.type_ = "GraphNode"
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        df = result[self.df_key]
        y_data = df[self.y_data_key]
        i = 0
        plt.xlabel('MOS')
        plt.ylabel('Predicted MOS')
        for key in self.x_data_keys:
            plt.scatter(y_data, df[key], label=self.labels[i])
            i += 1
        plt.legend()
        plt.show()
        return result