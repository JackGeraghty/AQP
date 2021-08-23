import os
import pandas as pd
import librosa
import logging
from .node import AQPNode
from pathlib import Path

LOGGER = logging.getLogger('pipeline')

class LoadFileNamesNode(AQPNode):
    
    def __init__(self, id_, children, output_key, path_to: str, 
                 column_names: list=None, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.path_to = Path(path_to)
        self.column_names = column_names
        self.type_ = 'LoadFileNamesNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        if str(self.path_to).endswith('.csv') and self.column_names is not None:
            df = pd.read_csv(self.path_to, dtype=str)
            result[self.output_key] = list(df[df[col_name].str.endswith('.wav')][col_name] for col_name in self.column_names)
            return result
        if os.path.isdir(self.path_to):
            LOGGER.info('path_to points to a directory audio file')
            result[self.output_key] = list(os.path.join(self.path_to, file_name) for file_name in os.listdir(self.path_to) if file_name.endswith('.wav'))
            return result
        else:
            LOGGER.warn('path_to points to something that isn\'t a file or directory')
        return result