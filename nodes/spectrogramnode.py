import qualitymetrics.visqol.spectrograms.spectrogram as spectrogram
import matplotlib.pyplot as plt
import librosa.display
import logging
import os
from .node import ViSQOLNode

LOGGER = logging.getLogger('pipeline')

class SpectrogramNode(ViSQOLNode):
    
    def __init__(self, id_, children, output_key, signal_key, is_reference,
                 save_spectrogram=False, output_dir='results/', draw_options=None, **kwargs):
        super().__init__(id_, children, output_key, draw_options=draw_options)
        self.signal_key = signal_key
        self.is_reference = is_reference
        self.save_spectrogram = save_spectrogram
        self.output_dir = output_dir
        self.type_ = 'SpectrogramNode'
    
    
    def execute(self, result, **kwargs):
        super().execute(result)
        signal = result[self.signal_key]
        filterbank = result['visqol_args'].filterbank
        analysis_window= result['visqol_args'].analysis_window
        sample_rate  = analysis_window.sample_rate
        result[self.output_key], result[self.output_key + '_spaces'] = spectrogram.build_spectrogram(signal, sample_rate, filterbank, analysis_window, True)

        if self.save_spectrogram:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            file_name = result['reference_file'] if self.is_reference else result['degraded_file']
            output_path = self.output_dir + file_name.replace('/', '_')
            plot_spectrogram(result[self.output_key], self.save_spectrogram, output_path)
            
        return result
    

def plot_spectrogram(spectrogram, save_spectrogram: bool = False,
                     file_name:str = 'DEFAULT') -> None:
    fig, ax = plt.subplots()
    img = librosa.display.specshow(spectrogram, ax=ax)
    
    if save_spectrogram:
        if file_name is None:
            LOGGER.error('No file name given, using DEFAULT')
            file_name = 'DEFAULT'
        LOGGER.info('Saving Spectrogram to %s', f'results/{file_name}.jpg')
        plt.colorbar(img, ax=ax)
        plt.title(file_name)
        plt.savefig(f'{file_name}.jpg')
    plt.show()