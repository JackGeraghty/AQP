"""Module containing the ScaleSignalNode, which is used to scale two signal to have the same Sound Pressure Level."""
import math
import numpy as np
from .node import AQPNode

class ScaleSignalsNode(AQPNode):
    """Node used to scale two signals to the same Sound Pressure Level."""
    
    def __init__(self, id_: str,  
                 ref_sig_key: str='reference_signal', 
                 deg_sig_key: str='degraded_signal',
                 draw_options: dict=None, **kwargs):
        """Initialize a ScaleSignalsNode.

        Parameters
        ----------
        ref_sig_key : str, optional
            Key to retrieve the reference audio signal. The default is 'reference_signal'.
        deg_sig_key : str, optional
            Key to retrieve the degraded audio signal. The default is 'degraded_signal'.
        """
        super().__init__(id_, draw_options=draw_options)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.type_ = 'ScaleSignalNode'
    
    
    def execute(self, result: dict, **kwargs):
        """Execute the ScaleSignalNode and updates the degraded signal key with the scaled signal."""
        super().execute(result)
        required_reference_spl = ScaleSignalsNode._calculate_SPL(result[self.ref_sig_key])
        required_degraded_spl = ScaleSignalsNode._calculate_SPL(result[self.deg_sig_key])
        result[self.deg_sig_key] *= (10 ** ((required_reference_spl - required_degraded_spl) / 20))
        return result
    
    
    @classmethod
    def _calculate_SPL(cls, signal: np.ndarray) -> float:
        return 20 * math.log10(math.sqrt(np.mean(np.square(signal))) / 20e-6)