import pyvad
import numpy as np
from .node import ViSQOLNode
from qualitymetrics.visqol.constants import PATCH_SIZE

class VADNode(ViSQOLNode):
    
    def __init__(self, id_, children, output_key=None, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.type_ = 'VADNode'
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        if result['visqol_args'].arguments.speech:
            reference_signal = result['reference_signal']
            reference_patches = result['reference_patches']
            reference_patch_indexes = result['reference_patch_indexes']
            sample_rate = result['visqol_args'].analysis_window.sample_rate
            
            voice_activity = pyvad.vad(reference_signal, sample_rate, fs_vad=sample_rate, hop_length=PATCH_SIZE, vad_mode=3)
            keep_indexes = np.array([np.sum(voice_activity[reference_patch_indexes[i] : reference_patch_indexes[i] + PATCH_SIZE - 1]) < PATCH_SIZE * 0.8 for i in range(len(reference_patch_indexes))])
            result['reference_patches'] = reference_patches[keep_indexes]
            result['reference_patch_indexes'] = reference_patch_indexes[keep_indexes]
        return result