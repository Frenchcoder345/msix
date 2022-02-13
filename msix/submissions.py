import numpy as np
import pandas as pd

from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
import joblib
import json
import warnings
from halo import Halo
from log_symbols import LogSymbols
warnings.filterwarnings('ignore')


datas = pd.read_csv('../data/final_prediction_frame.csv')
datas = datas[datas['date']== max(datas['date'])]
data = datas.drop(columns=['symbol','date','month','rank','quintile','log_return_20_d','std_dev'])

tickers = datas['symbol']

path = '../data/data.csv'

class Submitter():
    def __init__(self,data, path, tickers):
        self.model = None
        self.tickers = tickers
        self.data = data
        self.opt_path = path
        self.predictions = None
        self.allocations = None
        pass
    
    def load_models(self):
        self.model = joblib.load('models/rank_classifier.joblib')

    def generate_probas(self):
        global datas
        self.predictions = pd.concat([pd.DataFrame(self.tickers),
                                        pd.DataFrame(self.model.predict_proba(self.data))],
                                        axis=1)
        self.predictions.columns=  ['symbol','quintile_1','quintile_2','quintile_3','quintile_4','quintile_5']
        self.predictions.set_index('symbol', inplace=True)

    def generate_optimised_weights(self):
        
        #Read Data and transform for readiness for optimisation
        data = pd.read_csv(self.opt_path)
        opt_data  =data.pivot(index='date', columns='symbol',values='fClose').fillna(method='backfill')
        
        # Do the efficient portfolio optimisation
        mu = mean_historical_return(opt_data)
        S = CovarianceShrinkage(opt_data).ledoit_wolf()
        ef = EfficientFrontier(mu, S, weight_bounds=(-1,1))
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()
        ef.portfolio_performance(verbose=True)
        
        #Create dataframes with allocations 
        self.allocations = pd.DataFrame(weights, index=[0]).T
        self.allocations.columns= ['weight']
        assert round(np.sum(list(weights.values())),5) ==1


    def submission_file(self):
        submission = self.predictions.join(self.allocations)
        submission.reset_index(drop=False).to_csv('submission_test1.csv', index=False)

    def main(self):
        self.load_models()
        self.generate_probas()
        self.generate_optimised_weights()
        self.submission_file()
        
if __name__ =='__main__':
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    submit = Submitter(data, path, tickers)
    submit.main()
    spinner.stop()