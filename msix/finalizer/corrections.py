import pandas as pd
import numpy as np
import datetime as dt


class Last_steps:
    def __init__(self):
        self.preds= None
        self.roundings = 4
        pass
    
    def load(self):
        predictions = pd.read_csv('data/submission/submission_test1.csv')
        preds =predictions.groupby(['index']).mean().reset_index(drop=False)
        self.preds = np.round(preds, self.roundings)
        self.preds.rename(columns={'index':'ID'}, inplace=True)
        return self.preds
    
    def create_sum(self):
        self.preds.iloc[:,1:6] = np.round(self.preds.iloc[:,1:6],self.roundings)
        self.preds['sum'] = self.preds.iloc[:,1:6].sum(axis=1)
        assert self.preds['sum'].nunique() != 1 , "the columns already match the requirements"
        
    @staticmethod
    def check_columns(df, roundings ):
        """Check that all columns sum to 1 when rounded to the fourth digit"""
        return [np.round(x,roundings) == 1 for x in df['sum']] 
        
    def correct_sum(self):
        """Complex function that required a lot of time to code and hopefully will never be used again"""
        self.preds.iloc[:,1:6] = np.round(self.preds.iloc[:,1:6],self.roundings)
        dummy = 1-  self.preds.iloc[:,1:6].sum(axis=1)
        
        #create dummy variable that will set Rank5 column to equalize the differences in the dataset
        self.preds['Rank5'] = self.preds['Rank5']+ dummy
        self.preds['sum'] = self.preds.iloc[:,1:6].sum(axis=1)
        self.preds.iloc[:,1:6]= self.preds.iloc[:,1:6]+(1*10**-5)-(1*10**-5)
        self.preds = np.round(self.preds,self.roundings)
        
        #Recreate the sum column and check that the algorithm hopefully accepts it
        self.preds['sum'] = self.preds.iloc[:,1:6].sum(axis=1)
        assert False not in self.check_columns(self.preds, self.roundings) , 'The columns do not add up to 1'
        
        #Check that the dataframe contains all the required tickers and delete the sum column
        self.preds.dropna(inplace=True)
        assert len(self.preds.index) ==100, "Dataframe has too much data thus is invalid"
        self.preds.drop(columns=['sum'], inplace=True, errors='ignore')
        return self.preds

if __name__ == '__main__':
    stepper = Last_steps()
    stepper.load()
    stepper.create_sum()
    print(stepper.preds)
    df = stepper.correct_sum()
    df.Decision= 0.01
    df.to_csv('data/submission/final_submission.csv', index=False)