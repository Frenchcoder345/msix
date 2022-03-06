import pandas as pd 
import numpy as np
import warnings
from halo import Halo
import json
from log_symbols import LogSymbols
import argparse
warnings.filterwarnings('ignore')

# parser = argparse.ArgumentParser()
# parser.add_argument("--source", help="the dataprovider to be used for sourcing the data",
#                     type=str)

# parser.add_argument("--splits", help="the total number of splits to perform on the ticker list, default None",
#                     type=int, required=False)
# args = parser.parse_args()



class Target_creator():
    
    def __init__(self, symbols):
        self.df = None
        self.days =20
        self.price_dict = None
        self.symbols = symbols
        
    def create_yahoo_target(self,df):
        """Adjust the objects creator function for the yahoo datasets"""
        df['log_return_20_d']= np.log(df['close']/df['close'].shift(self.days))
        df['std_dev']= df['log_return_20_d'].rolling(20).std()
        df.drop(columns=['adj_close','currency','provider'], inplace=True)
       
        df = df.dropna()
        df.reset_index(drop=True, inplace=True)
        return df
        
    def create_target(self,df):
        """Create the target based on the IEX - Cloud data provided"""
        df['log_return_20_d']= np.log(df['fclose']/df['fclose'].shift(self.days))
        df['std_dev']= df['changepercent'].rolling(20).std()
        df.drop(columns=['changepercent'], inplace=True)
        df = df.dropna()
        df.reset_index(drop=True, inplace=True)
        return df

    def transform_frames(self, df):
        self.price_dict = {self.symbols[k]: df[df.symbol ==self.symbols[k]] for k in range(0,len(self.symbols))}
        self.price_dict = {self.symbols[k]: self.create_yahoo_target(self.price_dict[self.symbols[k]]).to_dict(orient='records') for k in range(0,len(self.symbols))}
        return self.price_dict

    def main(self,df):
        frame = self.transform_frames(df)
        with open('data/data_target_created.json', 'w') as fp:
            json.dump(frame, fp)
 
if __name__ =='__main__':
    df = pd.read_csv('../data/raw/yahoodatafull.csv')
    df.columns = df.columns.str.lower()
    print(df.columns)
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    df.rename(columns={"bloomberg_ticker": "symbol"}, inplace=True)
    # df.drop(columns=['high','low','open','volume'], inplace=True)
    symbols= list(df.symbol.unique())
    targeter = Target_creator(symbols)
    targeter.main(df)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "Dataframe targets successfully created")
    
    
    
