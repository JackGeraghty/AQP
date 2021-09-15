"""Module containing the SpectrogramNode, used to create different types of spectrogram."""

import numpy as np
import qualitymetrics.visqol.spectrograms.spectrogram as spectrogram
import matplotlib.pyplot as plt
import librosa.display
import logging
import os

from .node import AQPNode
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class SpectrogramNode(AQPNode):
    """Node which is used to create spectrograms based off of audio signals.
    
    TODO: Refactor to make it less tied to visqol.
    """    
    
    def __init__(self, id_: str, output_key: str, signal_key: str, 
                 file_name_key: str, save_spectrogram: bool=False,
                 output_dir: str='results/', draw_options: dict=None, **kwargs):
        """Initialize a SpectrogramNode.

        Parameters
        ----------
        signal_key : str
            Key used to retrieve the audio signal being used.
        file_name_key : str
            Key used to retrieve the file name of the signal being used. Then
            used for saving the spectrogram.
        save_spectrogram : bool, optional
            Boolean indicating whether or not to save the spectrogram to a file.
            The default is False.
        output_dir : str, optional
            If the spectrogram is being save then this is the path to where 
            the spectrogram should be saved to. The default is 'results/'.
        """
        super().__init__(id_, output_key, draw_options=draw_options)
        self.signal_key = signal_key
        self.file_name_key = file_name_key
        self.save_spectrogram = save_spectrogram
        self.output_dir = output_dir
        self.type_ = 'SpectrogramNode'
    
    
    def execute(self, result: dict, **kwargs):
        """Execute the SpectrogramNode and generate the spectrogram."""
        super().execute(result)
        signal = result[self.signal_key]
        filterbank = result['visqol_args'].filterbank
        analysis_window= result['visqol_args'].analysis_window
        sample_rate  = analysis_window.sample_rate
        result[self.output_key], result[self.output_key + '_spaces'] = spectrogram.build_spectrogram(signal, sample_rate, filterbank, analysis_window, True)

        if self.save_spectrogram:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            file_name = result[self.file_name_key]
            output_path = self.output_dir + file_name.replace('/', '_')
            _plot_spectrogram(result[self.output_key], self.save_spectrogram, output_path)
            
        return result
    

def _plot_spectrogram(spectrogram: np.ndarray, save_spectrogram: bool = False,
                     file_name:str = 'DEFAULT') -> None:
    """Plot and save the spectrogram if the option is set.
    
    TODO: cleanup/refactor 
    """
    fig, ax = plt.subplots()
    img = librosa.display.specshow(spectrogram, ax=ax)
    plt.colorbar(img, ax=ax)
    plt.title(file_name)
    if save_spectrogram:
        if file_name is None:
            LOGGER.error('No file name given, using DEFAULT')
            file_name = 'DEFAULT'
        LOGGER.debug('Saving Spectrogram to %s', f'results/{file_name}.jpg')
        plt.savefig(f'{file_name}.jpg')
    plt.show()