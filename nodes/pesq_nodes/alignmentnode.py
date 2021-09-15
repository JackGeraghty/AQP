"""Module containing the AlignemntNode, responsible for ViSQOL alignment of reference + degraded patches."""

from ..node import PESQNode
import numpy as np

class AlignmentNode(PESQNode):
    """The AlignmentNode is used to perform patch alignment of the reference and degraded signal patches."""
    
    def __init__(self, id_: str, output_key: str='align_signals',
                 ref_sig_key: str='reference_signal', 
                 deg_sig_key: str='degraded_signal', draw_options: dict=None, **kwargs):
        """Initialize an AlignmentNode.
        
        Parameters
        ----------
        ref_sig_key : str, optional
            Key used to lookup the reference signal in the results dict.
            The default is 'reference_signal'.
        deg_sig_key : str, optional
            Key used to lookup the degraded signal in the results dict.
            The default is 'degraded_signal'.
        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options, **kwargs)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.type_ = 'AlignSignalNode'

    def execute(self, result: dict, **kwargs) -> dict:
        """Execute the alignment node.
        
        Aligns the two signals based on the which signal is longer.
        """
        super().execute(result)
        ref_length = len(result[self.ref_sig_key])
        deg_length = len(result[self.deg_sig_key])
        if ref_length > deg_length:
            aligned_reference_signal, aligned_degraded_signal=np.array(result[self.ref_sig_key].tolist()[:deg_length]), result[self.deg_sig_key]
        elif deg_length > ref_length:
            aligned_reference_signal, aligned_degraded_signal=result[self.ref_sig_key], np.array(result[self.deg_sig_key].tolist()[:ref_length])
        else:
            aligned_reference_signal, aligned_degraded_signal=result[self.ref_sig_key], result[self.deg_sig_key]
        
        result['aligned_ref_signal'] = aligned_reference_signal
        result['aligned_deg_signal'] = aligned_degraded_signal
        return result