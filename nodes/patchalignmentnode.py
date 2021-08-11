from .node import ViSQOLNode
from qualitymetrics.visqol.constants import PATCH_SIZE
import qualitymetrics.visqol.dsp as dsp


class PatchAlignmentNode(ViSQOLNode):
    
    def __init__(self, id_, children, output_key=None, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.type_ = 'PatchAlignmentNode'
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        max_alignment_offset = PATCH_SIZE
        degraded_spect = result['degraded_spect']
        reference_patches = result['reference_patches']
        reference_patch_indexes = result['reference_patch_indexes']
        num_bands = result['visqol_args'].filterbank.num_bands
        L = result['L']
        speech = result['visqol_args'].arguments.speech
        warp = result['warps']
        
        if speech:
            patch_corr, degraded_patch_indexes = dsp.align_degraded_patches_nsim(degraded_spect, reference_patches, warp, num_bands, reference_patch_indexes, L, speech)
        else:
            if result['visqol_args'].arguments.use_patch_alignment:
                patch_corr, degraded_patch_indexes = dsp.align_degraded_patches_audio(degraded_spect, reference_patches, reference_patch_indexes, warp, num_bands, L, speech)
            else:
                degraded_patch_indexes = result['reference_patch_indexes'].copy()
                patch_corr = []
            max_alignment_offset = PATCH_SIZE
        for i in range(len(reference_patch_indexes)):
            if abs(reference_patch_indexes[i] - degraded_patch_indexes[i]) > max_alignment_offset:
                degraded_patch_indexes[i] = reference_patch_indexes[i]
        patch_deltas = [ref - deg for ref, deg in zip(reference_patch_indexes, degraded_patch_indexes)]
        result['degraded_patch_indexes'] = degraded_patch_indexes
        result['patch_corr'] = patch_corr
        result['patch_deltas'] = patch_deltas
        return result