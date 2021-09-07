"""Module containing the LoadSignalNode class. Handles the loading of any wav files."""

import sys
import logging

from .node import AQPNode
from pathlib import Path
from librosa import load
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

class LoadSignalNode(AQPNode):
    """Node which loads a signal from either a file path contained within the result dict or from a path passed during initialization."""
    
    def __init__(self, id_: str, output_key: str, file_name_key: str,
                 signal_path: str=None, signal_key: str=None,
                 target_sample_rate: int=48000, mono: bool=False, 
                 draw_options=None, **kwargs):
        """
        Initialize the LoadSignalNode. Only one of either signal_path or signal_key can be used.

        Parameters
        ----------
        file_name_key : str
            Key to store the file name at during execution.
        signal_path : str, optional
            Path to the file to load. The default is None.
        signal_key : str, optional
            Key to retrieve the file path from. The default is None.
        target_sample_rate : int, optional
            Target sample rate to use. If signal doesn't already use this 
            sample rate, then it is resampled by librosa. The default is 48000.
        mono : bool, optional
            Bool indicating whether or not the signal is mono. If the signal 
            loaded only has once channel and mono is set to false, it is reloaded
            with mono set to true. The default is False.
            
        Raises
        ------
        ValueError
            Only one of either signal_path or signal_key can be used. A value error
            is raised if both or neither are set.

        Returns
        -------
        None.

        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options, **kwargs)
        if signal_path and signal_key or not signal_path and not signal_key:
            raise ValueError("Cannot set both signal_path and signal_key or None. One must be set")
        self.file_name_key = file_name_key
        self.signal_path = signal_path
        self.signal_key = signal_key
        self.target_sample_rate = target_sample_rate
        self.mono = mono
        self.type_ = 'LoadSignalNode'
       
    
    def execute(self, result: dict, **kwargs) -> dict:
        """Load the signal and assign it to the result dict alongside the file name.
        
        Parameters
        ----------
        result : dict
            The result dictionary used throughout the pipeline.

        Returns
        -------
        result : dict
            The result dictionary used throughout the pipeline.
        """
        super().execute(result, **kwargs)
        if self.signal_path:
            audio = self._load_audio_from_path(self.signal_path)
            result[self.file_name_key] = self.signal_path
        elif self.signal_key:
            audio = self._load_audio_from_path(result[self.signal_key])
            result[self.file_name_key] = result[self.signal_key]
        result[self.output_key] = audio
        return result
    
    
    def _load_audio_from_path(self, path: str):
        """Load the audio signal for the given path.

        Parameters
        ----------
        path : str
            The path of the file to load.

        Returns
        -------
        audio : np.ndarray
            Numpy array of the audio signal.

        """
        converted_path = Path(path)
        try:
            audio = load(converted_path, sr=self.target_sample_rate, mono=self.mono)[0]
            if not self.mono and audio.ndim == 1:
                audio = load(converted_path, sr=self.target_sample_rate, mono=True)[0]
            return audio
        except(FileNotFoundError) as err:
            LOGGER.error("%s", err)
            sys.exit(1)