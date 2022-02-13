###################################################################
#
#  Meme Process que M6_Stage01.py
#  mais Boucle sur toutes les valeurs
#
#
#  Etape 2 - Passer Etape 1 readInit.py avant
#
#  - Identification des droites
#
#  Input : fichiers data/stockXX.xls traités par ReadInit.py
#
#  Output:  fichiers data/stockXX_1.xls
##################################################################

import time
import pandas as pd
#module datetime
import datetime as dt
import sys
# adding IA/M6Comp/lib to the system path pour aller chercher classDef.py
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')
from classDef import *

startTime = time.time()


###################################################################
#  Chargement des Tickers
#  Fichier origine avec toutes les valeurs
###################################################################

inputFile = 'C:/Users/Ajax/Documents/IA/M6Comp/data/dataFull.csv'
allStocks = pd.read_csv(inputFile, sep=",",engine="c",low_memory=True)

# Quelles valeurs?
dataSymbol = allStocks.groupby(allStocks['symbol']).size()
symbols = list(allStocks.symbol.unique())

###################################################################
#  Boucle sur Ticker
###################################################################

for ticker in symbols:
    print(ticker)

    # Chargement
    stock1 = serieStock(ticker)

    # Rendement à 20 jours
    stock1.y20d()
    # plt.hist(stock1.sd['y20d'], bins=10)
    # plt.show()

    ###################################################################
    #  Recherche 2eme Creux pour point de départ des calculs
    ###################################################################

    dateStudy="08.01.2030"
    dfPB = seriePB(stock1.sd,dateStudy)

    # les Creux 35 avant, 20 derriere
    dfPBFlow = dfPB.isCreux(35,20)

    dateSecondCreux = dfPBFlow.loc[1]['date']
    dfStudy = stock1.sd[stock1.sd['date']>dateSecondCreux]
    # listDate= list(dfStudy.date.dt.strftime('%d.%m.%Y').unique())
    listDate= list(stock1.sd.date.dt.strftime('%d.%m.%Y').unique())
    length = len(listDate)

    ###################################################################
    #  / Recherche 2eme Creux pour point de départ des calculs
    ###################################################################

    ###################################################################
    #  on a le point de départ - on peut lancer
    ###################################################################

    lesBestDroite = pd.DataFrame()
    # listDate=(["08.01.2019"])
    # length = len(listDate)


    ###################################################################
    #   Boucle sur les jours
    ###################################################################

    startDateSt = dt.datetime.strptime("01.01.2020", "%d.%m.%Y")
    for i in range(length):
        dateInList = dt.datetime.strptime(listDate[i], "%d.%m.%Y")
    # for i in range(30):
        if i > 20 and dateInList>startDateSt:
            dateStudy = listDate[i]
            print(i, ' ' , listDate[i],' ',dateStudy)
            ###################################################################
            #  Recherche des Creux pour construction Droite support
            ###################################################################
            dfPB = seriePB(stock1.sd,dateStudy)

            # les Creux 40 avant, 20 derriere
            dfPBFlow = dfPB.isCreux(35,20)

            ###################################################################
            #  Identification des Droites support
            ###################################################################

            # toutes les combinaisons
            dfTrend = dfPB.lesDroites(dfPBFlow)

            # la plus récente
            bestDroite = dfPB.lastDroite(dfTrend,stock1)


            # Calcul des deltas
            stock1.delta2T1(bestDroite)
            bestDroite['dateStudy'] = dateStudy
            lesBestDroite = lesBestDroite.append(bestDroite)

    ###################################################################
    #  / Boucle sur les jours
    ###################################################################


    # sauvegarde du stockXX_1.xls
    stock1.dumpExcel()
    stock1.dumpCSVJulien()
    outFileDroites = 'data/' + stock1.stockName + '_Droites.xls'
    lesBestDroite.to_excel(outFileDroites)

###################################################################
#  / Boucle sur Ticker
###################################################################



executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))