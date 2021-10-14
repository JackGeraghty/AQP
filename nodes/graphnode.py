import matplotlib.pyplot as plt
import matplotlib

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
        colors = ['red', 'green', 'blue']
        metric_names = ['WARP-Q Mel', 'WARP-Q MFCC', 'PESQ']
        ylabel = ['WARP-Q Distance', 'WARP-Q Distance', 'Predicted MOS']
        plt.rcParams['axes.labelsize'] = 17
        matplotlib.rc('xtick', labelsize=15) 
        matplotlib.rc('ytick', labelsize=15) 
        fig, axs = plt.subplots(1, 3, sharey=False, sharex=True, figsize=(12, 12))
        for i, key in enumerate(self.x_data_keys):
            axs[i].scatter(y_data, df[key], label=self.labels[i], color=colors[i])
            axs[i].set_title(metric_names[i], fontsize=17)
            axs[i].set(xlabel='MOS', ylabel=ylabel[i])
            axs[i].grid()
            axs[i].set_xlim([1, 5])
            axs[i].set_aspect(1./axs[i].get_data_ratio(), adjustable='box')
        
        plt.tight_layout()
        plt.show() 
        return result