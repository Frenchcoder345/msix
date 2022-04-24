import pandas as pd
import warnings
from transformers import Transformer
from tqdm import tqdm
import argparse
import warnings
import numpy as np
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()

# dict of all ta functions that are native to the ta package
FUNCTION_MAP = {'all': Transformer.all_indicators,
 'momentum': Transformer.momentum_indicators,
 'others': Transformer.other_indicators,
 'trend': Transformer.trend_indicators,
 'volatility': Transformer.volatility_indicators,
 'volume': Transformer.volume_indicators}

#Declare arguments
parser.add_argument('--command', choices=FUNCTION_MAP.keys(),
                    required=True,
                    type=str,
                    help=' please choose from: all, momentum, others, trend,volatility, volume')

parser.add_argument('--lags',
                    type=int,
                    default=25,
                    help='number of shifts to apply',
                    required=True)

parser.add_argument('--startticker',
                    type=int,
                    help='the first ticker to transform in the list of tickers',
                    required=False)

parser.add_argument('--endticker',
                    type=int,
                    help='the last ticker to transform in the list of tickers',
                    required=False)

parser.add_argument('--name',
                    type=str,
                    default=1,
                    help='to append the file name if looped',
                    required=False)
args = parser.parse_args()

class Optimiser:
    
    def __init__(self):
        pass
    
    @staticmethod
    def optimise_frame(df):
        """For our yahoo dataset, this function optimises the total memory used in pandas"""
        df.drop(columns=['open', 'close', 'high', 'low', 'provider','volume'], inplace=True, errors='ignore')
        fcols = df.select_dtypes('float').columns
        df[fcols] = df[fcols].astype('float16')
        return df
    
    def grouper(self, df, ticker_col, ticker_name):
        """Segregate dataframes into ticker based chunks"""
        grouped = df.groupby([str(ticker_col)])
        one_frame = grouped.get_group(str(ticker_name))
        return one_frame
    
    def shifter(self,df, column, done=True):
        """The shifter shifts a specific column and adds it to the dataframe with the prefix 'FEATURE' to it"""
        df.rename(columns={column: f"FEATURE_{column}_shift0"}, inplace=True)
        for x in range(0,shifts):
            df[f'FEATURE_{column}_shift'+str(x+1)] = df[f"FEATURE_{column}_shift0"].shift(x)
        df.dropna(inplace=done)
        return df
    
if __name__ == '__main__':

    #Load data
    df =pd.read_parquet('data/raw/may_data.parquet')
    df['date'] = pd.to_datetime(df['timestamp'], unit="d")
    print(df.head(10))
    print(df.dtypes)
  
    #Declare the variables that will be required later       
    shifts = args.lags
    func = FUNCTION_MAP[args.command]
    
    print("data is loaded 🔥 ")
    tickers = list(df.ticker.unique())
    training = pd.DataFrame()
    tournament = pd.DataFrame()
    
    #initiate the loop that will iterate through the tickers / dataframe
    for i in tqdm(tickers[args.startticker:args.endticker]):
        #Create a final frame with the transformed tickers
        trans = Optimiser()
        optimised = trans.grouper(df,'ticker',i)
        # optimised['target'] = optimised.close.shift(-20)
        optimised['log_return_20_d']= np.log(optimised['close']/optimised['close'].shift(-20))
        #This is where the magic happens
        try:
            func(optimised)
        except:pass
        
        optimised = trans.optimise_frame(optimised)
        

        if args.command == 'trend':
            for i in optimised.columns[5:]:
                optimised = trans.shifter(optimised, i, done=False)
            tourn = optimised[optimised['log_return_20_d'].isna()]
            optimised.dropna(subset=['log_return_20_d'], inplace=True)
            training = training.append(optimised)
            tournament = tournament.append(tourn)
            
        else:
            for i in optimised.columns[5:]:
                optimised = trans.shifter(optimised, i, done=False)
            tourn = optimised[optimised['log_return_20_d'].isna()]
            optimised.dropna(subset=['log_return_20_d'], inplace=True)
            training = training.append(optimised)
            tournament = tournament.append(tourn)
            
    # Finalize the dataframe and save feature dataset        
    training.drop(columns=['adj_close', 'currency', 'timestamp'], inplace=True, errors='ignore')
    print("....................Training frame looks as follows.......................")
    training.info()
    print("....................Tournament frame looks as follows.....................")
    tournament.info()
    training.to_csv(f'data/transformed/{str(func.__name__)}_features_{str(args.name)}.csv', index=False)
    training.to_parquet(f'data/transformed/{str(func.__name__)}_features_{str(args.name)}.parquet',engine='fastparquet', index=False)
    tournament.to_parquet(f'data/tournament/{str(func.__name__)}_tour_{str(args.name)}.parquet',engine='fastparquet', index=False)
    tournament.to_csv(f'data/tournament/{str(func.__name__)}_tour_{str(args.name)}.csv', index=False)


    