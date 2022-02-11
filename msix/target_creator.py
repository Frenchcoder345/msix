import pandas as pd 
import numpy as np
import warnings
from halo import Halo
import json
from log_symbols import LogSymbols

warnings.filterwarnings('ignore')


class target_creator():
    
    def __init__(self):
        self.df = None
        self.days =20
        self.price_dict = None

    def create_target(self,df):
        df['log_return_20_d']= np.log(df['fclose']/df['fclose'].shift(self.days))
        df = df.dropna()
        df.reset_index(drop=True, inplace=True)
        return df

    def transform_frames(self, df):
        self.price_dict = {symbols[k]: df[df.symbol ==symbols[k]] for k in range(0,len(symbols))}
        self.price_dict = {symbols[k]: self.create_target(self.price_dict[symbols[k]]).to_dict(orient='records') for k in range(0,len(symbols))}
        return self.price_dict

    def main(self,df):
        frame = self.transform_frames(df)
        with open('../data/data_target_created.json', 'w') as fp:
            json.dump(frame, fp)
 
if __name__ =='__main__':
    df = pd.read_csv('../data/data.csv')
    df.columns = df.columns.str.lower()
    spinner = Halo(text='Loading', spinner='unicorn')

    spinner.start()
    df.drop(columns=['high','low','open','volume','change','changepercent'], inplace=True)
    symbols= list(df.symbol.unique())
    targeter = target_creator()
    targeter.main(df)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "success")
    
