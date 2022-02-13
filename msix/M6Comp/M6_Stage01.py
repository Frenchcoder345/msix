###################################################################
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
# adding Thonny/lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')
from classDef import *

startTime = time.time()

# Chargement
stock1 = serieStock('XLE')

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

listDate= list(stock1.sd.date.dt.strftime('%d.%m.%Y').unique())
# listDate= list(dfStudy.date.dt.strftime('%d.%m.%Y').unique())
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

startDate = dt.datetime.strptime("01.01.2020", "%d.%m.%Y")
for i in range(length):
    dateInList = dt.datetime.strptime(listDate[i], "%d.%m.%Y")
    # for i in range(30):
    if i > 20 and dateInList>startDate:
        dateStudy = listDate[i]
        print('i ',i, ' ' , listDate[i])
        
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
#  Vectorisation de la droite
###################################################################

# dateDeb = dt.datetime.strptime("2019-01-04", "%Y-%m-%d")
# valDeb = 64.8702
# dateFin = dt.datetime.strptime("2019-11-12", "%Y-%m-%d")
# valFin = 81.7050
# 
# 
# dTest = droiteTrend(dateDeb, valDeb, dateFin, valFin)
# dTest.coeff()
# print(dTest.isHit(stock1,"09.01.2020"))



# # Definition point de base d une parallèle
# dateAncrage = dt.datetime.strptime("29.10.2020", "%d.%m.%Y")
# valAncrage = 74.71
# pointAncrage1 = ancrage(dateAncrage,valAncrage)
# # Calcul du b
# pointAncrage1.calculB(d1.a,dateOrigine)
# 
# # Prevision à datePrev
# datePrev = dt.datetime.strptime("20.09.2021", "%d.%m.%Y")
# nbDatePrev = calculDateDiff(dateOrigine,datePrev)
# valPrev = d1.a*nbDatePrev+pointAncrage1.bAncrage
# #print(valPrev)


# sauvegarde du stockXX_1.xls
stock1.dumpExcel()
stock1.dumpCSVJulien()
outFileDroites = 'data/' + stock1.stockName + '_Droites.xls'
lesBestDroite.to_excel(outFileDroites)
#####your python script#####


executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))