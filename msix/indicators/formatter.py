#Add our technical Indicators
from msix.indicators.ichimoku_cloud import IchimokuIndicator
# from msix.indicators.nvi import NegativeVolumeIndexIndicator
import pandas as pd 
import numpy as np

class Formatter:
    def __init__(self, df):
        self.df = df
        self.volume = None
        self.ichi = None
        self.rsi = None
        self.final = None
        
    def volume_indicators(self):
        #Create Dataframe for Volume Indicators
        self.volume = pd.DataFrame()
        self.volume['NVI'] =NegativeVolumeIndexIndicator(self.df['Close'], self.df['Volume']).negative_volume_index()
#         self.volume['NVI_Mean'] = self.volume['NVI'].rolling(5).mean()
        self.volume['NVI_Mean'] = self.volume.ewm(span=255, adjust=False).mean()
        self.volume['NVI_Above_Mean'] = self.volume['NVI'] > self.volume['NVI_Mean']
        self.volume['NVI_Above_Mean'] = self.volume['NVI_Above_Mean'].astype('int')
        return self.volume

    def ichi_frame(self):
        #ichimoku indicators as dataframe
        self.ichi = pd.DataFrame()
        self.ichi['ichi_a'] = IchimokuIndicator(self.df['fhigh'],self.df['flow']).ichimoku_a()
        self.ichi['ichi_b'] = IchimokuIndicator(self.df['fhigh'],self.df['flow']).ichimoku_b()
        self.ichi['ichi_bl']=IchimokuIndicator(self.df['fhigh'],self.df['flow']).ichimoku_base_line()
        self.ichi['ichi_cl']=IchimokuIndicator(self.df['fhigh'],self.df['flow']).ichimoku_conversion_line()
        return self.ichi

    def rsiframe(self):
        #Create RSIs
        self.rsi = pd.DataFrame()
        self.rsi['RSI'] = RSIIndicator(self.df['Close'],fillna=False).rsi()
        self.rsi['stochRSI'] = StochRSIIndicator(self.df['Close'],fillna=False).stochrsi() * 100
        return self.rsi

    def concat_frames(self):
        # frames = [self.ichi, self.rsi,self.volume, self.df.Target,self.df.Date]
        frames = [self.ichi]
        final_df = pd.concat(frames,axis=1)
        final_df.dropna(inplace=True)
        return final_df
    
    def main(self):
        # self.volume_indicators()
        # self.rsiframe()
        self.ichi_frame()
        # assert len(self.volume) == len(self.ichi)
        self.final= self.concat_frames()
        return self.final

#Shif_t each of them to corresponding columns
#Run the boruta algorithm to eliminate irrelevants
#Save boruta column parameters
#Fit models to log-returns
#Evaluate Score performance
