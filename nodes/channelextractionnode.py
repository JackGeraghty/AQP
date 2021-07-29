from .node import Node

class ChannelExtractionNode(Node):
    
    def __init__(self, id_, children, output_key, channel, signal_key, **kwargs):
        super().__init__(id_, children, output_key)
        self.channel = channel
        self.signal_key = signal_key
        self.type_ = 'ChannelExtractionNode'
        
        
    def execute(self, result):
        """ 
        Used to extract information relating to specific channels present in 
        the input signal

        parameters
        ----------
        signal: numpy.ndarray
            Input signal to extract channel information from
        channel: str
            The channel to try and extract

        returns
        -------
        signal: nump.ndarray
            Subset of the origal signal data, containing only the data 
            relating to the specified channel
        """
        super().execute(result)
        signal = result[self.signal_key]
        if self.channel == 'left':
            result[self.output_key] = signal[0,:]
        elif self.channel == 'right':
            result[self.output_key] = signal[1,:]
        elif self.channel == 'mid':
            result[self.output_key] = (signal[0,:] + signal[1,:]) / 2
        elif self.channel == 'side':
            result[self.output_key] = (signal[0,:] - signal[1,:]) / 2
        return result