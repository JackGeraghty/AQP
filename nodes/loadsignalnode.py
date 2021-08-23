import sys
import logging
from .node import AQPNode
from pathlib import Path
from librosa import load

LOGGER = logging.getLogger('pipeline')

class LoadSignalNode(AQPNode):
    
    def __init__(self, id_, children, output_key, signal_path=None, signal_key=None,
                 target_sample_rate: int=48000, mono: bool=False, draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        if signal_path and signal_key:
            raise ValueError("Cannot set both signal_path and signal_key. Use only one")
            
        self.signal_path = signal_path
        self.signal_key = signal_key
        self.target_sample_rate = target_sample_rate
        self.mono = mono
        self.type_ = 'LoadSignalNode'
       
    
    def execute(self, result, **kwargs) -> dict:
        super().execute(result)
        if self.signal_path:
            audio = self._load_audio_from_path(self.signal_path)
        elif self.signal_key:
            audio = self._load_audio_from_path(result[self.signal_key])
        result[self.output_key] = audio
        return result
    
    
    def _load_audio_from_path(self, path):
        converted_path = Path(path)
        try:
            audio = load(converted_path, sr=self.target_sample_rate, mono=self.mono)[0]
            print(audio.shape)
            if not self.mono and audio.ndim == 1:
                audio = load(converted_path, sr=self.target_sample_rate, mono=True)[0]
            
            return audio
        except(FileNotFoundError) as err:
            LOGGER.error("%s", err)
            sys.exit(1)