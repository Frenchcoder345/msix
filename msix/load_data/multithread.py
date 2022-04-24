import pandas as pd
import numpy as np
import requests
import datetime as dt
import time as _time
import random
import os
import glob
from halo import Halo
import time
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--ndays', 
                    required=False,
                    default=500,
                    type=int,
                    help=' please choose from: all, momentum, others, trend,volatility, volume')
parser.add_argument('--name', 
                    required=False,
                    default="Testset",
                    type=str,
                    help='The Filename and path if desired')

parser.add_argument('--today', 
                    required=False,
                    default=True,
                    type=int,
                    help=' please choose from: all, momentum, others, trend,volatility, volume')

parser.add_argument('--ending_date', 
                    required=False,
                    default=True,
                    type=int,
                    help=' please choose from: all, momentum, others, trend,volatility, volume')

parser.add_argument('--ntickers', 
                    required=False,
                    type=int,
                    help=' If you want to test limit the number to the first n tickers')

args = parser.parse_args()
#Users for the Yfinance API usage
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

        tickers = pd.read_csv("competition_files/m6universe.csv")
        tickers = list(tickers.symbol.unique())
        return tickers
    

#Get the dates we want in the module
if args.today == False:
    end = dt.datetime.today() - dt.timedelta(days=args.ending_date)
else:
    end = dt.datetime.today() - dt.timedelta(days=1)
start = dt.datetime.today() - dt.timedelta(days=args.ndays)


from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

#Create our list of tickers after downloading them from numerai
tickers = Universe.get_m6_ticks()
print(tickers)
if args.ntickers is not None:
    tickers = tickers[:args.ntickers]
url_list = [f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}' for ticker in tickers]


start_2 = time()
params= dict(
period1=int(start.timestamp()),
period2=int(end.timestamp()),
interval='1d',
events='div,splits',)

def download_file(url):
    """Basic funtion to request data from the API"""
    data = requests.get(
                    url=url,
                    params=params,
                    headers={'User-Agent': random.choice(USER_AGENTS)}
                )
    return data.json()

print(url_list)
#Create Processes
processes = []
with ThreadPoolExecutor(max_workers=100) as executor:
    for url in tqdm(url_list):
        processes.append(executor.submit(download_file, url))

frame = pd.DataFrame()
n_processes = len(processes)
print(n_processes)
#Deploy multithreads to download the XXXX tickers
for task in tqdm(as_completed(processes)):

    print(task.result()["chart"]["result"][0]["meta"]["symbol"])
    new_frame= pd.DataFrame.from_dict(task.result()["chart"]["result"][0]["indicators"]["quote"][0])
    new_frame['ticker'] = task.result()["chart"]["result"][0]["meta"]["symbol"]
    new_frame['timestamp'] = task.result()["chart"]["result"][0]["timestamp"]
    new_frame['timestamp'] = pd.to_datetime(new_frame['timestamp'], unit="s")
    new_frame['currency'] = task.result()["chart"]["result"][0]['meta']['currency']
    frame = frame.append(new_frame)

    
#Save as parquet file and print basic information
frame.to_parquet(f'{args.name}.parquet',index=False)
print(frame.info())
print(f'Time taken: {round(time() - start_2,2)}')
print("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")

