"""Module containing functionality relating to any processing of a signal throughout ViSQOL"""

import numpy as np
import logging
import math
from typing import Callable, Tuple
from .nsim import nsim_map
from scipy.interpolate import RectBivariateSpline
from scipy.signal import hilbert, correlate, correlation_lags
PATCH_SIZE = 30

LOGGER = logging.getLogger('pipeline')

def calculate_SPL(signal: np.ndarray) -> float:
    return 20 * math.log10(math.sqrt(np.mean(np.square(signal))) / 20e-6)


def extract_channel(signal: np.ndarray, channel: str) -> np.ndarray:
    """ 
        Used to extract information relating to specific channels present in 
        the input signal

        parameters
        ----------
        signal: numpy.ndarray
            Input signal to extract channel information from
        channel: str
            The channel to try and extract

        returns
        -------
        signal: nump.ndarray
            Subset of the origal signal data, containing only the data 
            relating to the specified channel
    """
    if signal.ndim == 1:
        return signal
    
    if channel == 'left':
        return signal[0,:]
    elif channel == 'right':
        return signal[1,:]
    elif channel == 'mid':
        return (signal[0,:] + signal[1,:]) / 2
    elif channel == 'side':
        return (signal[0,:] - signal[1,:]) / 2


def upper_envelope(signal: np.ndarray) -> np.ndarray:
    """
        Calculates an upper envelope of the input signal using it'
        analytic_signal which is calculated 
        using the Hilbert transform

        Parameters
        ----------
        signal: numpy.ndarray
            input signal from wavfile

        Returns
        -------
        out: numpy.ndarray
            Upper envelope of the input signal
    """
    return np.abs(hilbert(signal))


def xcorr(signal_one: np.ndarray, signal_two: np.ndarray, 
          mode:str = 'full') -> Tuple[np.array, np.array]:
    """
        Performs a cross-correlation between the two input signals.Tries to 
        mimic the MATLAB xcorr function.

        Parameters
        ----------
        signal_one: numpy.ndarray
            The first input signal
        signal_two: numpy.ndarray
            The second input signal
        mode: str, optional
            The mode to use when performing the cross-correlation, default=full

        Returns
        -------
        correlate: numpy.array
            An N-dimensional array containing a subset of the discrete 
            cross-correlation between signal_one and signal_two
        lags: numpy.array
            An N-dimensional array containing the cross-correlation
            lag/displacement indices
    """
    return correlate(signal_one, signal_two, mode),\
            correlation_lags(len(signal_one), len(signal_two), mode)


def calculate_best_lag(reference_signal: np.ndarray, 
                       degraded_signal: np.ndarray) -> int:
    """
        Calculates the best lag parameter to use when correct for delays in
        the degraded signal and performing the global alignment

        Parameters
        ----------
        reference_signal: numpy.ndarray
            reference signal being used, should be a 1D array when being passed
        degraded_signal: numpy.ndarray
            degraded signal being used, should be a 1D array when being passed

        Returns
        -------
        best_lag: int
            TODO, what exactly this is
    """
    reference_upper_envelope = upper_envelope(reference_signal)
    degraded_upper_envelope = upper_envelope(degraded_signal)
    corrs, lags = xcorr(reference_upper_envelope, degraded_upper_envelope)
    max_index = np.argmax(np.abs(corrs))
    LOGGER.debug('Best Lag = %d', lags[max_index])
    return lags[max_index]


def correct_for_initial_delay_codec_artifact(reference_signal : np.ndarray,
                                             degraded_signal: np.ndarray) -> np.ndarray:
    """
        Encoding and decoding can add zero padding at the beginning and end
        of a signal. If the number of zeros doesn't mod with the size of a 
        frame in ViSQOL, the subframe misalignment can throw the similarity 
        score far from where it should be. To compensate, we xcorr the first 
        second of the reference and degraded signals and move the degraded 
        signal to line up.

        Parameters
        ----------
        reference_signal: numpy.ndarray
            Reference signal being used. Single channel
        degraded_signal: numpy.ndarray
            Degraded signal being evaluated. Single channel

        Returns
        -------
        degraded_signal: numpy.ndarray
            Aligned version of the degraded signal
    """
    x_corr_window_size = min(min(reference_signal.shape[0], 48000), degraded_signal.shape[0])
    best_lag = calculate_best_lag(reference_signal[0:x_corr_window_size], degraded_signal[0:x_corr_window_size])
    return degraded_signal[abs(best_lag) - 1:-1] if best_lag < 0.0 else np.pad(degraded_signal, (best_lag, 0), 'constant')


def global_align(reference_signal: np.ndarray, 
                 degraded_signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
        Globally align degraded signal to reference to compensate for encoder 
        artefacts.
        Aligned using cross correlation.

        Parameters
        ----------
        reference_signal: numpy.ndarray
            Reference signal being used. Single channel
        degraded_signal: numpy.ndarray
            Signal to be aligned. Single channel

        Returns
        -------
        degraded_signal: numpy.ndarray
            Aligned version of the degraded signal
    """
    best_lag = calculate_best_lag(reference_signal, degraded_signal)
    min_length = min(degraded_signal.shape[0], reference_signal.shape[0])
    if best_lag < 0:
        return reference_signal[0:min_length], degraded_signal[abs(best_lag) - 1:-1]
    return reference_signal, np.pad(degraded_signal, (best_lag, 0))


def create_reference_patches(sig_img: np.ndarray, warps: list, speech: bool,
                             compare_whole_signal: bool) -> Tuple[np.ndarray, np.ndarray]:
    """
        Create patches from reference signal image to test degraded signal 
        against. For each patch frequency get patches based on max intensity 
        at that f-band. For each warp create patches, reference patches warped 
        by warp factor

        Parameters
        ----------
        sig_img: numpy.ndarray
            input image of signal
        warps: list[float]
            list of warp factors
        speech: bool
            Speech flag
        compare_whole_signal: bool
            Compare whole signal flag

        Returns
        -------
        patches: list[numpy.ndarray]
            List of numpy arrays of each patch
        patch_indexes: list[int]
            List containing the x-offsets for each corresponding patch start 
            index
    """
    num_warps = len(warps)
    
    if speech or not compare_whole_signal:
        patch_indexes = [i for i in range(int(PATCH_SIZE//2), sig_img.shape[1] - PATCH_SIZE, PATCH_SIZE)]
        num_patches = len(patch_indexes)
        
        patches = []
        for i in range(num_patches):
            start_index = patch_indexes[i]
            end_index = start_index + PATCH_SIZE
            img_patch = sig_img[:, start_index:end_index]
            rows, cols = img_patch.shape
            src_img_patch = np.copy(img_patch)

            # Does this work? Good question!
            for j in range(num_warps):
                w_cols = round(cols * warps[j])
                x = np.array([int(i/(w_cols) * cols) for i in range(w_cols)])
                interp_func = RectBivariateSpline([y for y in range(rows)], [y for y in range(cols)], src_img_patch)
                for y in range(rows):
                    for z in range(cols):
                        img_patch[y][z] = interp_func.ev(y,z)
                patches.append(img_patch)
        return np.array(patches), np.array(patch_indexes)
    else:
        patch_indexes = [i for i in range(0, sig_img.shape[1], PATCH_SIZE)]
        LOGGER.debug('Patch indexes: %s', patch_indexes)

        patches = [np.array(sig_img[:, patch_indexes[i]:patch_indexes[i+1]]) for i in range(len(patch_indexes)-1)]
        LOGGER.info('Patches length=%d, 1st shape=%s', len(patches), patches[0].shape)
        if patch_indexes[-1] + PATCH_SIZE > sig_img.shape[1]:
            LOGGER.info('Partial patch at end')
            patches.append(np.array(sig_img[:, patch_indexes[-1]:sig_img.shape[1]]) )
        return np.array(patches), np.array(patch_indexes)


def align_degraded_patches_nsim(deg_img: np.ndarray, ref_patches: np.ndarray, 
                                warp: list, num_bands: int, ref_patch_indexes: list,
                                L: int, speech: bool) -> Tuple[np.ndarray, list]:
    """
        Finds the indices of the best patch matches in the degraded signal image

        Parameters
        ----------
        deg_img: numpy.ndarray
            Spectrogram of the degraded signal
        ref_patches: list[numpy.ndarray]
            List containing all of the reference patches
        warp: list[float]
            The warp to apply
        num_bands: int
            The number of freqeuncy bands that the signal is divided into
        ref_patch_indexes: list[int]
            The indexes at which each patch in the reference signal starts
        L: int
            The mysterious L value
        speech: bool
            Bool indicating whether or not there is speech in the signals
        
        Returns
        -------
        patch_corr: numpy.ndarray
            Numpy array containing the correlation scores for each patch
        deg_indexes: list[int]
            List of x-offsets of the the degraded patch best match to the reference signal patches
    """
    try:
        warp_index = warp.index(1)
    except(ValueError):
        warp_index = 0

    num_frames = ref_patches[0].shape[1]
    max_slide_offset = deg_img.shape[1] - ref_patches[0].shape[1]
    LOGGER.debug('Sig img shape = %s patches shape = %s', deg_img.shape, ref_patches[0].shape)
    num_patches = len(ref_patches)
    patch_corr = np.empty([max_slide_offset, num_patches])
    patch_corr[:] = np.nan
    deg_indexes = []
    
    LOGGER.debug('Num Frames = %d', num_frames)
    LOGGER.debug('Max Slide Offset = %d', max_slide_offset)
    LOGGER.debug('Num Patches = %d', num_patches)
    LOGGER.debug('Patch Corr = %s', patch_corr.shape)

    start_index = 0
    for i in range(num_patches):
        slide_offset = start_index

        for j in range(start_index, max_slide_offset):
            img_patch = ref_patches[i]
            num_cols = img_patch.shape[1]
            deg_patch = deg_img[ 0 : num_bands , slide_offset : slide_offset + num_cols]
            neurogram_map = nsim_map(img_patch, deg_patch, L)
            patch_corr[j,i] = np.mean(neurogram_map)
            slide_offset += 1

        deg_indexes.append(np.argmax(patch_corr[:,i]))
    LOGGER.debug('patch_corr : %s', patch_corr[0,:])
    LOGGER.debug('deg indexes : %s', deg_indexes)
    return patch_corr, deg_indexes


def align_degraded_patches_audio(sig_img, ref_patches,
                                 ref_patches_indexes, warp, num_bands,
                                 L, speech) -> Tuple[np.ndarray, list]:
    """
        Finds the indices of the best patch matches in the degraded signal image

        Parameters
        ----------
        deg_img: numpy.ndarray
            Spectrogram of the degraded signal
        ref_patches: list[numpy.ndarray]
            List containing all of the reference patches
                ref_patch_indexes: list[int]
            The indexes at which each patch in the reference signal starts
        warp: list[float]
            The warp to apply
        num_bands: int
            The number of freqeuncy bands that the signal is divided into

        L: int
            The mysterious L value
        speech: bool
            Bool indicating whether or not there is speech in the signals
        
        Returns
        -------
        patch_corr: numpy.ndarray
            Numpy array containing the correlation scores for each patch
        deg_indexes: list[int]
            List of x-offsets of the the degraded patch best match to the 
            reference signal patches
    """
    try:
        warp_index = warp.index(1)
    except(ValueError):
        warp_index = 0

    num_frames = ref_patches[0].shape[1]
    max_slide_offset = sig_img.shape[1] - ref_patches[0].shape[1]
    num_patches = len(ref_patches)
    patch_corr = np.empty([max_slide_offset, num_patches])
    patch_corr[:] = np.nan
    deg_indexes = []

    LOGGER.debug('Num Frames = %d', num_frames)
    LOGGER.debug('Max Slide Offset = %d', max_slide_offset)
    LOGGER.debug('Num Patches = %d', num_patches)
    LOGGER.debug('Patch Corr = %s', patch_corr.shape)

    for i in range(num_patches):
        LOGGER.debug('%s', ref_patches[0].shape)
        start_index = ref_patches_indexes[i-1] + int(math.floor(ref_patches[0].shape[1] / 2))   if i > 0 else 0       
        end_index = ref_patches_indexes[i+1] - int(math.floor(ref_patches[0].shape[1] / 2)) if i < num_patches - 1 else max_slide_offset

        slide_offset = start_index
        for j in range(start_index, end_index):
            img_patch = ref_patches[i]
            num_cols = img_patch.shape[1]
            deg_patch = sig_img[ 0 : num_bands , slide_offset : slide_offset + num_cols]
            neurogram_map = nsim_map(img_patch, deg_patch, L)
            patch_corr[j,i] = np.mean(neurogram_map)
            slide_offset += 1
        deg_indexes.append(np.nanargmax(patch_corr[:,i]))
        LOGGER.debug('Max Index = %s', np.nanargmax(patch_corr[:,i]))
        
    LOGGER.debug('deg indexes : %s', deg_indexes) 
    return patch_corr, deg_indexes


def create_degraded_patches(degraded_patch_indexes: list, deg_spect: np.ndarray,
                            ref_patches: np.ndarray, PATCH_SIZE: int,
                            warp: list) -> np.ndarray:
    """

    Parameters
    ----------
    degraded_patch_indexes : list
        DESCRIPTION.
    deg_spect : np.ndarray
        DESCRIPTION.
    ref_patches : np.ndarray
        DESCRIPTION.
    PATCH_SIZE : int
        DESCRIPTION.
    warp : list
        DESCRIPTION.

    Returns
    -------
    deg_patches : TYPE
        DESCRIPTION.

    """
    NUM_PATCHES = len(degraded_patch_indexes)
    deg_patches = np.empty(ref_patches.shape)
    
    for patch_index in range(NUM_PATCHES):
        for warp_index in warp:
            smallest_warped_patch_size = np.int32(PATCH_SIZE/max(warp))
            max_warp_offset = PATCH_SIZE - smallest_warped_patch_size # want to test NSIM patches around the size of the max warp offset
            earliest_frame_to_consider = degraded_patch_indexes[patch_index] - max_warp_offset
            latest_frame_to_consider = degraded_patch_indexes[patch_index] + max_warp_offset
            
            for slide_offset in range(max(0,earliest_frame_to_consider), latest_frame_to_consider+1):
                ref_patch = ref_patches[patch_index]
                ref_patch_num_cols = ref_patch.shape[1]
                
                current_patch_end_col = slide_offset + ref_patch_num_cols - 1
                deg_patch_end_col = len(deg_spect[0])
         
                if current_patch_end_col <= deg_patch_end_col:
                    deg_patch_last_col = min(current_patch_end_col, deg_patch_end_col)
                    # Numbers are bit weird in here
                    deg_patch = deg_spect[:,slide_offset:deg_patch_last_col+1]
                    deg_patches[patch_index] = deg_patch
                    
    return deg_patches
  
  
def calc_ref_deg_similarity(ref_patches: np.ndarray, deg_patches: np.ndarray, 
                            warp: list, L: int, 
                            similarity_measure: str) -> np.ndarray:
    NUM_PATCHES = ref_patches.shape[0]
    neurogram_patches, mean_warp_patch_nsims = [], []    

    for patch_index in range(NUM_PATCHES): 
        #number of patches
        for warp_index in warp:
            ref_patch = ref_patches[patch_index]
            deg_patch = deg_patches[patch_index]
            if similarity_measure == 'nsim':
                neurogram_map = nsim_map(ref_patch, deg_patch, L)
            elif similarity_measure == 'ssim':
                a, neurogram_map = ssim(deg_patch, ref_patch, 'Radius', 0.33)# Need to be implmented
            else:
                raise Exception ('invalid similarity measure') 

            mean_of_freq_band_sim_means = np.mean(neurogram_map)
            mean_warp_patch_nsims.append(mean_of_freq_band_sim_means)
            neurogram_patches.append(neurogram_map)
    return np.array(mean_warp_patch_nsims), np.array(neurogram_patches)


def extract_best_nsim_per_patch(mean_warp_patch_nsims: np.ndarray,
                                num_patches: int) -> list:
    patch_nsims = []
    for patch_index in range(num_patches):
        optimal_slide_index = mean_warp_patch_nsims.tolist()\
            .index(max(mean_warp_patch_nsims[:patch_index+1]))
        optimal_warp_index = mean_warp_patch_nsims.tolist()\
            .index(max(mean_warp_patch_nsims[optimal_slide_index:patch_index+1]))
        patch_nsims.append(mean_warp_patch_nsims[optimal_warp_index])
    return patch_nsims


def calc_patch_freq_band_similarities(neurogram_patches: list, 
                                      fn: Callable) -> np.ndarray:
    num_patches = len(neurogram_patches)
    num_bands = neurogram_patches[0].shape[0]
    patch_freq_band_mean_similarities = np.empty((num_patches, num_bands))
    patch_freq_band_mean_similarities[:] = np.nan   

    for patch_index in range(num_patches):
        nsim_patch = neurogram_patches[patch_index]
        for band_index in range(num_bands):
            band_nsims = nsim_patch[band_index,:]
            patch_freq_band_mean_similarities[patch_index, band_index] = np.mean(band_nsims)   

    return patch_freq_band_mean_similarities.transpose()


def is_low_pass_filtered(patch_freq_band_mean_similarities: np.ndarray) -> bool:
    percent_freqs_before_consideration = 50
    similarity_threshold = 0.995
    num_contiguous_freqs_above_threshold = count_contiguous_freq_above_threshold(patch_freq_band_mean_similarities, similarity_threshold)
    percent_above_threshold = (num_contiguous_freqs_above_threshold * 100) / len(patch_freq_band_mean_similarities)
    enough_contiguous_passed = percent_above_threshold > percent_freqs_before_consideration
    all_freqs_passed = num_contiguous_freqs_above_threshold == len(patch_freq_band_mean_similarities)
    return enough_contiguous_passed and all_freqs_passed

def count_contiguous_freq_above_threshold(freqs: np.ndarray, 
                                          threshold: float) -> int:
    # Pretty sure we expect freqs to always be a 1D array
    freqs_above_threshold = np.where(freqs > threshold)[0]
    num_contiguous_freqs_above_threshold = 0
    for freq_index in range(len(freqs_above_threshold)):
        if freqs_above_threshold[freq_index] > num_contiguous_freqs_above_threshold + 1:
            break
        else:
            num_contiguous_freqs_above_threshold = freqs_above_threshold[freq_index]
    return num_contiguous_freqs_above_threshold

def stich_patches_together(patches: np.ndarray) -> np.ndarray:
    raise NotImplementedError('TODO')