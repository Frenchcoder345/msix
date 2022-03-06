
#Load the required packages
import pandas as pd
import numpy as np
from msix.target_creator import Target_creator
from msix.generate_ta import Technical_indicators
from msix.prediction_frame import Final_frame
from msix.submissions import Submitter
import glob
# All files and directories ending with .txt and that don't begin with a dot:
raw_path = glob.glob("data/raw/yahoodatafull.csv")[0]
print(raw_path)
def RPSscore( reals, predictions):
    score  = np.mean(np.square(np.cumsum(reals)-np.cumsum(predictions)))
    return score

#Load the latest data
df = pd.read_csv(raw_path)
df.columns = df.columns.str.lower()
df.rename(columns={"bloomberg_ticker": "symbol"}, inplace=True)

#Get the list of tickers
symbols= list(df.symbol.unique())

df = df.sort_values(by='date', ascending=True)
# df = df.iloc[-40000:,:]

#Create the target
targeter = Target_creator(symbols)
targeter.main(df)

#Add technical indicators
transformer = Technical_indicators(symbols)
data = transformer.load()
transformer.transform_frames(data)
transformer.save()

#Preprocess for model
framer = Final_frame()
df = framer.main()
framer.save(df)

#predict and check performance
data =  pd.read_csv('data/final_prediction_frame.csv')
data = data[data['date']== max(data['date'])]
submit = Submitter(data, raw_path, symbols)
submit.main()

#Get RPS score
print(RPSscore(np.array(pd.get_dummies(submit.target)),np.array(submit.predictions)))

