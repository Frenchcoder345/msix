import pandas as pd 
import numpy as np
import requests
from urllib.parse import urljoin
from halo import Halo
from log_symbols import LogSymbols
token = 'sk_87eb7ec4fa3746cfa685f1150a8b1a09'

spinner = Halo(text='Loading', spinner='unicorn')

#This is a sample list of tickers aiming to demonstrated functionality
# iex_list= ['abbv', 'acn', 'aep', 'aiz', 'alle']
assets = pd.read_csv('../competition_files/assets_available.csv')
iex_list = assets.symbol.str.lower().to_list()

class Data_fetch():
    """ This class' purpose is to load data from the IEX console for multiple tickers 
    at once and to concatenate them into a dataframe ready for batch technical analysis"""
    
    def __init__(self,token,iex_list, years):
        self.iex_list = iex_list
        self.token=token
        self.years=years
        self.base= 'https://cloud.iexapis.com/v1/'

    def check_ticker_available(self,ticker):
        params = f'stock/{ticker}/quote?1m&token={self.token}'
        url = urljoin(self.base,params)
        response = requests.get(url)
        return response.status_code

    def get_data_iex(self,ticker):
        params = f'stock/{ticker}/chart/{self.years}y?token={self.token}'
        url = urljoin(self.base,params)
        response = requests.get(url)
        return response.json()

    def arrange_data_in_frame(self,asset_dict):
        prices_frame = pd.concat({k: pd.DataFrame(v) for k, v in asset_dict.items()}, axis=0).iloc[:,1:].reset_index(drop=True)
        prices_frame.drop(columns=[ 'id', 'subkey','updated', 'changeOverTime','key', 'marketChangeOverTime', 'uOpen','uClose', 'uHigh', 'uLow', 'uVolume',  'label'],inplace=True)
        prices_frame.date = pd.to_datetime(prices_frame.date)
        return prices_frame

    def main(self):
        asset_dict= {x:self.get_data_iex(x) for x in self.iex_list}
        df = self.arrange_data_in_frame(asset_dict)
        return df

if __name__ =='__main__':
    spinner.start()    
    fetcher = Data_fetch(token=token, iex_list= iex_list, years=5)
    df = fetcher.main()
    df.to_csv('data.csv', index=False)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "success")
