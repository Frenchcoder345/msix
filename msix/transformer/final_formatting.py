

import pandas as pd
import numpy as np

import seaborn as sns
import json
import warnings
from sklearn.preprocessing import StandardScaler
from halo import Halo
from log_symbols import LogSymbols
from tqdm import tqdm
import argparse 


parser = argparse.ArgumentParser()
parser.add_argument('--indicator',
                    type=str,
                    default=1,
                    help='define the indicator that should be used',
                    required=False)
args = parser.parse_args()


warnings.filterwarnings('ignore')

class Final_frame():
    def __init__(self): 
        pass
    
    def rank_and_encode(self,final_frame):
        #Create the rank values
        final_frame['rank'] = final_frame.groupby(['date'])['log_return_20_d'].rank(method='first')
        final_frame['rank']= final_frame['rank'].astype(int)
        return final_frame

    def add_quintile(self, df, date):
        """Function to create quintiles for the ranks / targets"""
        df = df[df.date == date]
        df['quintile'] = pd.qcut(df[df.date == date].log_return_20_d,5,labels=False, duplicates='drop')+1
        return df
    
    def main(self):
        #Load data
        self.data = pd.read_parquet(f'data/transformed/{str(args.indicator)}_indicators_features_1.parquet')
        #create symbols for iterations
        self.symbols= list(self.data.ticker.unique())
        #Create a Dataframe with all tickers and data inside

        #Get unique dates
        self.data['date']= self.data['date'].map(pd.Timestamp.date)
        self.dates = list(self.data['date'].unique())

        #Do some preprocessing
        frame= self.rank_and_encode(self.data)
        
        #Add quintiles to a new frame
        quint_frame = pd.DataFrame()
        for date in tqdm(self.dates):
            df = self.add_quintile(frame, date)
            quint_frame = quint_frame.append(df)
        return quint_frame
    
    def save(self,df):
        df.to_csv(f'data/transformed/final_prediction_frame{args.indicator}.csv', index=False)
    
if __name__ =="__main__":
    framer = Final_frame()
    df = pd.read_parquet(f'data/transformed/{args.indicator}_indicators_features_1.parquet',engine='fastparquet', index=False)
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    df =pd.concat([df, pd.get_dummies(df.ticker,prefix='ticker_')], axis=1)
    df = framer.main()
    framer.save(df)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "Prediction Frame was successfully created")
    