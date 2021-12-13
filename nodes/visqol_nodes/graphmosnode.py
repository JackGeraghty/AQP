"""Module containing ViSQOL graphing node."""

import logging
import matplotlib.pyplot as plt
import numpy as np

from ..node import ViSQOLNode
from constants import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)
PLOT_TYPES = ['box', 'scatter']

class GraphMOSNode(ViSQOLNode):
    
    def __init__(self, id_: str, df_key: str, x_data_keys: list, y_data_key: str, 
                 plot_title: str, x_label: str,
                 y_label: str, plot_type: str='box',
                 draw_options: dict=None, **kwargs):
        super().__init__(id_, draw_options=draw_options, **kwargs)
        self.df_key = df_key
        self.x_data_keys = x_data_keys
        self.y_data_key = y_data_key
        if plot_type not in PLOT_TYPES:
            raise ValueError(f'plot_type must be one of {PLOT_TYPES}')
            plot_type = 'scatter'
        self.plot_type = plot_type
        self.plot_title = plot_title
        self.x_label = x_label
        self.y_label = y_label
        self.type_ = "GraphMOSNode"
        
    def execute(self, result: dict, **kwargs):
        super().execute(result, **kwargs)
        df = result[self.df_key]
        plt.grid(True)
        plt.title(self.plot_title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        
        y_data = df[self.y_data_key]
        x_data = [df[k] for k in self.x_data_keys]
        
        plt.xticks([i for i in np.arange(1.0, 5.5, 0.5)])
        plt.yticks([i for i in np.arange(1.0, 5.5, 0.5)])
        plt.xlim(1.0, 5.0)
        plt.ylim(1.0, 5.0)
        colours = ['r', 'g', 'b']
        if self.plot_type == 'scatter':
            for i in range(len(x_data)):
                legend_name = self.x_data_keys[i]
                colour = colours[i]
                plt.scatter(x_data[i], y_data, color=colour, label=legend_name)
                
            plt.legend()
            plt.show()
        return result
        