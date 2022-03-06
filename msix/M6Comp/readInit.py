###################################################################
#  Etape 1
#
#  - Chargement du gros fichier avec tous les cours
#  - Découpage par valeur
#  - Production du premier input = Droites
#
#  Input : data.csv
#
#  Output:  1 fichier par valeur  = STOCK.xls
##################################################################

import sys
# adding /lib to the system path
sys.path.insert(0, '/Users/Ajax/Documents/IA/M6Comp/lib')

# Classes et variables globales
from lib.classDef import *


###################################################################
#  Chargement des données
###################################################################

inputFile = inputFileClass('data/raw/data.csv')
symbols = inputFile.symbols # liste des symboles
# inputFile.dumpSymbols2CSV() # sauvegarde liste pour usage ultérieur

# #symbols = list(['XLE','XLY','XLI','XLC','XLU','XLP','XLB','VXX'])
#symbols = list(['ABBV','ACN'])


final_frame = pd.DataFrame()

for ticker in symbols:
    
    
    print(ticker)
    ####################################################
    # 1ère Etape : Découpage par valeur
    ####################################################

    # stock1 = serFromBigFile(inputFile.allStocks, ticker)
    # sauvegarde dans ticker.xls
    # stock1.dumpExcel()
    
    ####################################################
    # 2ème étape : Production des droites
    ####################################################
    
    # Re-Chargement du fichier source données Excel
    stock1 = serieStock(inputFile.allStocks, ticker)


    # les Creux = minimum de  horizonAnte  avant et  horizonPost  derriere
    dfPBFlow = stock1.isCreux(horizonAnte, horizonPost)

    ###################################################################
    #  Identification des Droites 
    ###################################################################
    # on passe dfPBFlow -> toutes les combinaisons de supports 
    # on passe dfPBHigh -> toutes les combinaisons de résistances 

    dfTrend = stock1.calculLesDroites(dfPBFlow, horizonPost)
    dfTrend['symbol'] = ticker
    final_frame = final_frame.append(dfTrend)

final_frame.columns=[['date','valDeb','dateFin','valFin','indexDeb','indexFin','activDateFromOri','indexDroite','a','b','symbol']]
    

final_frame.to_csv('msix/M6Comp/data/csv/first_transform.csv', index=False)
    # sauvegarde dans ticker_dtes.xls
    # stock1.dumpDroites2Excel()
    
    # FIN 2ème étape
    


