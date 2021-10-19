import matplotlib.pyplot as plt
import matplotlib

from .node import AQPNode

class GraphNode(AQPNode):
    
    def __init__(self, id_: str, df_key: str, x_data_key: str, 
                 y_data_keys: list, titles: list, y_labels: list, **kwargs):
        super().__init__(id_)
        self.df_key = df_key
        self.x_data_key = x_data_key
        self.y_data_keys = y_data_keys
        self.titles = titles
        self.y_labels = y_labels
        self.type_ = "GraphNode"
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        df = result[self.df_key]
        x_data = df[self.x_data_key] # MOS
        colors = ['red', 'green', 'blue']
        plt.rcParams['axes.labelsize'] = 17
        matplotlib.rc('xtick', labelsize=15) 
        matplotlib.rc('ytick', labelsize=15) 
        fig, axs = plt.subplots(1, len(self.y_data_keys), sharey=False, sharex=True, figsize=(12, 12))
        if  len(self.y_data_keys) > 1:
            for i, key in enumerate(self.y_data_keys):
                axs[i].scatter(x_data, df[key], label=self.y_labels[i], color=colors[i])
                axs[i].set_title(self.titles[i], fontsize=17)
                axs[i].set(xlabel='MOS', ylabel=self.y_labels[i])
                axs[i].grid()
                axs[i].set_xlim([1, 5])
                axs[i].set_aspect(1./axs[i].get_data_ratio(), adjustable='box')
        else:
            axs.scatter(x_data, df[self.y_data_keys[0]], label=self.y_labels[0], color=colors[0])
            axs.set_title(self.titles[0], fontsize=17)
            axs.set(xlabel='MOS', ylabel=self.y_labels[0])
            axs.grid()
            axs.set_xlim([1, 5])
            axs.set_aspect(1./axs.get_data_ratio(), adjustable='box')

        plt.tight_layout()
        plt.show() 
        return result