import numpy as np
import logging
import math

from .rastamat import melfcc
from .gammatone import gtgram
from .goertzel import goertzel
from typing import Tuple
from qualitymetrics.visqol.filterbank import Filterbank
from qualitymetrics.visqol.analysiswindow import AnalysisWindow

LOGGER = logging.getLogger('pipeline')

def calculate_time_spaces(window_overlap: float, signal_len: int, 
                          analysis_window_len: int, sample_rate: int) -> list:
    """
        Calculates the size of each frame. Used for plotting later on 

        Parameters
        ----------
        window_overlap: float
            TBC
        signal_len: int
            Length of the input signal array
        analysis_window_len: int
            Length of the analysis window data
        sample_rate: int
            The sample rate of the audio

        Returns
        -------
        time_spaces: List[float]
            A list of floats containing the time(in seconds) at which each
            frame begins

    """
    num_columns = np.fix((signal_len - window_overlap) / (analysis_window_len - window_overlap)) - 1
    column_indexes = [(analysis_window_len - window_overlap) * x for x in range(int(num_columns))]
    return [(x + (analysis_window_len / 2)) / sample_rate for x in column_indexes]

def build_spectrogram(signal: np.ndarray, sample_rate: int, filterbank: Filterbank,
                      analysis_window: AnalysisWindow, do_multiprocessing = False) -> Tuple[np.ndarray, list]:
    """
        Builds a spectrogram for the given input. Used to create both the reference and degraded spectrograms. 
        The final spectrogram power is converted to dB

        Parameters
        ----------
        signal: numpy.ndarray
            Signal to create spectrogram of. Should be single channel
        sample_rate: int
            Sample rate of the input signal
        filterbank: Filterbank
            Filterbank to be used during spectrogram creation
        analysis_window: AnalysisWindow
            Analysis Window to be used

        Returns
        -------
        spectrogram_bf: numpy.ndarray
            Spectrogram in decibels
        time_spaces: List[float]
            A list of floats containing the time(in seconds) at which each frame begins
    """
    num_windows = math.floor((len(signal) - analysis_window.window_overlap) / (len(analysis_window.data) - analysis_window.window_overlap)) 
    time_spaces = calculate_time_spaces(analysis_window.window_overlap, len(signal), len(analysis_window.data), sample_rate)
    spect = build_specific_spectrogram(signal, sample_rate, filterbank, analysis_window, time_spaces, num_windows, do_multiprocessing)
    spectrogram = np.abs(np.real(spect)) # Remove complex components
    spectrogram[spectrogram == 0.0] = np.finfo(float).eps # Replace any zero values with a very small float value
    spectrogram_bf = 10 * np.log10(spectrogram) # convert to power in dB
    LOGGER.debug('Spectrogram Shape=%s', spectrogram.shape)
    return spectrogram_bf, time_spaces

      
def build_specific_spectrogram(signal: np.ndarray, 
                               sample_rate: int, 
                               filterbank: Filterbank,
                               analysis_window: AnalysisWindow,
                               time_spaces: list,
                               num_windows: int,
                               do_multiprocessing: bool) -> np.ndarray:
    """
        Stil WIP
    """
    hop = round(time_spaces[1] - time_spaces[0], 4)
    if filterbank.name == 'mel':
        window_duration = round((1 / analysis_window.overlap) * hop,4)
        return melfcc(signal * 3.3752, sample_rate, min_freq=filterbank.min_frequency, max_freq=filterbank.max_frequency, \
                              n_mfcc=filterbank.num_cep_bands, n_bands=filterbank.num_fft_bands, window_time=window_duration, hop_time=hop, \
                              preemph=0)
    elif filterbank.name == 'gammatone':
        return gtgram(signal, sample_rate, hop, hop, filterbank.num_bands, filterbank.low_frequency)
    elif filterbank.name == 'goertzel':
        return goertzel(signal, sample_rate, filterbank, analysis_window, time_spaces, num_windows)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    