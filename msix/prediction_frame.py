

import pandas as pd
import numpy as np

import seaborn as sns
import json
import warnings
from sklearn.preprocessing import StandardScaler
from halo import Halo
from log_symbols import LogSymbols

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

    def drop_reduce(self,frame):
        frame.drop(columns=['fopen','fclose','fhigh','flow'],inplace=True)
        return frame

    def format_numericals(self,frame):
        #get the log for the float columns
        frame.iloc[:,-4:] = scaler.fit_transform(np.log(frame.iloc[:,-4:]))
        frame.loc[:,'fvolume'] = scaler.fit_transform(np.array(frame.loc[:,'fvolume']).reshape(-1,1))
        return frame
    
    def rank_and_encode(self,final_frame):
        #Create the rank values
        final_frame['rank'] = final_frame.groupby(['date'])['log_return_20_d'].rank(method='first')
        final_frame['rank']= final_frame['rank'].astype(int)
        final_frame['month'] = pd.DatetimeIndex(final_frame['date']).month
        final_frame = final_frame.sort_values('date', ascending=False)

        #Create dataframe with ranks for each day
        final_frame  =pd.concat([final_frame, pd.get_dummies(final_frame.month,prefix='month'),pd.get_dummies(final_frame.symbol,prefix='ticker_')], axis=1)
        return final_frame

    def add_quintile(self, df, date):
        """Function to create quintiles for the ranks / targets"""
        df = df[df.date == date]
        df['quintile'] = pd.qcut(df[df.date == date].log_return_20_d,5,labels=False)+1
        return df
    
    def final_frame(self):
        frame = pd.DataFrame()
        for i in self.symbols:
            dataframe = pd.DataFrame(self.data[i])
            dataframe = self.format_numericals(self.drop_reduce(dataframe))
            frame =frame.append(dataframe)
            frame.sort_values('date', ascending=False, inplace=True)
        return frame
    
    def save(self,df):
        df.to_csv('data/final_prediction_frame.csv', index=False)
    
    def main(self):
        #Load data
        self.data = self.load()
        #create symbols for iterations
        self.symbols= list(self.data.keys())
        #Create a Dataframe with all tickers and data inside
        frame = self.final_frame()
        #Get unique dates
        self.dates = list(frame.date.unique())
        #Do some preprocessing
        frame= self.rank_and_encode(frame)
        
        #Add quintiles to a new frame
        quint_frame = pd.DataFrame()
        for date in self.dates:
            df = self.add_quintile(frame, date)
            quint_frame = quint_frame.append(df)
        return quint_frame
    
if __name__ =="__main__":
    framer = Final_frame()
    
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    df = framer.main()
    framer.save(df)
    spinner.stop()
    print(LogSymbols.SUCCESS.value, "Prediction Frame was successfully created")
    
# data = load()