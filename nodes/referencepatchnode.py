from .node import Node
import qualitymetrics.visqol.dsp as dsp

class ReferencePatchNode(Node):
    
    def __init__(self, id_, children, output_key='reference_patches', signal_key='reference_spect',
                 patch_indexes_key='reference_patch_indexes',**kwargs):
        super().__init__(id_, children, output_key)
        self.signal_key = signal_key        
        self.patch_indexes_key = patch_indexes_key
        self.type_ = 'ReferencePatchNode'
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        sig_img = result[self.signal_key]
        warps = result['warps']
        speech = result['visqol_args'].arguments.speech
        compare_whole_signal = result['visqol_args'].arguments.compare_whole_signal
        result[self.output_key], result[self.patch_indexes_key] = dsp.create_reference_patches(sig_img, warps, speech, compare_whole_signal)
        return result
        