"""Module containing the PyPESQNode. Calculates the PESQ metric for the audio signals given."""

from ..node import PESQNode
from pesq import pesq

class PyPESQNode(PESQNode):
    """Node containing the logic for running the PESQ quality metric on a reference and test signal."""
    
    def __init__(self, id_: str, output_key: str='py_pesq_score',
                 ref_signal_key: str='aligned_ref_signal', 
                 deg_signal_key: str='aligned_deg_signal',
                 target_sample_rate: int=16000, pesq_mode:str='wb', 
                 draw_options: dict=None, **kwargs):
        """Initialize a PyPESQNode.

        Parameters
        ----------
        signal_key : str, optional
            Key used to loopup the . The default is 'align_signals'.
        target_sample_rate : int, optional
            DESCRIPTION. The default is 48000.
        pesq_mode : str, optional
            DESCRIPTION. The default is 'wb'.

        Returns
        -------
        None.

        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options, **kwargs)
        self.sample_rate = target_sample_rate
        self.ref_signal_key = ref_signal_key
        self.deg_signal_key = deg_signal_key
        self.pesq_mode = pesq_mode
        self.type_ = 'PypesqNode'
    
    
    def execute(self, result: dict, **kwargs):
        """Execute the node and calculate the PESQ score for input signals."""
        super().execute(result, **kwargs)
        ref_sig = result[self.ref_signal_key]
        deg_sig = result[self.deg_signal_key]
        sim_score = pesq(self.sample_rate, ref_sig, deg_sig, self.pesq_mode)
        result[self.output_key] = sim_score
        return result