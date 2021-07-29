import numpy as np
from .node import Node

class FloorSpectrogramsNode(Node):
    
    def __init__(self, id_: int, children: list, output_key: str,
                 reference_signal_key: str, degraded_signal_key: str, 
                 reference_spect_key: str, degraded_spect_key: str, 
                 arguments_key: str, **kwargs):
        super().__init__(id_, children, output_key)
        self.reference_signal_key = reference_signal_key
        self.degraded_signal_key = degraded_signal_key
        self.reference_spect_key = reference_spect_key
        self.degraded_spect_ley = degraded_spect_key
        self.arguments_key = arguments_key
        
        
    def execute(self, result):
        super().execute(result)
        reference_signal = result[self.reference_signal_key]
        degraded_signal = result[self.degraded_signal_key]
        ref_floor = np.min(reference_signal)
        deg_floor = np.min(degraded_signal)
        visqol_args = result[self.arguments_key]
        
        low_floor = ref_floor if visqol_args.arguments['speech'] else min(ref_floor, deg_floor)
        result[self.reference_spect_key] -= low_floor
        result[self.degraded_spect_key] -= low_floor
        return result
        
        
        
        