"""Module containing the functionality for mapping similarity data to a final MOS using the SVM."""

import numpy as np
import logging

from ..node import ViSQOLNode
from constants import LOGGER_NAME
from libsvm.svmutil import svm_load_model, svm_predict

from functools import reduce  
import operator

LOGGER = logging.getLogger(LOGGER_NAME)

class MOSMapperNode(ViSQOLNode):
    """Combines similarity data per channel and maps the similarity scores to MOS using a SVM."""
    
    def __init__(self, id_: str, output_key: str, target_key: str, visqol_args_key: str,
                 path_to_svm: str='config/visqol/svm.txt',draw_options: dict=None, **kwargs):
        """
        Initialize a MOSMapperNode.

        Parameters
        ----------
        target_key : str
            Template string used to as the keys to retrieve the similarity 
            scores from the result dictionary.
        visqol_args_key : str
            Key to retrieve the visqol_args data.
        path_to_svm : str, optional
            Path to the SVM data. Required to construct the SVM.
            The default is 'config/visqol/svm.txt'.
        """
        super().__init__(id_, output_key=output_key, draw_options=draw_options)
        self.target_key = target_key
        self.visqol_args_key = visqol_args_key
        self.model = svm_load_model(path_to_svm)
        self.type_ = 'MOSMapperNode'
      
    
    def execute(self, result: dict, **kwargs):
        """Extract the similarity data for each active channel and map it to a MOS.
        
        The similarity data is a tuple containing, vnsim scores,
        patch_scores and fvnsim scores. 
        
        After applying the specified function (mean/max/min) to the data, pass
        it to the SVM and retrieve a MOS.
        """
        super().execute(result, **kwargs)
        active_channels = result['active_channels']
        
        dict_keys = []
        split_keys = self.target_key.split('.')
        for channel in active_channels:
            split_keys_copy = split_keys.copy()
            split_keys_copy.insert(-1, channel)
            dict_keys.append(split_keys_copy)
            
        sim_data = []
        for d_key in dict_keys:
            similarity_data = get_from_dict(result, d_key)
            sim_data.append(similarity_data)

        patch_function = result[self.visqol_args_key].channel_config.patch_function
        patch_data = [s_data[1] for s_data in sim_data]
        patch_scores = np.array(patch_data) if len(patch_data) > 1 else patch_function(np.array(patch_data))
        vnsim = np.mean(patch_scores)
        
        fvnsim_func = result[self.visqol_args_key].channel_config.fvnsim_function
        fvnsim_data = [s_data[2] for s_data in sim_data]
        fvnsims = np.array(fvnsim_data) if len(fvnsim_data) > 1 else fvnsim_func(np.array(fvnsim_data))
        
        fvnsims = np.reshape(fvnsims, (fvnsims.shape[0], 1))
        moslqo = -1
        if result[self.visqol_args_key].arguments.perform_mos_mapping:
            if vnsim < 0.15:
                moslqo = 1
            else:
                [p_label, p_acc, p_val] = svm_predict(np.ndarray([0]), fvnsims, self.model, '-q')
                p_val = p_val[0][0]
                if p_val < 1:
                    p_val = 1
                elif p_val > 5:
                    p_val = 5
                moslqo = p_val
        result[self.output_key] = moslqo
        return result
    
def get_from_dict(dataDict, mapList):
    """Given a list of keys retrieve data from a nested dictionary."""
    return reduce(operator.getitem, mapList, dataDict)