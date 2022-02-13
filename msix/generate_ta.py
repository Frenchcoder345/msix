
import pandas as pd
import numpy as np

import json
import warnings
# from indicators.ichimoku_cloud import IchimokuIndicator
from msix.indicators.formatter import Formatter
from halo import Halo
from log_symbols import LogSymbols
warnings.filterwarnings('ignore')


class Technical_indicators(Formatter):
    """This class is freely editable and is supposed to create the technical indicators used to forecast the final target"""
    def __init__(self,symbols):
        self.price_dict=None
        self.formatter = None
        self.symbols = symbols
        self.data = None
        pass
    
    def load(self):
        """Load the data as json because multiple frames at once"""
        with open('data/data_target_created.json') as json_data:
            data = json.load(json_data)
        self.data =data
        return data
    def create_indicators(self, ticker):
        """We use the formatter module to create our final dataframe - the specifics are in indicators.formatter"""
        frame = pd.DataFrame(self.data[ticker])
        self.formatter = Formatter(frame)
        ichiframe = self.formatter.main()
        ichiframe = pd.concat([frame,ichiframe], axis=1).dropna()
        return ichiframe
    
    def transform_frames(self, data):
        """The dataframes are returned into their final dict with the corresponding ticker assigned"""
        #self.price_dict = {symbols[k]: df[df.symbol ==symbols[k]] for k in range(0,len(symbols))}
        self.price_dict = {self.symbols[k]: self.create_indicators(self.symbols[k]).to_dict('records') for k in range(0,len(data.keys())) }
        return self.price_dict
    
    def save(self):
        """We save a local copy of the data for checkpoint purposes and further usage"""
        with open('data/tech_indicators_created.json', 'w') as fp:
            json.dump(self.price_dict, fp)        

if __name__ == '__main__':
    
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    transformer = Technical_indicators()
    data = transformer.load()
    symbols= list(data.keys())
    transformer.transform_frames(data)
    transformer.save()
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "Technical indicators created successfully")