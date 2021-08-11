import qualitymetrics.visqol.spectrograms.spectrogram as spectrogram
from .node import ViSQOLNode


class SpectrogramNode(ViSQOLNode):
    
    def __init__(self, id_, children, output_key, signal_key,  draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.signal_key = signal_key
        self.type_ = 'SpectrogramNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        signal = result[self.signal_key]
        filterbank = result['visqol_args'].filterbank
        analysis_window= result['visqol_args'].analysis_window
        sample_rate  = analysis_window.sample_rate
        result[self.output_key], result[self.output_key + '_spaces'] = spectrogram.build_spectrogram(signal, sample_rate, filterbank, analysis_window, True)
        return result
    
