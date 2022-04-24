import numpy as np
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import optuna
import json
from sklearn.model_selection import train_test_split
import catboost as cb
from sklearn.cluster import KMeans

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
        self.model = joblib.load('msix/models/rank_classifier.joblib')

    def generate_probas(self):
        self.predictions = pd.concat([pd.DataFrame(self.tickers),
                                        pd.DataFrame(self.model.predict_proba(self.data))],
                                        axis=1)
        self.predictions.columns=  ['ID','Rank1','Rank2','Rank3','Rank4','Rank5']
        self.predictions.set_index('ID', inplace=True)
        print(self.predictions)
        print(self.predictions.shape)

    def generate_optimised_weights(self):
        
        #Read Data and transform for readiness for optimisation
        data = pd.read_parquet(self.opt_path)
        data['date'] = data['timestamp'].dt.date
        data = data.loc['01-03-2021':]
        
        opt_data  =data.pivot(index='date', columns='ticker',values='close').fillna(method='backfill')
        
        # Do the efficient portfolio optimisation
        mu = mean_historical_return(opt_data)
        S = CovarianceShrinkage(opt_data).ledoit_wolf()
        ef = EfficientFrontier(mu, S, weight_bounds=(-1,1))
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()
        ef.portfolio_performance(verbose=True)
        
        #Create dataframes with allocations 
        self.allocations = pd.DataFrame(weights, index=[0]).T
        self.allocations.columns= ['Decision']
        assert round(np.sum(list(weights.values())),5) ==1
        
    def split(self):
        try:
            self.target = self.data.quintile
            self.data.drop(columns=['symbol','date','change','month','rank','quintile','log_return_20_d','std_dev'], errors='ignore', inplace=True)
        except: pass
        
    
    def check_performance(self):
        try:
            print(cr(self.target, self.model.predict(self.data)))
        except: pass
        
    def submission_file(self):
        submission = self.predictions.join(self.allocations)
        submission.reset_index(drop=False).to_csv('submission_test1.csv', index=False)

    def main(self):
        self.split()
        self.load_models()
        self.generate_probas()
        self.generate_optimised_weights()
        self.check_performance()
        self.submission_file()
        
if __name__ =='__main__':
    spinner = Halo(text='Loading', spinner='unicorn')
    spinner.start()
    
    
    tour = pd.read_csv('data/tournament/momentum_indicators_tour_1.csv', parse_dates=['date'])
    tour=tour.loc['01-03-2022':]
    tickers = tour.ticker
    #Basic selection & transformation
    X = tour.drop(columns=['era','id','timestamp', 'currency','target','data_type','rank','quintile','log_return_20_d','ticker','date'], errors='ignore')

    #Do Transformations
    scaler = StandardScaler()
    X  =scaler.fit_transform(X)
    X = KMeans(n_clusters=15, random_state=0).fit_transform(X)
    X = PCA(n_components=10).fit_transform(X)

    print(tour)
    # data = datas.drop(columns=['symbol','date','month','rank','quintile','log_return_20_d','std_dev'], errors='ignore')

    path = 'data/raw/may_data.parquet'
    submit = Submitter(X, path, tickers)
    submit.main()
    spinner.stop()