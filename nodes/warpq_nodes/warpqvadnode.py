from ..node import WarpQNode

from pyvad import vad

class WarpQVADNode(WarpQNode):
    
    def __init__(self, id_: str, ref_sig_key: str, deg_sig_key: str,
                 **kwargs):
        super().__init__(id_)
        self.ref_sig_key = ref_sig_key
        self.deg_sig_key = deg_sig_key
        self.type_ = "WarpQVadNode"
    
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        ref_signal = result[self.ref_sig_key]
        deg_signal = result[self.deg_sig_key]
        vad_hop_size = 30
        vad_sr = result['sr']
        aggresive = 0
        
        vact_ref = vad(ref_signal, vad_sr, fs_vad=vad_sr, hop_length=vad_hop_size, vad_mode=aggresive)
        ref_sig_vad = ref_signal[vact_ref==1]
        
        vact_deg = vad(deg_signal, vad_sr, fs_vad=vad_sr, hop_length=vad_hop_size, vad_mode=aggresive)
        deg_sig_vad = deg_signal[vact_deg==1]
        
        result[self.ref_sig_key] = ref_sig_vad
        result[self.deg_sig_key] = deg_sig_vad
        return result
        