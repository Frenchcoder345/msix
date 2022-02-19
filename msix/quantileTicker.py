###################################################################
#  Etape 3 - Passer Etape 2 M6_Stage02_Bcle.py avant
#            pout produire les indicateurs
#
#
#  Input : - Liste des tickers
#            C:/Users/Ajax/Documents/IA/M6Comp/data/tickerList.csv
#          - Indicateurs des tickers
#            C:/Users/Ajax/Documents/IA/M6Comp/data/csv/'+ ticker + '_1.csv
#
#             ,symbol,date,prevDeltaPost
#          ...
#          758,ACN,2020-02-18,0.0
#          759,ACN,2020-02-19,0.123946788253531
#          760,ACN,2020-02-20,0.1087941402267405
#          ...
#
#  Output:  pour chaque jour 2020 & 2021,
#           chaque ticker classé dans son 5-ile de mon indicateur 
#            C:\Users\Ajax\Documents\IA\M6Comp\features\tickerCat.csv
#
##################################################################

import time
import sys
# adding Thonny/lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')
from classDef import *

inputFileTicker = 'C:/Users/Ajax/Documents/IA/M6Comp/data/tickerList.csv'
dfTicker = pd.read_csv(inputFileTicker, sep=",",engine="c",low_memory=True, names = ['symbol'])

symbols = list(dfTicker.symbol.unique())
# symbols = symbols[:26]

deltaJoin = pd.DataFrame()

for ticker in symbols:
    inputFileDelta = 'C:/Users/Ajax/Documents/IA/M6Comp/data/csv/'+ ticker + '_1.csv'
    delta = pd.read_csv(inputFileDelta, sep=",", engine="c",low_memory=True, index_col=[0])
    delta.rename(columns = {'prevDeltaPost': ticker}, inplace = True)
    delta.date = pd.to_datetime(delta.date, format="%Y-%m-%d")
    delta.set_index('date', inplace = True)
    delta = delta.drop('symbol', axis = 1)
    delta = delta[delta[ticker] != 0]
    deltaJoin = deltaJoin.join(delta, how='outer')


deltaT = deltaJoin.transpose()

dateList = deltaT.columns.tolist()

deltaCat = pd.DataFrame()

for jourCotation in dateList:
    if deltaT[jourCotation].isna().sum() < 10:
        df0 = pd.qcut(deltaT[jourCotation], 5, labels = ['1','2','3','4','5'], duplicates = 'drop')

        listIndex = df0.index
        listCat = df0.to_list()
        dfCat0 = pd.DataFrame(list(zip(listIndex, listCat)), columns =['index', df0.name])
        dfCat0.set_index('index', inplace = True)
        deltaCat = deltaCat.join(dfCat0, how='outer')


deltaFinal = deltaCat.transpose()

csvFile = 'C:/Users/Ajax/Documents/IA/M6Comp/features/tickerCat.csv'
deltaFinal.to_csv(csvFile)


