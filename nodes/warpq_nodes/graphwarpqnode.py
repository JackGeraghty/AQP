from ..node import AQPNode
import seaborn as sns
from scipy.stats import pearsonr
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

class GraphWarpQNode(AQPNode):
    
    def __init__(self, id_, df_key, x_key, y_key, **kwargs):
        super().__init__(id_, **kwargs)
        self.df_key = df_key
        self.x_key = x_key
        self.y_key = y_key
        self.type_ = 'GraphWarpQNode'
        
        
    def execute(self, result, **kwargs):
        super().execute(result, **kwargs)
        df = result[self.df_key]

        pearson_coef, p_value = pearsonr(df[self.x_key], df[self.y_key])
        Spearmanr_coef, p_spearman = spearmanr(df[self.x_key], df[self.y_key])                                  
        
        #plt.figure()           
        sns.relplot(x="MOS", y="warp_q", 
                    hue="Codec", palette="muted",
                    data=df).fig.suptitle(
                        'Per-sample Correlation: Pearsonr= '+ str(round(pearson_coef,2)) +
                        ', Spearman='+str(round(Spearmanr_coef,2))
                        )
        #plt.tight_layout()
        #plt.show()
        return result