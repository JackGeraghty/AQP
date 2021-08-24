import qualitymetrics.visqol.constants as constants
import qualitymetrics.visqol.dsp as dsp
import numpy as np
from ..node import ViSQOLNode


class PatchSimilarityNode(ViSQOLNode):
    
    def __init__(self, id_, children, output_key=None, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.type_ = 'PatchSimilarityNode'
        
    
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        freq_band_sim = constants.FREQ_BAND_SIM_FUNCTIONS[result['visqol_args'].arguments.freq_band_sim_per_patch]
        reference_patches = result['reference_patches']
        reference_patch_indexes = result['reference_patch_indexes']
        reference_spect = result['reference_spect']
        
        degraded_patch_indexes = result['degraded_patch_indexes']
        degraded_spect = result['degraded_spect']
        warp = result['warps']
        L = result['L']
        speech = result['visqol_args'].arguments.speech
        
        
        degraded_patches = dsp.create_degraded_patches(degraded_patch_indexes, degraded_spect, reference_patches, constants.PATCH_SIZE, warp)
        
        # TODO
        # if result['visqol_args'].arguments.global_comparison:
            
        mean_warp_patch_nsims, similarity_maps = dsp.calc_ref_deg_similarity(reference_patches, degraded_patches, warp, L, result['visqol_args'].arguments.similarity_measure);  
        
        num_patches = reference_patches.shape[0]
        patch_nsims = dsp.extract_best_nsim_per_patch(mean_warp_patch_nsims, num_patches)
        patch_freq_band_per_patch_similarities = dsp.calc_patch_freq_band_similarities(similarity_maps, freq_band_sim)
        # The FVNSIM is the similarity measure across frequency bands.
        fvnsim = np.empty((len(patch_freq_band_per_patch_similarities), 1))
        fvnsim[:] = np.nan
        fn = constants.FREQ_BAND_SIM_FUNCTIONS[result['visqol_args'].arguments.freq_band_sim_aggregate]
        for i in range(len(patch_freq_band_per_patch_similarities)):
            fvnsim[i] = fn(patch_freq_band_per_patch_similarities[i,:])
    
        # Calculate vnsim.
        # If the signal is low pass filtered, penalize the vnsim score by replacing
        # all of the near 1 scores for those bands with just a single 1. VNSIM is
        # then the mean of these.
    
        if dsp.is_low_pass_filtered(fvnsim):
            patch_freq_band_mean_similarity = fvnsim(fvnsim < 0.995)
            patch_freq_band_mean_similarity = [1, patch_freq_band_mean_similarity]
            vnsim = np.mean(patch_freq_band_mean_similarity)
        else:
            vnsim = np.mean(patch_nsims) if speech else np.mean(fvnsim)
    
        if not speech:
            patch_corr = np.zeros([reference_spect.shape[1], reference_patch_indexes.shape[0]])
            for i in range(len(reference_patch_indexes)):
                patch_corr[reference_patch_indexes[i]] = patch_nsims[i]
    
        sim_spect = []
        for i in range(len(similarity_maps)):
            sim_spect.append(similarity_maps[i])
        result['vnsim'] = vnsim
        return result