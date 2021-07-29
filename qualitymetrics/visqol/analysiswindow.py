"""Module containing the dataclass for the AnalysisWindow structure"""

import numpy as np
from math import remainder
from dataclasses import dataclass, field
from qualitymetrics.visqol.constants import DESIRED_SIGNAL_FREQUENCY

def calculate_window_size(sample_rate:int = DESIRED_SIGNAL_FREQUENCY) -> int:
    """
        Size of the analysis (e.g. Hamming) window. Ensure that no matter what 
        the sample rate value is, the 'resolution' of the spectrogram is set 
        to give consistent time frames. Otherwise the length (duration) of 
        the patch windows will change with sample rate.

        Parameters
        ----------
        sample_rate:int, optional, default=48000
            Sample rate of the signal being evaluated

        Returns
        -------
        window_size: int
            Size of the analysis window
            
    """
    window_size = round((sample_rate / 8000) * 256)
    if remainder(window_size, 2) != 0:
        window_size -= 1
    return window_size

@dataclass
class AnalysisWindow:
    """
        Class which stores the information representing the
        analysis window of ViSQOL

        Attributes
        ----------
        size: int
            Window size 
        sample_rate: int
            Sample rate of the input signals
        overlap: float
            The amount each frame overlaps with another
        window_overlap:
            TBD
        data: numpy.ndarray
            Data representing the Hamming window
    """
    size :int = calculate_window_size()
    sample_rate :int = DESIRED_SIGNAL_FREQUENCY
    overlap :float = 0.5
    window_overlap : int = field(init=False)
    data : np.ndarray = np.hamming(size)

    def __post_init__(self):
        self.window_overlap = round(self.size * self.overlap)

    def __dict__(self):
        return {
                'size': self.size,
                'sample_rate': self.sample_rate,
                'overlap': self.overlap,
                'window_overlap': self.window_overlap
            }

    def __repr__(self):
        return str(self.__dict__())
