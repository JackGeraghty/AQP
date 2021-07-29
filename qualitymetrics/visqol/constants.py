"""Constants used throughout ViSQOL"""

import numpy as np

CONFIG_FILE_PATH = 'config/visqol_config.json'
DESIRED_SIGNAL_FREQUENCY = 48000
BAND_FREQUENCIES = {
    'NB': np.asarray([150, 250, 350, 450, 570, 700, 840, 1000, 1170, 1370, 1600, 1850, 2150, 2500, 2900, 3400]),
    'WB' : np.asarray([50, 150, 250, 350, 450, 570, 700, 840, 1000, 1170, 1370, 1600, 1850, 2150, 2500, 2900, 3400, 4000, 4800, 6500, 8000]),
    'ASWB' : np.asarray([50, 150, 250, 350, 450, 570, 700, 840, 1000, 1170, 1370, 1600, 1850, 2150, 2500, 2900, 3400, 4000, 4800, 5800, 7000, 8500, 10500, 13500, 16000]),
    'bark_scale_edges' : np.asarray([20, 100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300, 6400, 7700, 9500, 12000, 15500]),
    'mel_scale_edges_beranek' : np.asarray([20, 160, 394, 670, 1000, 1420, 1900, 2450, 3210, 4000, 5100, 6600, 9000, 14000])
}
CHANNELS = ('left', 'right', 'mid', 'side')
NUM_PATCHES = 30
PATCH_SIZE = 30
WARP_FLAGS = {'NB' : True, 'WB': True, 'ASWB': False, 'bark_scale_edges': 1, 'dynamic': 0}
FREQ_BAND_SIM_FUNCTIONS = {'mean':np.mean, 'min':np.min, 'max':np.max}