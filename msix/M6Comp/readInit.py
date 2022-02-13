###################################################################
#  Etape 1
#
#  - Chargement du gros fichier avec tous les cours
#  - Découpage par valeur
#  - Calcul DateDiff
#
#  Input : data.csv
#
#  Output:  1 fichier par valeur  = STOCK.xls
##################################################################

import pandas as pd
#module datetime
import datetime as dt

import sys
# adding Thonny/lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')

from classDef import *

###################################################################
#  Chargement des données
###################################################################

inputFile = 'C:/Users/Ajax/Documents/IA/M6Comp/data/dataFull.csv'
allStocks = pd.read_csv(inputFile, sep=",",engine="c",low_memory=True)

# Quelles valeurs?
dataSymbol = allStocks.groupby(allStocks['symbol']).size()
symbols = list(allStocks.symbol.unique())

# Découpage par valeur
# stock1 = serFromBigFile(allStocks,'AEP')

#symbols = list(['XLE','XLY','XLI','XLC','XLU','XLP','XLB','VXX'])
#symbols = list(['AEP'])

for ticker in symbols:
    print(ticker)
    # Découpage par valeur
    stock1 = serFromBigFile(allStocks,ticker)
    # Etape longue
    stock1.initDateDiff()

    # sauvegarde
    stock1.dumpExcel()
    #stock1.readXLS()

    
# Etape longue
# stock1.initDateDiff()

# sauvegarde
# stock1.dumpExcel()
#stock1.readXLS()


