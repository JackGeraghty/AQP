"""Module containing the dataclass for the Filterbank structure"""

import logging
import numpy as np

from dataclasses import dataclass, field
from scipy.signal.windows import triang, hann
from qualitymetrics.visqol.constants import BAND_FREQUENCIES

LOGGER = logging.getLogger('pipeline')

@dataclass
class Filterbank:
    def __repr__(self):
        return str(self.__dict__())
    
@dataclass
class MelFilter(Filterbank):
    name : str = 'mel'
    band_flag : str = 'dynamic'
    band_frequencies : list = field(default_factory=lambda: [])
    num_periodogram_ffts : int = 512
    window_function = triang
    min_frequency : int = 50
    max_frequency : int = 16000
    num_fft_bands : int = 32
    num_cep_bands : int = 13
    output_type : str = 'cepstrals'
    num_bands : int = field(init=False)
    
    def __post_init__(self):
        self.num_bands = self.num_fft_bands - 2 if self.output_type == 'audioSpectrogram' else self.num_cep_bands
   
    def __dict__(self):
        return {
                'name' : 'mel',
                'band_flag': self.band_flag,
                'band_frequencies' : self.band_frequencies,
                'num_periodogram_ffts' : self.num_periodogram_ffts,
                'window_function' : self.window_function.__name__,
                'min_frequency': self.min_frequency,
                'max_frequency': self.max_frequency,
                'num_fft_bands': self.num_fft_bands,
                'num_bands': self.num_bands,
                'output_type': self.output_type,
                'num_cep_bands' : self.num_bands
            }

@dataclass
class GammatoneFilter(Filterbank):
    name : str = 'gammatone'
    band_flag : str = 'dynamic'
    band_frequencies : np.array = field(default_factory=lambda: [])
    low_frequency : int = 50
    high_frequency : int = 1600
    num_bands : int = 32
    window_function = hann ## todo is this the right function to use?

    def __dict__(self):
        return {
                'name' : self.name,
                'band_flag': self.band_flag,
                'band_frequencies': self.band_frequencies,
                'low_frequency': self.low_frequency,
                'high_frequency': self.high_frequency,
                'num_bands' : self.num_bands,
                'window_function': self.window_function.__name__
            }

@dataclass
class GoertzelFilter(Filterbank):
    name : str = 'goertzel'
    band_flag : str = 'ASWB'
    band_frequencies : np.array = field(init=False)
    num_bands : int = field(init=False)

    def __post_init__(self):
        self.band_frequencies = BAND_FREQUENCIES[self.band_flag]
        self.num_bands = len(self.band_frequencies)
        
        
    def __dict__(self):
        return {
                'name': self.name,
                'band_flag': self.band_flag,
                'band_frequencies': self.band_frequencies,
                'num_bands': self.num_bands
            }

@dataclass
class PowerSpectralDensityFilter(Filterbank):
    name : str = 'power_spectral_density'
    band_flag : str = 'bark_scale_edges'
    band_frequencies : list = field(init=False)
    fft_band_grouping_function = min
    num_bands : int = field(init=False)

    def __post_init__(self):
        self.band_frequencies = BAND_FREQUENCIES[self.band_flag]
        self.num_bands = len(self.band_frequencies) - 1 if 'edges' in self.band_flag else len(self.band_frequencies)
    
    def __dict__(self):
        return {
                'name' : self.name,
                'band_flag': self.band_flag,
                'band_frequencies': self.band_frequencies,
                'fft_band_grouping_function': self.fft_band_grouping_function.__name__,
                'num_bands': self.num_bands
            }

def create_filterbank(configuration_dict: dict) -> Filterbank:
    """
        Helper function for creating a filterbank based on a dictionary
        created from a JSON file

        Parameters
        ----------
        configuration_dict: dictionary
            Dictionary containing the construction parameters of the filterbank
            
        Returns
        -------
        filterbank: Filterbank
            Specific type of filterbank based on the name value in the
            configuration dictionary with the values given in the
            configuration dictionary
    """

    #Python doesn't have a switch statement in 3.8
    # 3.10 (February 2021) introduces the match-case statement, something
    # for the future
    try:
        filterbank_name = configuration_dict['name']
        try:
            if filterbank_name == 'mel':
                return MelFilter(**configuration_dict)
            elif filterbank_name == 'gammatone':
                return GammatoneFilter(**configuration_dict)
            elif filterbank_name == 'goertzel':
                return GoertzelFilter(**configuration_dict)       
            elif filterbank_name == 'power_spectral_density':
                return PowerSpectralDensityFilter(**configuration_dict)     
        except(KeyError):
            LOGGER.warn('Invalid filter name, %s, passed. Returning default MelFilter', filterbank_name)
            return MelFilter()
    except(KeyError):
        LOGGER.warn("Configuration dictionary missing 'name' key, returning default MelFilterbank")
        return MelFilter()