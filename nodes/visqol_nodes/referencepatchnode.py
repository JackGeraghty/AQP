"""Module containing the ReferencePatchNode, which is responsible for creating the splitting the reference spectrogram into patches."""

import qualitymetrics.visqol.dsp as dsp
from ..node import ViSQOLNode


class ReferencePatchNode(ViSQOLNode):
    """Node encapsulate the logic of creating the patches of the reference spectrogram."""
    
    def __init__(self, id_: str, output_key: str='reference_patches', 
                 signal_key: str='reference_spect',
                 patch_indexes_key: str='reference_patch_indexes', 
                 draw_options: dict=None, **kwargs):
        """Initialize a ReferencePatchNode.

        Parameters
        ----------
        signal_key : str, optional
            Key used to look up the reference spectrogram.
            The default is 'reference_spect'.
        patch_indexes_key : str, optional
            Output key for the patch indexes. Node needs to output more than 
            one value to the result dict.The default is 
            'reference_patch_indexes'.
        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options, **kwargs)
        self.signal_key = signal_key        
        self.patch_indexes_key = patch_indexes_key
        self.type_ = 'ReferencePatchNode'
        
        
    def execute(self, result: dict, **kwargs):
        """Execute the node and create both the reference_patches and their corresponding indexes."""
        super().execute(result, **kwargs)
        sig_img = result[self.signal_key]
        warps = result['warps']
        speech = result['visqol_args'].arguments.speech
        compare_whole_signal = result['visqol_args'].arguments.compare_whole_signal
        result[self.output_key], result[self.patch_indexes_key] = dsp.create_reference_patches(sig_img, warps, speech, compare_whole_signal)
        return result
        