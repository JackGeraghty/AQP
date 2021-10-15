import numpy as np
import librosa
from ..node import WarpQNode


class WarpQSDTWNode(WarpQNode):
    
    def __init__(self, id_, output_key, mfcc_ref_key,
                 mfcc_coded_patch_key, sigma=np.array([[1,1],[3,2],[1,3]]), **kwargs):
        super().__init__(id_, output_key=output_key, **kwargs)
        self.mfcc_ref_key = mfcc_ref_key
        self.mfcc_coded_patch_key = mfcc_coded_patch_key
        self.sigma = sigma
        self.type_ = 'WarpQSDTWNode'
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        acc = []
        band_rad = 0.25
        weights_mul = np.array([1,1,1])
        mfcc_ref = result[self.mfcc_ref_key]
        mfcc_coded_patch = result[self.mfcc_coded_patch_key]
        for i in range(mfcc_coded_patch.shape[1]):
            patch = mfcc_coded_patch[0][i]
            D, P = librosa.sequence.dtw(X=patch, Y=mfcc_ref, metric='euclidean', 
                                        step_sizes_sigma=self.sigma, weights_mul=weights_mul, band_rad=band_rad, subseq=True, backtrack=True)
            P_librosa = P[::-1,:]
            b_ast = P_librosa[-1, 1]
            acc.append(D[-1, b_ast]/D.shape[0])
        
        result[self.output_key] = np.median(acc)
        return result