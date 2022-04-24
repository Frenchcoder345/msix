

import pandas as pd
import numpy as np

import seaborn as sns
import json
import warnings
from sklearn.preprocessing import StandardScaler
from halo import Halo
from log_symbols import LogSymbols
from tqdm import tqdm

scaler = StandardScaler()
warnings.filterwarnings('ignore')
#Load all our dataframes


class Final_frame():
    
    def __init__(self):
        self.data = None
        self.symbols=None
        self.dates = None
        
    def load(self):
        with open('data/tech_indicators_created.json') as json_data:
            data = json.load(json_data)
        return data
    
    def load_csv(self, filename):
        df = pd.read_csv(filename, engine='c', low_memory=True, parse_dates=['date'])
        return df

    def drop_reduce(self,frame, yahoo=True):
        if yahoo is False:
            frame.drop(columns=['fopen','fclose','fhigh','flow'],inplace=True)
            return frame
        else: 
            return frame

    def format_numericals(self,frame):
        #get the log for the float columns
        # frame.iloc[:,-4:] = scaler.fit_transform(np.log(frame.iloc[:,-4:]))
        # frame.loc[:,'volume'] = scaler.fit_transform(np.array(frame.loc[:,'volume']).reshape(-1,1))
        return frame
    
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
    def tournament_data(self, df):
        df = df[df.log_return_20_d.isnull()]
        return df
    
    def final_frame(self):
        frame = pd.DataFrame()
        tournament =pd.DataFrame()
        for i in self.symbols:
            dataframe = pd.DataFrame(self.data[i])
            # dataframe = self.format_numericals(self.drop_reduce(dataframe))
            frame =frame.append(dataframe)
            frame.sort_values('date', ascending=True, inplace=True)
            frame.drop(columns=['std_dev'], inplace=True)
       
        frame['month'] = pd.DatetimeIndex(frame['date']).month
        frame =pd.concat([frame, pd.get_dummies(frame.month,prefix='month'),pd.get_dummies(frame.symbol,prefix='ticker_')], axis=1)
        tournament = tournament.append(self.tournament_data(frame))
        tournament.to_csv('tournament.csv',index=False)
        frame.dropna(subset='log_return_20_d', inplace=True)
        return frame , tournament
    
    def save(self,df):
        # df.drop(columns=['high','low','open','close','volume'],inplace=True, errors='ignore')
        df.to_csv('final_prediction_frame.csv', index=False)
    
    def main(self):
        #Load data
        self.data = self.load_csv('volatility_indicators_test.csv')
        #create symbols for iterations
        self.symbols= list(self.data.bloomberg_ticker.unique())
        #Create a Dataframe with all tickers and data inside
        # frame, tournament = self.final_frame()
        #Get unique dates
        self.dates = list(self.data.date.unique())
        #Do some preprocessing
        frame= self.rank_and_encode(self.data)
        
        #Add quintiles to a new frame
        quint_frame = pd.DataFrame()
        for date in tqdm(self.dates):
            df = self.add_quintile(frame, date)
            quint_frame = quint_frame.append(df)
        return quint_frame
    
if __name__ =="__main__":
    framer = Final_frame()
    
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    df = framer.main()
    df =pd.concat([df, pd.get_dummies(df.bloomberg_ticker,prefix='ticker_')], axis=1)
    # df.drop(columns=['bloomberg_ticker'], inplace=True)
    framer.save(df)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "Prediction Frame was successfully created")
    
# data = load()