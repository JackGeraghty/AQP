from tabulate import tabulate
from .node import AQPNode
from texttable import Texttable

from scipy.stats import pearsonr
from scipy.stats import spearmanr
from pathlib import Path

class CorrelationTableNode(AQPNode):
    
    def __init__(self, id_, df_key, mos_col_name, col_keys, output_file, **kwargs):
        super().__init__(id_)
        self.df_key = df_key
        self.col_keys = col_keys
        self.mos_col_name = mos_col_name
        self.output_file = output_file
        self.type_ = "LatexTableNode"
        
    
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        df = result[self.df_key]
        col_one_data = df[self.col_keys[0]] # warp_q
        col_two_data = df[self.col_keys[1]] # pesq
        mos = df[self.mos_col_name]
        pearson_coef, p_value = pearsonr(col_one_data, df['MOS'])
        Spearmanr_coef, p_spearman = spearmanr(col_one_data, df['MOS'])

        pearson_coef_, p_value = pearsonr(col_two_data, df['MOS'])
        Spearmanr_coef_, p_spearman = spearmanr(col_two_data, df['MOS'])
        rows = [
                ['WARP-Q', pearson_coef, Spearmanr_coef],
                ['PESQ', pearson_coef_, Spearmanr_coef_]
            ]
        
        table = Texttable()
        table.set_cols_align(["c"] * 3)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.add_rows(rows)        

        table = tabulate(rows, headers=['Quality Metric', 'Pearson', 'Spearman'], tablefmt='latex')
        with open(Path(self.output_file), 'w+') as f:
            f.write(table)
        return result