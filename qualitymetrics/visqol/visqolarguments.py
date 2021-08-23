from dataclasses import dataclass
from qualitymetrics.visqol.constants import FREQ_BAND_SIM_FUNCTIONS

@dataclass
class VisqolArguments():
    mosqol_mapper:str = 'nu-svr_radial'
    perform_mos_mapping: bool = True
    csv_output_path: str = None
    compensate_for_padding: bool = False
    use_patch_alignment: bool = True
    speech: bool = False
    floor_spectrograms: bool = True
    similarity_measure: str = 'nsim'
    global_align: bool = True
    freq_band_sim_per_patch: str = 'mean'
    freq_band_sim_aggregate: str = 'mean'
    global_comparison: bool = False
    compare_whole_signal: bool = False
    save_spectrograms: bool = False
    debug: bool = False
    
    def __post_init__(self):
        if self.freq_band_sim_per_patch not in FREQ_BAND_SIM_FUNCTIONS:
            self.freq_band_sim_per_patch = 'mean'
        if self.freq_band_sim_aggregate not in FREQ_BAND_SIM_FUNCTIONS:
            self.freq_band_sim_aggregate = 'mean'