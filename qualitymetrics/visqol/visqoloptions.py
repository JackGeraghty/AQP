"""Module containing the dataclass for the VisqolOptions structure"""

from dataclasses import dataclass
from typing import Any
from qualitymetrics.visqol.analysiswindow import AnalysisWindow
from qualitymetrics.visqol.channelconfig import ChannelConfig
from qualitymetrics.visqol.filterbank import Filterbank

@dataclass(frozen=True)
class VisqolOptions:
    """
        Class used to store all the meta-information needed when
        building the signal spectrograms and calculating the NSIM
        score.

        Attributes
        ----------
        arguments: dict
            Dictionary containing all of the arguments passed to the program
        analysis_window: AnalysisWindow
            The constructed analysis window to be used.
        filterbank: Filterbank
            The filterbank to be used when creating the signal spectrograms
        channel_config: ChannelConfig
            The channel configuration being used
    """
    arguments: dict
    analysis_window: AnalysisWindow
    filterbank: Filterbank
    channel_config: ChannelConfig

    def __dict__(self):
        return {
                'arguments' : self.arguments,
                'analysis_window' : str(self.analysis_window),
                'filterbank' : str(self.filterbank),
                'channel_config': str(self.channel_config)
            }

    def __repr__(self):
        return str(self.__dict__())