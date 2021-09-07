"""Module containing the LoadCSVAsDFNode. Used to load a csv file into a dataframe."""

import sys
import logging
import pandas as pd

from pathlib import Path
from .node import AQPNode
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class LoadCSVAsDFNode(AQPNode):
    """Node which takes a path to a csv file and store the csv as a pandas dataframe in the result dictionary upon execution."""

    def __init__(self, id_: str, output_key: str, path_to_csv: str,
                 draw_options=None, **kwargs):
        """Initialize a LoadCSVAsDF Node.

        Parameters
        ----------
        path_to_csv : str
            Path to the csv file to load.
        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options)
        self.path_to_csv = Path(path_to_csv)
        self.type_ = 'LoadCSVAsDFNode'

    def execute(self, result: dict, **kwargs):
        """Execute the LoadCSVAsDFNode.
        
        Assigns the loaded dataframe to the output key of the node.
        """
        super().execute(result, **kwargs)
        try:
            result[self.output_key] = pd.read_csv(self.path_to_csv)
        except (FileNotFoundError) as err:
            LOGGER.error(err)
            sys.exit(-1)
        return result
