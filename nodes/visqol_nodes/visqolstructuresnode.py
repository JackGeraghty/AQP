import logging
import qualitymetrics.visqol.constants as constants
from .node import ViSQOLNode
from pathlib import Path
from json import load
from qualitymetrics.visqol.analysiswindow import AnalysisWindow
from qualitymetrics.visqol.channelconfig import ChannelConfig, setup_channel_configuration
from qualitymetrics.visqol.filterbank import create_filterbank, MelFilter
from qualitymetrics.visqol.visqolarguments import VisqolArguments
from qualitymetrics.visqol.visqoloptions import VisqolOptions

LOGGER = logging.getLogger('pipeline')

class VisqolStructuresNode(ViSQOLNode):
   
    def __init__(self, id_, children, output_key, 
                 config_file_path='config/visqol/structures_config.json', draw_options=None, **kwargs): 
        super().__init__(id_, children, output_key, draw_options)
        self._config_file_path = Path(config_file_path)
        self.options = self._construct_visqol_options()
        self.type_: str = 'VisqolStructuresNode'
   
        
    def execute(self, result, **kwargs):
        super().execute(result)
        channel_info = self.options['channel_config'].channel_info
        if channel_info['left'] is None and channel_info['right'] is None and channel_info['mid'] is None and channel_info['side'] is None: 
            self.options['channel_config'] = setup_channel_configuration(result['reference_signal'], result['degraded_signal'], self.options['channel_config'])
            
        visqol_options = VisqolOptions(self.options['visqol_args'], self.options['analysis_window'], self.options['filterbank'], self.options['channel_config'])
        channel_info = self.options['channel_config'].channel_info
        result['active_channels']  = tuple([key for key in channel_info if channel_info[key]])
        result['PATCH_SIZE'] = constants.PATCH_SIZE
        warp_flag = constants.WARP_FLAGS[visqol_options.filterbank.band_flag]
        result['warps'] = [1, 0.95, 1.05] if warp_flag else [1]
        result['L'] = 1
        
        result[self.output_key] = visqol_options
        
        return result 
    
    
    def _construct_visqol_options(self):
        try:
            with open(self._config_file_path, 'rb') as config:
                config_data = load(config)
                analysis_window = AnalysisWindow(**(config_data['analysis_window']))
                filterbank = create_filterbank(config_data['filterbank'])
                channel_config = ChannelConfig(**config_data['channel_config'])
                visqol_args = VisqolArguments(**config_data['program_arguments'])
                return {
                        'visqol_args': visqol_args,
                        'analysis_window': analysis_window,
                        'filterbank': filterbank,
                        'channel_config': channel_config
                    }
        except FileNotFoundError as err:
            LOGGER.error("%s", err)
            LOGGER.info('Using default configurations for the AnalysisWindow, ChannelConfig and Filterbank')
            return {
                    'visqol_args': VisqolArguments(),
                    'analysis_window': AnalysisWindow,
                    'filterbank': MelFilter(),
                    'channel_config': channel_config
                }
        return ()