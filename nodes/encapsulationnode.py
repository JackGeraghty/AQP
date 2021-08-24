import json
import logging
import sys
from .node import AQPNode, deserialize
from pathlib import Path

LOGGER = logging.getLogger('pipeline')

class EncapsulationNode(AQPNode):
    
    def __init__(self, id_, children, 
                 path_to_node_config, output_key,blacklist=None,
                 draw_options=None, **kwargs):
        super().__init__(id_, children, output_key=output_key, draw_options=draw_options)
        try:
            with open(Path(path_to_node_config), 'rb') as data:
                self.node = deserialize(json.load(data))
        except (FileNotFoundError) as err:
            LOGGER.warn("%s", err)
            sys.exit(-1)
            
        if blacklist is None:
            blacklist = []
        
        self.blacklist = blacklist
        self.type_ = 'EncapsulationNode'
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        ## Not really happy with this, but for now it works. Lots of work 
        ## needed to clean up what information is passed down the graph. 
        ## Currently a decent bit of duplication
        r = {k: result[k] for k in result.keys() if k not in self.blacklist}
        result[self.output_key] = self.node.execute(r, **kwargs)
        return result