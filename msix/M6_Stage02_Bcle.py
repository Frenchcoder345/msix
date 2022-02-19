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
import sys
# adding Thonny/lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')

# Classes et variables globales
from classDef import *


###################################################################
#  Chargement des Tickers
#  Fichier origine avec toutes les valeurs
###################################################################

inputFile = inputFileClass('C:/Users/Ajax/Documents/IA/M6Comp/data/data.csv')
symbols = inputFile.symbols # liste des symboles

# si on interrompt le PG après i-ème ticker, reprise reprise i+1
# symbols=symbols[26:]


###################################################################
#  Boucle sur Ticker
###################################################################

for ticker in symbols:
    startTime = time.time()
    print(ticker)

    # Chargement
    stock1 = serieStock(ticker)

    # Rendement à 20 jours
    stock1.y20d()

    # Chargement des Dtroites
    stock1.readDroitesXLS()
    
    stock1.setStartEstim()
    # 729 = 02 janvier 2020
    # arret calcul 20 jours avant fin fichier
    finEstim = stock1.finOri - 20
    # on calcule tailleEchantillon sur 2 ans ~= 500 jours
    tailleEchantillon = 500    
    # certains tickers (OGN)  n'ont pas 500 obs
    debutEstim = max(stock1.startEstim, stock1.finOri - tailleEchantillon)
   
    for dateOfStudyOri in range(debutEstim,finEstim):
        print(dateOfStudyOri)
        stock1.activeDroites(dateOfStudyOri)
        stock1.hitTrend(dateOfStudyOri)
        stock1.isGoodDroite(dateOfStudyOri)
        stock1.isDeadDroite()
        bestDroite = stock1.bestDroite()
        stock1.valeursIndividuellesPost(bestDroite,dateOfStudyOri)

    stock1.vCPDump()
    stock1.dumpCSVJulien()

    executionTime = (time.time() - startTime)
    print('Execution time in seconds for ' + ticker +': ' + str(executionTime))

###################################################################
#  / Recherche 2eme Creux pour point de départ des calculs
###################################################################


