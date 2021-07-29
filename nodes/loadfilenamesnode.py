import os
import pandas as pd
import librosa
from .node import Node
from pathlib import Path

class LoadFileNamesNode(Node):
    
    def __init__(self, id_, children, output_key, path_to: str, column_names: list=None, **kwargs):
        super().__init__(id_, children, output_key)
        self.path_to = Path(path_to)
        self.column_names = column_names
        self.type_ = 'LoadFileNamesNode'
    
    
    def execute(self, result):
        super().execute(result)
        if str(self.path_to).endswith('.csv') and self.column_names is not None :
            df = pd.read_csv(self.path_to)
            result[self.output_key] = list(list(df[col_name]) for col_name in self.column_names)
            return result
        if os.path.isdir(self.path_to):
            self.LOGGER.info('path_to points to a directory audio file')
            result[self.output_key] = list(os.path.join(self.path_to, file_name) for file_name in os.listdir(self.path_to) if file_name.endswith('.wav'))
            return result
        else:
            self.LOGGER.warn('path_to points to something that isn\'t a file or directory')
        return result