###################################################################
#  Etape 1
#  1er Git
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

inputFile = 'C:/Users/Ajax/Documents/IA/M6Comp/data/data.csv'
allStocks = pd.read_csv(inputFile, sep=",")

# Quelles valeurs?
dataSymbol = list(allStocks.symbol.unique())

# Découpage par valeur
stock1 = serFromBigFile(allStocks,'AEP')

# Etape longue
stock1.initDateDiff()

# sauvegarde
stock1.dumpExcel()
#stock1.readXLS()


