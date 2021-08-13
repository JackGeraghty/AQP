
import sys
from .node import Node
from pathlib import Path
from pesq import pesq

class PypesqNode(Node):

    def __init__(self, id_, children, output_key='py_pesq_score',
                    signal_key='align_signals', target_sample_rate: int=48000,
                      pesq_mode:str='wb', **kwargs):
        super().__init__(id_, children, output_key)
        self.sample_rate = target_sample_rate
        self.signal_key = signal_key
        self.pesq_mode = pesq_mode
        self.type_ = 'PypesqNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        signal = result[self.signal_key]
        ref_sig = signal['aligned_reference_signal']
        deg_sig = signal['aligned_degraded_signal']
        sim_score = pesq(self.sample_rate, ref_sig, deg_sig, self.pesq_mode)
        result[self.output_key] = sim_score
        return result