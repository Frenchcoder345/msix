"""
Optuna example that optimizes a classifier configuration for cancer dataset using
Catboost.
In this example, we optimize the validation accuracy of cancer detection using
Catboost. We optimize both the choice of booster model and their hyperparameters.
"""

import numpy as np
import optuna
import pandas as pd
import catboost as cb
import json
from sklearn.model_selection import train_test_split


# datas = pd.read_csv('data/transformed/final_prediction_frame.csv')


#Define our custom optimisation function
def RPSscore( reals, predictions):
    score  = np.mean(np.square(np.cumsum(reals)-np.cumsum(predictions)))
    return score

# data = datas.drop(columns=['symbol','date','month','rank','quintile'])
# target = datas.quintile

def objective(trial):
    train_x, valid_x, train_y, valid_y = train_test_split(data, target, test_size=0.3)
    

    param = {
        "objective": trial.suggest_categorical("objective", ["MultiClass", "MultiClassOneVsAll"]),
        "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.01, 0.1),
        "depth": trial.suggest_int("depth", 1, 12),
        "iterations": trial.suggest_int("iterations", 1000, 4000),
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
    return score

if __name__ == "__main__":
    optuna.logging.set_verbosity(optuna.logging.INFO)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=15, timeout=600)

    print("Number of finished trials: {}".format(len(study.trials)))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: {}".format(trial.value))

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))
        
    fig = optuna.visualization.plot_optimization_history(study)
    fig.show()

    with open(f'model_parameters.json', 'w') as fp:
        json.dump(trial.params, fp)
