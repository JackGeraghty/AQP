# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 17:21:09 2021

@author: jgera
"""
from .node import Node
import qualitymetrics.visqol.dsp as dsp


class VisqolChannelNode(Node):
    
    def __init__(self, id_, children, output_key=None,
                 reference_signal_key='reference_signal',
                 degraded_signal_key='degraded_signal', **kwargs):
        super().__init__(id_, children, output_key)
        self.reference_signal_key = reference_signal_key
        self.degraded_signal_key = degraded_signal_key
        self.type_ = 'VisqolChannelNode'
        
    def execute(self, result, **kwargs):
        super().execute(result)
        reference = dsp.extract_channel(result[self.reference_signal_key], kwargs['var'])
        degraded = dsp.extract_channel(result[self.degraded_signal_key], kwargs['var'])
        visqol_args = result['visqol_args']
        if visqol_args.arguments.compensate_for_padding:
            degraded = dsp.correct_for_initial_delay_codec_artifact(reference, degraded)
        if visqol_args.arguments.global_align:
            reference, degraded = dsp.global_align(reference, degraded)
        result['reference_signal'] = reference
        result['degraded_signal'] = degraded
        return result