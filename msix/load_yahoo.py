import pandas as pd
import numpy as np
import random
import requests
import datetime as dt
import time as _time
import random
import warnings
warnings.filterwarnings("ignore")
from halo import Halo
import argparse
import time
import os
import glob


parser = argparse.ArgumentParser()
parser.add_argument("--days", help="the number of days of data to download in total",
                    type=int)

parser.add_argument("--splits", help="the total number of splits to perform on the ticker list, default None",
                    type=int, required=False)
args = parser.parse_args()

start = dt.datetime.today() - dt.timedelta(days=args.days)
end = dt.datetime.today() - dt.timedelta(days=1)


USER_AGENTS = [
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/39.0.2171.95 Safari/537.36'
    ),
    (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    )
]


class Universe():

    @staticmethod
    def get_m6_ticks(): 
    #Get current workpath
        path = os.getcwd()
        csv_files = glob.glob("../competition_files/m6universe.csv")
        tickers = pd.read_csv(csv_files[0])
        tickers = list(tickers.symbol.unique())
        return tickers
        
    @staticmethod
    def get_numerai_tickers():
        """get all the currently available tickers in our Numerai universe"""
        napi = numerapi.SignalsAPI()
        napi.ticker_universe()
        return [x for x in napi.ticker_universe()]
    
    @staticmethod
    def get_data(tickers,start,end):
        """Loads all the requested tickers into one big CSV for the specified timeframe"""
        return {str(x):pd.DataFrame(Yahoo.download_ticker(x, start=start,end=end, agent=random.choice(USER_AGENTS))[1]) for x in tickers}

    @staticmethod
    def concat_save(frames,name, save=False):
        """This function iterates over tickers and stores the aggregated result as a csv if specified True otherwise dataframe"""
        concat_frame = pd.DataFrame()

        for key in frames.keys():
            concat_frame = concat_frame.append(frames[key])
        concat_frame.reset_index(drop=True, inplace=True)

        if save == True:
            concat_frame.to_csv(f'yahoodata{str(name)}.csv', index=False)
        else: 
            return concat_frame

    @staticmethod
    def get_tickers():
        """This function helps mapping to yahoo tickers and to return the corresponding, cleaned list"""
        ticker_map = correct_tickers.get_ticker_map()
        universe = pd.Series(Universe.get_numerai_tickers())
        universe.name = 'universe'
        tickers= pd.merge(ticker_map, universe, how='inner', left_on='bloomberg_ticker', right_on='universe')
        ticker_list = tickers.yahoo.dropna().to_list()
        return ticker_list
    
    
#Get the beautifully made code from the Signals guys
class Yahoo():
    """Implementation of a stock data price provider that uses the Yahoo! Finance API"""
    
    
    def download_ticker(ticker: str, start: dt.datetime, end: dt.datetime, agent):
        """dowload data for a given ticker"""
        startTime = time.time()
        spinner = Halo(text='Downloading dataset', spinner='dots')
        spinner.start()
        def empty_df() -> pd.DataFrame:
            return pd.DataFrame(columns=[
                "date", "bloomberg_ticker",
                "open", "high", "low", "close",
                "adj_close", "volume", "currency", "provider"])

        retries = 1
        tries = retries + 1
        backoff = 1
        url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
        user_agent = agent
        params: Dict[str, Union[int, str]] = dict(
            period1=int(start.timestamp()),
            period2=int(end.timestamp()),
            interval='1d',
            events='div,splits',
        )
        # print(f' {ticker}')
        while tries > 0:
            tries -= 1
            
            try:
                data = requests.get(
                    url=url,
                    params=params,
                    headers={'User-Agent': user_agent}
                )
                data_json = data.json()
                quotes = data_json["chart"]["result"][0]
                if "timestamp" not in quotes:
                    return ticker, empty_df()

                timestamps = quotes["timestamp"]
                ohlc = quotes["indicators"]["quote"][0]
                volumes = ohlc["volume"]
                opens = ohlc["open"]
                closes = ohlc["close"]
                lows = ohlc["low"]
                highs = ohlc["high"]

                adjclose = closes
                if "adjclose" in quotes["indicators"]:
                    adjclose = quotes["indicators"]["adjclose"][0]["adjclose"]

                df = pd.DataFrame({
                    "date": pd.to_datetime(timestamps, unit="s").normalize(),
                    "bloomberg_ticker": ticker,
                    "open": np.array(opens, dtype='float32'),
                    "high": np.array(highs, dtype='float32'),
                    "low": np.array(lows, dtype='float32'),
                    "close": np.array(closes, dtype='float32'),
                    "adj_close": np.array(adjclose, dtype='float32'),
                    "volume": np.array(volumes, dtype='float32'),
                    "currency": quotes['meta']['currency'],
                    "provider": 'yahoo'
                })
                executionTime = (time.time() - startTime)
                spinner.stop_and_persist(symbol='🦄'.encode('utf-8'), text=f'This ticker {str(ticker)} took {str(np.round(executionTime,3))} seconds')  
                # print('Execution time in seconds for ' + ticker +': ' + str(np.round(executionTime,3)))                
                return ticker, df.drop_duplicates().dropna()

            except Exception:
                _time.sleep(backoff)
                backoff = min(backoff * 2, 30)
        return ticker, empty_df()

    
if __name__ =="__main__":
    
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    tickers = Universe.get_m6_ticks()
    
    if args.splits is not None:
        splits = args.splits
        arrays = np.array_split(tickers,splits)
        arrays = [list(arrays[i]) for i in range(0,len(arrays))]
        for i in range(0,len(arrays)):
            data = Universe.get_data(arrays[i], start,end)
            data_frame = Universe.concat_save(data,i, save=True)
            spinner.stop_and_persist(symbol='🦄'.encode('utf-8'), text=f'You re such a cool stud and loaded the data for the array {str(i)}')
            time.sleep(60)
    else:
        arrays = tickers
        data = Universe.get_data(arrays, start,end)
        data_frame = Universe.concat_save(data,'full', save=True)
        spinner.stop_and_persist(symbol='🦄'.encode('utf-8'), text='You re such a cool stud and got the tickers')
        spinner.stop()
    
    spinner.stop_and_persist(symbol='🦄'.encode('utf-8'), text='You re such a cool stud and saved the data')
    
    