
import sys
from .node import Node
from pathlib import Path
import numpy as np

class AlignmentNode(Node):

    def __init__(self, id_, children, output_key='align_signals',
                 ref_sig_key='reference_signal', 
                 deg_sig_key='degraded_signal', **kwargs):
        super().__init__(id_, children, output_key)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.type_ = 'AlignSignalNode'

    def execute(self, result) -> dict:
        super().execute(result)
        ref_length = len(result[self.ref_sig_key])
        deg_length = len(result[self.deg_sig_key])
        if ref_length > deg_length:
            aligned_reference_signal, aligned_degraded_signal=np.array(result[self.ref_sig_key].tolist()[:deg_length]), result[self.deg_sig_key]
        elif deg_length > ref_length:
            aligned_reference_signal, aligned_degraded_signal=result[self.ref_sig_key], np.array(result[self.deg_sig_key].tolist()[:ref_length])
        else:
            aligned_reference_signal, aligned_degraded_signal=result[self.ref_sig_key], result[self.deg_sig_key]
        
        signals = {'aligned_reference_signal': aligned_reference_signal, 'aligned_degraded_signal': aligned_degraded_signal}
        result[self.output_key]=signals
        return result