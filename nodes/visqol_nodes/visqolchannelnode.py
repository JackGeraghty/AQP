"""Module containing the ViSQOLChannelNode, responsible for extracting channel information during execution."""

import qualitymetrics.visqol.dsp as dsp
from ..node import ViSQOLNode

class ViSQOLChannelNode(ViSQOLNode):
    """Node used to extract channel information and perform initial visqol correction operations."""
    
    def __init__(self, id_: str, output_key: str=None,
                 reference_signal_key: str='reference_signal',
                 degraded_signal_key: str='degraded_signal', 
                 draw_options=None, **kwargs):
        """Initialize a ViSQOLChannelNode.
        
        Parameters
        ----------
        reference_signal_key : str, optional
            Key to retrieve and then reassign the extracted reference channel 
            to. The default is 'degraded_signal'.
        degraded_signal_key : str, optional
            Key to retrieve and then reassign the extracted degraded channel 
            to. The default is 'degraded_signal'.

        """
        super().__init__(id_, output_key, draw_options=draw_options)
        self.reference_signal_key = reference_signal_key
        self.degraded_signal_key = degraded_signal_key
        self.type_ = 'ViSQOLChannelNode'
        
    
    def execute(self, result: dict, **kwargs):
        """Execute the ViSQOLChannelNode."""
        super().execute(result)
        reference = dsp.extract_channel(result[self.reference_signal_key], result['iterator_item'])
        degraded = dsp.extract_channel(result[self.degraded_signal_key], result['iterator_item'])
        visqol_args = result['visqol_args']
        if visqol_args.arguments.compensate_for_padding:
            degraded = dsp.correct_for_initial_delay_codec_artifact(reference, degraded)
        if visqol_args.arguments.global_align:
            reference, degraded = dsp.global_align(reference, degraded)
        result[self.reference_signal_key] = reference
        result[self.degraded_signal_key] = degraded
        return result