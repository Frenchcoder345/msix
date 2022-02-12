###################################################################
#  Etape 2 - Passer Etape 1 readInit.py avant
#
#  - Identification des droites
#
#  Input : fichiers data/stockXX.xls traités par ReadInit.py
#
#  Output:  fichiers data/stockXX_1.xls
##################################################################

import pandas as pd
#module datetime
import datetime as dt
import sys
# adding Thonny/lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')
from classDef import *


# Chargement
stock1 = serieStock('AEP')

# Rendement à 20 jours
stock1.y20d()
# plt.hist(stock1.sd['y20d'], bins=10)
# plt.show()

###################################################################
#  Recherche des Creux pour construction Droite support
###################################################################
dfPB = seriePB(stock1.sd,"30.01.2022")

# les Creux 40 avant, 20 derriere
dfPBFlow = dfPB.isCreux(40,20)

###################################################################
#  Identification des Droites support
###################################################################

# toutes les combinaisons
dfTrend = dfPB.lesDroites(dfPBFlow)

# la plus récente
bestDroite = dfPB.lastDroite(dfTrend,stock1)


# Calcul des deltas
stock1.delta2T1(bestDroite)


###################################################################
#  Vectorisation de la droite
###################################################################

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