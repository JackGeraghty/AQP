'''Module containing the functionality to produce Goertzel Spectrograms'''

import numpy as np
import multiprocessing as mp
import logging
import math
import cmath

from multiprocessing import shared_memory
from queue import Empty
from qualitymetrics.visqol.filterbank import Filterbank
from qualitymetrics.visqol.analysiswindow import AnalysisWindow

LOGGER = logging.getLogger('pipeline')

def goertzel(signal: np.ndarray,
             sample_rate: int,
             filterbank: Filterbank,
             analysis_window: AnalysisWindow,
             time_spaces: list,
             num_windows: int) -> np.ndarray:
    '''
    
    Builds a Goertzel Spectrogram

    Parameters
    ----------
    signal : np.ndarray
        Input signal.
    sample_rate : int
        Sample rate of the input signal.
    filterbank : Filterbank
        Filterbank containing the necessary information for creating a 
        Goertzel Spectrogram.
    analysis_window : AnalysisWindow
        Analysis Window containing the necessary information for creating a 
        Goertzel Spectrogram.
    time_spaces : list
        List containing the point at which each frame begins.
    num_windows : int
        The amount of windows to divide the signal into.

    Returns
    -------
    spect: np.ndarray
        Goertzel spectrogram.

    '''
    
    # Building the spectrogram takes a decent amount of time when running
    # on a single core, so if there's multiple cores, run in it parallel!
    if mp.cpu_count() > 1:
        LOGGER.info('Multiple Cores detected, running processes in parallel')
        
        # Paralleling processing in Python is pretty messy IMO, and to avoid
        # copying a load of data every time, some shared memory is needed
        
        # First bit of shared memory is for the spectrogram itself,
        # Need to allocate enough space for the entire 2D array of complex doubles
        # Complex double is 128 bits or 16 bytes, hence the * 16
        spect_shm = shared_memory.SharedMemory(create=True, size=filterbank.num_bands * num_windows * 16)
        # Then an actual numpy array needs to be attached to this shared memory
        spect = np.ndarray((filterbank.num_bands, num_windows), dtype='complex_', buffer=spect_shm.buf)
        
        # Same then happens for the transformed_cols array, except instead of
        # 128 bit complex doubles, it's just 64 bit floats i.e. a double
        transformed_cols_shm = shared_memory.SharedMemory(create=True, size=len(analysis_window.data) * num_windows * 8)
        transformed_cols = np.ndarray((len(analysis_window.data), num_windows), dtype='float64', buffer=transformed_cols_shm.buf)
        # With the space allocated, the data can be assigned to it.
        transformed_cols[:] = build_window_transformed_cols(analysis_window.data, signal, num_windows, analysis_window.window_overlap)
    
        # Same for the coefficients array as the transformed_cols
        coefficients_shm = shared_memory.SharedMemory(create=True, size=len(filterbank.band_frequencies) * 8)
        coefficients = np.ndarray((len(filterbank.band_frequencies)), dtype='float64', buffer=coefficients_shm.buf)
        coefficients[:] = filterbank.band_frequencies / sample_rate * transformed_cols.shape[0]
        
        # Once the memory is assigned, it can now be shared across processes
        
        cpu_count = mp.cpu_count()
        LOGGER.info('cpu_count = %d', cpu_count)
            
        ## To help share data across processes, also need a Queue, nothing fancy
        in_q = mp.Queue()
        
        # Dict of shared memory names, this enables a lookup of the shared memory
        # by different processes.
        shm_names = {
            'spect': spect_shm,
            'cols': transformed_cols_shm,
            'coefficients': coefficients_shm
            }
        # Create the processes based on the number of CPUs
        processes = [mp.Process(target=update_goertzel, args=(in_q, shm_names, spect.shape, transformed_cols.shape, coefficients.shape)) for _ in range(cpu_count)]
        
        # Start each process
        for p in processes:
            p.start()

        # Send the data to these processes via the queue            
        for window_index in range(num_windows):
            in_q.put(window_index)
        
        # Send a negative one to indicate that there's no more indexes to process
        for _ in processes:
            in_q.put(-1)
                
        # Wait for the processes to join
        for p in processes:
            p.join()
            
        spect_copy = np.copy(spect) ## need to copy, since the close and unlink operations destroy the original
        LOGGER.info("Finished processing spectrogram")
        # Tidy up the shared memory
        spect_shm.close()
        spect_shm.unlink()
        transformed_cols_shm.close()
        transformed_cols_shm.unlink()
        coefficients_shm.close()
        coefficients_shm.unlink()
    
        return spect_copy
    
    # If there's only a single core then run the process sequentially
    LOGGER.info('Single Core detected, running processes sequentially')
    spect = np.zeros((filterbank.num_bands, num_windows), dtype='complex_')
    transformed_cols = build_window_transformed_cols(analysis_window.data, signal, num_windows, analysis_window.window_overlap)
    coefficients = filterbank.band_frequencies / sample_rate * transformed_cols.shape[0]
    for window_index in range(num_windows):
        signal_window = transformed_cols[:, window_index]
        window_powers = generalized_goertzel(signal_window, coefficients)
        spect[:, window_index] = window_powers
    return spect


def update_goertzel(in_q, shm_names: dict, 
                    spect_shape: tuple,
                    cols_shape: tuple,
                    coefficients_shape: tuple):
    '''
    Function used by each process to calculate it's chunk of the spectrogram
    and then assign it

    Parameters
    ----------
    in_q : mp.queue
        The queue containing the indexes to operate on, shared across processes.
    shm_names : dict
        Dictionary of the SharedMemory names.
    spect_shape : tuple
        Shape of the spectrogram.
    cols_shape : tuple
        Shape of the transformed_cols array.
    coefficients_shape : tuple
        Shape of the coefficients array.

    Returns
    -------
    None

    '''
    # Get the SharedMemory for each numpy array
    spect_shm = shm_names['spect']
    transformed_cols_shm = shm_names['cols']
    coefficients_shm = shm_names['coefficients']
    # Get the value of each SharedMemory location in a numpy array
    spect = np.ndarray(spect_shape, dtype='complex_', buffer=spect_shm.buf)
    transformed_cols = np.ndarray(cols_shape, dtype='float64', buffer=transformed_cols_shm.buf)
    coefficients = np.ndarray(coefficients_shape, dtype='float64', buffer=coefficients_shm.buf)
    
    ## While there's window indexes to process, keep processing.
    while True:
        try:    
            window_index = in_q.get(1)
        except Empty:
            LOGGER.debug('Empty Queue')
            break
        if window_index == -1:
            LOGGER.debug('Received -1, stopping')
            break
        # Calculate the chunk of spectrogram and assign it back to SharedMemory
        signal_window = transformed_cols[:, window_index]
        window_powers = generalized_goertzel(signal_window, coefficients)
        spect[:,window_index] = window_powers[:,]
           

def build_window_transformed_cols(analysis_window_data: np.ndarray,
                                  sample_window: np.ndarray,
                                  num_windows: int,
                                  window_overlap: int) -> np.ndarray:
    '''
    Build the signal after the analysis window has been applied to it.

    Parameters
    ----------
    analysis_window_data : np.ndarray
        Data used to transform the sample window
    sample_window : np.ndarray
        The window of the reference or degraded signal being transformed by 
        the analysis window.
    num_windows : int
        Number of windows to divide the signal into.
    window_overlap : int
        The amount of overlap between windows.

    Returns
    -------
    transformed_cols : TYPE
        DESCRIPTION.

    '''
    transformed_cols = np.zeros((len(analysis_window_data), num_windows ), dtype='float64')
    s_index = 0
    e_index = len(analysis_window_data) 
    for win_index in range(num_windows):
        windowed_signal = sample_window[s_index:e_index]

        transformed_cols[:, win_index] = np.asarray([windowed_signal[i] * analysis_window_data[i] for i in range(len(windowed_signal))])
        s_index += window_overlap
        e_index += window_overlap
    return transformed_cols        


def generalized_goertzel(signal_window: np.ndarray, 
                         coefficients: np.ndarray) -> np.ndarray:
    '''
    Finds the power of frequencies in a signal

    Parameters
    ----------
    signal_window : np.ndarray
        The signal to calculate the powers on. This will be the window 
        from the STFT.
    coefficients : np.ndarray
        Coefficients to use.

    Returns
    -------
    powers : np.ndarray
        Array of signal powers.

    '''
    signal_length = len(signal_window)
    signal_window = np.reshape(signal_window, (signal_length, 1), order='F')
    num_freqs = len(coefficients)
    powers = np.zeros((num_freqs), dtype = 'complex_')
    for freq_index in range(num_freqs):
        A = 2 * math.pi * (coefficients[freq_index] / signal_length)
        B = math.cos(A) * 2
        C = cmath.exp(A * -1j)
        s_0 = 0
        s_1 = 0
        s_2 = 0
        for i in range(0, signal_length-1):
            s_0 = signal_window[i] + B * s_1 - s_2
            s_2 = s_1
            s_1 = s_0
        s_0 = signal_window[signal_length - 1] + B * s_1 - s_2
        powers[freq_index] = s_0 - s_1 * C
        powers[freq_index] = powers[freq_index] * cmath.exp(A * (signal_length - 1) * -1j)
    return powers