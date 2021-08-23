import numpy as np
from .node import ViSQOLNode


class FloorSpectrogramsNode(ViSQOLNode):
    
    def __init__(self, id_: int, children: list, output_key: str=None,
                 reference_signal_key: str = 'reference_signal',
                 degraded_signal_key: str='degraded_signal', 
                 reference_spect_key: str='reference_spect',
                 degraded_spect_key: str='degraded_spect', 
                 arguments_key: str='visqol_args', 
                 draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.reference_signal_key = reference_signal_key
        self.degraded_signal_key = degraded_signal_key
        self.reference_spect_key = reference_spect_key
        self.degraded_spect_key = degraded_spect_key
        self.arguments_key = arguments_key
        self.type_ = 'FloorSpectrogramsNode'
        
    def execute(self, result, **kwargs):
        super().execute(result)
        if result[self.arguments_key].arguments.floor_spectrograms:
            reference_spect = result[self.reference_spect_key]
            degraded_spect = result[self.degraded_spect_key]
            ref_floor = np.min(reference_spect)
            deg_floor = np.min(degraded_spect)
            visqol_args = result[self.arguments_key]
            
            low_floor = ref_floor if visqol_args.arguments.speech else min(ref_floor, deg_floor)
            result[self.reference_spect_key] -= low_floor
            result[self.degraded_spect_key] -= low_floor
        return result
        
        
        
        