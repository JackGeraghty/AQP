import math
import numpy as np
from .node import ViSQOLNode


class ScaleSignalsNode(ViSQOLNode):
    
    def __init__(self, id_, children,  
                 ref_sig_key='reference_signal', 
                 deg_sig_key='degraded_signal',
                 draw_options=None, **kwargs):
        super().__init__(id_, children, draw_options=draw_options)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.type_ = 'ScaleSignalNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        required_reference_spl = ScaleSignalsNode.calculate_SPL(result[self.ref_sig_key])
        required_degraded_spl = ScaleSignalsNode.calculate_SPL(result[self.deg_sig_key])
        result[self.deg_sig_key] *= (10 ** ((required_reference_spl - required_degraded_spl) / 20))
        return result
    
    
    @classmethod
    def calculate_SPL(cls, signal: np.ndarray) -> float:
        return 20 * math.log10(math.sqrt(np.mean(np.square(signal))) / 20e-6)