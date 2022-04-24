#Importing our Packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import optuna
import json
from sklearn.model_selection import train_test_split
import catboost as cb
from sklearn.cluster import KMeans
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--indicator',
                    type=str,
                    default=1,
                    help='define the indicator that should be used',
                    required=False)
args = parser.parse_args()



#Load and clean
df =  pd.read_csv('data/transformed/final_prediction_frame.csv')
df.replace([np.inf, -np.inf], np.nan, inplace=True)
fcols = df.select_dtypes('float').columns
df[fcols] = df[fcols].astype('float16')
df.dropna(inplace=True)


#Basic selection & transformation
X = df.drop(columns=['era','id','target','data_type','rank','quintile','log_return_20_d','ticker','date'], errors='ignore')
target = df.quintile

#Do Transformations
scaler = StandardScaler()
X  =scaler.fit_transform(X)
X = KMeans(n_clusters=15, random_state=0).fit_transform(X)
X = PCA(n_components=10).fit_transform(X)
print(X.shape)

#Define our custom optimisation function
def RPSscore( reals, predictions):
    score  = np.mean(np.square(np.cumsum(reals)-np.cumsum(predictions)))
    return score

def objective(trial):
    train_x, valid_x, train_y, valid_y = train_test_split(X, target, test_size=0.1)
    param = {
        "objective": trial.suggest_categorical("objective", ["MultiClass", "MultiClassOneVsAll"]),
        "learning_rate": trial.suggest_float("learning_rate",0.001,0.5),
        "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.01, 0.1),
        "depth": trial.suggest_int("depth", 1, 12),
        "iterations": trial.suggest_int("iterations", 500, 1500),
        "boosting_type": trial.suggest_categorical("boosting_type", ["Ordered", "Plain"]),
        "bootstrap_type": trial.suggest_categorical(
            "bootstrap_type", ["Bayesian", "Bernoulli", "MVS"]
        ),
        "used_ram_limit": "4gb",
    }

    if param["bootstrap_type"] == "Bayesian":
        param["bagging_temperature"] = trial.suggest_float("bagging_temperature", 0, 10)
    elif param["bootstrap_type"] == "Bernoulli":
        param["subsample"] = trial.suggest_float("subsample", 0.1, 1)
    gbm = cb.CatBoostClassifier(**param,task_type="CPU", 
                                devices='0:8',
                                 od_type='IncToDec',
                                thread_count=-1 )

    gbm.fit(train_x, train_y, eval_set=[(valid_x, valid_y)], verbose=0,early_stopping_rounds=100, plot=False)
    preds = gbm.predict_proba(valid_x)

    valid_y2 = np.array(pd.get_dummies(valid_y))
    score = RPSscore(valid_y2, preds)
    print(score)
    return score

if __name__ == "__main__":
    optuna.logging.set_verbosity(optuna.logging.INFO)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=20, timeout=6000)

    print("Number of finished trials: {}".format(len(study.trials)))
    print("Best trial:")
    trial = study.best_trial
    print("  Value: {}".format(trial.value))
    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))
        
    # fig = optuna.visualization.plot_optimization_history(study)
    # fig.show()

    with open(f'msix/models/model_parameters{args.indicator}.json', 'w') as fp:
        json.dump(trial.params, fp)
    params = trial.params

    #fit the model with the corresponding parameters
    gbm = cb.CatBoostClassifier(**params,task_type="CPU", 
                                devices='0:8',
                                od_type='IncToDec',
                                thread_count=-1 ,
                            )
    train_x, valid_x, train_y, valid_y = train_test_split(X, target, test_size=0.1)
    gbm.fit(train_x, train_y, eval_set=[(valid_x, valid_y)], verbose=1,early_stopping_rounds=100, plot=False)

    import joblib
    #Save model as joblib for usage
    joblib.dump(gbm, f'rank_classifier{args.indicator}.joblib')