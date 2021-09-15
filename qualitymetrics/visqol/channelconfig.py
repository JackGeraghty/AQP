"""Module containing the dataclass for the ChannelConfig structure."""

import numpy as np
import math
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict
from pipeline import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)

@dataclass(frozen=True)
class ChannelConfig:
    """Class which stores the information relating to the way in which the channels are configured.

    Attributes
    ----------
    channel_info: dict
        Stores which channels are active, true = active, false = not-active.
    patch_function: function
        Function used when evaluating each of the patches.
    fvnsim_function: function
        Function used when calculating the vsnsim score.
    """
    
    channel_info : Dict[str, bool] = field(default_factory=lambda: {'left':None,'right':None, 'mid':None, 'side': None})
    patch_function: Callable[[], int] = max
    fvnsim_function:  Callable[[], int]= max

    def __dict__(self):
        """Get the class as a Dict."""
        return {
                'channel_info': self.channel_info,
                'patch_function': self.patch_function.__name__,
                'fvnsim_function': self.fvnsim_function.__name__
            }

    def __repr__(self):
        """Represent the class as a dict."""
        return str(self.__dict__())

def setup_channel_configuration(reference_signal: np.ndarray, 
                                degraded_signal: np.ndarray,
                                channel_configuration: ChannelConfig) -> ChannelConfig:
    """Handle the final steps of constructing the channel configuraton data if it is necessary.

    Parameters
    ----------
    reference_signal: numpy.ndarray
        Reference signal being used
    degraded_signal: numpy.ndarray
        Degraded signal being evaluted

    Returns
    -------
    channel_config: ChannelConfig
        Finalized channel configuration information
    """
    LOGGER.debug('Reference Signal Shape = %s', reference_signal.shape)
    LOGGER.debug('Degraded Signal Shape = %s', degraded_signal.shape)

    if reference_signal.ndim == 1:
        channels = {
            'left': False,
            'right': False,
            'mid': True,
            'side': False
        }
    else:
        threashold = 0.1
        reference_signal_mid_energy = math.sqrt(np.mean(np.square((reference_signal.sum(axis=0) / 2))))
        degraded_signal_mid_energy = math.sqrt(np.mean(np.square((degraded_signal.sum(axis=0) / 2))))
        reference_signal_avg_energy = (math.sqrt(np.mean(np.square(reference_signal[0,:]))) + math.sqrt(np.mean(np.square(reference_signal[1,:])))) / 2
        degraded_signal_avg_energy = (math.sqrt(np.mean(np.square(degraded_signal[0,:]))) + math.sqrt(np.mean(np.square(degraded_signal[1,:])))) / 2
    
        if reference_signal_mid_energy < reference_signal_avg_energy * threashold or degraded_signal_mid_energy < degraded_signal_avg_energy * threashold:
            channels = {
                'left': True,
                'right': True,
                'mid': False,
                'side': False
            }
        else:
            channels = {
                'left': False,
                'right': False,
                'mid': True,
                'side': False
            }
    return ChannelConfig(channels, channel_configuration.patch_function, channel_configuration.fvnsim_function)

def calc_channel_score(score_list: list, func_name: Callable):
    """Use to calculate the patch NSIM score and the MOSLQO score when ViSQOL has been used on more than one channel."""
    if score_list.ndim == 1:
        return score_list
    else:
        return func_name(score_list)      