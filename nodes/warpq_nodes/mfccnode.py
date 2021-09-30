import librosa, librosa.core, librosa.display
import speechpy
import numpy as np
from ..node import WarpQNode
from skimage.util.shape import view_as_windows

class MFCCNode(WarpQNode):
    
    def __init__(self, id_, ref_sig_key, deg_sig_key,
                 n_mfcc=12, fmax=5000, patch_size=0.4,
                 **kwargs):
        super().__init__(id_, **kwargs)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.n_mfcc = n_mfcc
        self.fmax = fmax
        self.patch_size = patch_size
        self.type_ = "MFCCNode"
    
    
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        sr = result['sr']
        win_length = int(0.032 * sr)
        hop_length = int(0.004 * sr)
        n_fft = 2 * win_length
        lifter = 3
        
        ref_sig = result[self.ref_sig_key]
        deg_sig = result[self.deg_sig_key]
        
        mfcc_ref = librosa.feature.mfcc(ref_sig,sr=sr,n_mfcc=self.n_mfcc,fmax=self.fmax,
                                    n_fft=n_fft,win_length=win_length,hop_length=hop_length,lifter=lifter)
        mfcc_coded = librosa.feature.mfcc(deg_sig,sr=sr,n_mfcc=self.n_mfcc,fmax=self.fmax,
                                    n_fft=n_fft,win_length=win_length,hop_length=hop_length,lifter=lifter)
        
        mfcc_ref = speechpy.processing.cmvnw(mfcc_ref.T,win_size=201,variance_normalization=True).T
        mfcc_coded = speechpy.processing.cmvnw(mfcc_coded.T,win_size=201,variance_normalization=True).T
        
        # Divid MFCC features of Coded speech into patches
        cols = int(self.patch_size/(hop_length/sr))
        window_shape = (np.size(mfcc_ref,0), cols)
        step  = int(cols/2)
        
        mfcc_Coded_patch = view_as_windows(mfcc_coded, window_shape, step)
        result['mfcc_coded_patch'] = mfcc_Coded_patch
        result['mfcc_ref'] = mfcc_ref
        result['mfcc_coded'] = mfcc_coded
        return result