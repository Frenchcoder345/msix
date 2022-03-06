import pandas as pd
from datetime import timedelta
import datetime as dt
import time
import numpy as np

#################################################################
#
# Enchainenemt: 1. readInit.py
#               2. M6_Stage02_Bcle.py
#               3. quantileTicker.py
#
#################################################################



#################################################################
# variables globales
#
#  |              \                   |
#  |               \  /               | 
#  |  horizonAnte   \/   horizonPost  |
#
#  pour identification des creux    
#  pas de calcul possible ecart Droite/Cours avant (horizonPost + 1)

horizonPost = 20  
horizonAnte = 20
#################################################################


#############################################################################
#
#  Class inputFile : lecture fichier source des données
#                    extraction de liste des ticker
#
#  Input           : data/data.csv tous les cours
#                    
#
#############################################################################

class inputFileClass:
    def __init__(self,inputFile):
        self.inputFile = inputFile
        self.allStocks = pd.read_csv(inputFile, sep=",",engine="c",low_memory=True)

        # Quelles valeurs?
        self.dataSymbol = self.allStocks.groupby(self.allStocks['symbol']).size()
        self.symbols = list(self.allStocks.symbol.unique())


    def dumpSymbols2CSV(self):
        csvFile = 'data/tickerList.csv'
        df = pd.DataFrame(self.symbols)
        df.to_csv(csvFile, index=False, header=False)    


#############################################################################
#
#  Class serFromBigFile : traitement pour découpage du fichier initial
#                         et operations longues
#
#  Input           : data/data.csv tous les cours
#                     stockName, filtre sur code stock
#
#############################################################################

class serFromBigFile:
    def __init__(self, allData, stockName):
        self.stockName = stockName
        # read text file into pandas DataFrame
        self.sdOri = allData[allData['symbol']==stockName]
        #self.sdOri.drop(['high','low','open'], axis=1,inplace=True)
        self.sdOri.date = pd.to_datetime(self.sdOri.date, format="%Y-%m-%d")
        self.sdOri = self.sdOri.reindex()
        

    def dumpExcel(self):
        xlsFile = 'data/' + self.stockName + '.xls'
        self.sdOri.to_excel(xlsFile, index=False)
    
       
    def readXLS(self):
        xlsFile = 'data/' + self.stockName + '.xls'
        self.sdOri = pd.read_excel(xlsFile)
     
    # Rendement à 20 jours 
    def y20d(self):
        self.sdOri['c20'] = self.sdOri['fClose'].shift(-20)
        self.sdOri.dropna(inplace=True)
        self.sdOri['y20d'] = self.sdOri['c20']/self.sdOri['fClose'] - 1

#############################################################################
#  END - Class serFromBigFile
#############################################################################


#############################################################################
#
#  Class serieStock : pour les cotations d'un seul actif
#
#  Attributs: - serieStock.de -> DF des données
#             - MetaDonnées de la série
#
#  Input           : data/ticker.xls
#                    
#############################################################################

class serieStock(serFromBigFile):
    # # chargement du xls prétraité par readinit.py 
    # def __init__():
    #     super(serieStock).__init__()
    #     pass
    
    def main(self):   
        # self.stockName = stockName
        # xlsFile = 'data/' + self.stockName + '.xls'
        # self.sdOri = pd.read_excel(xlsFile)
        # self.sdOri.date = pd.to_datetime(self.sdOri.date, format="%Y-%m-%d")
        # init pour les valeurs calculée
        self.sdOri['prevDroiteActive'] = 1
        self.sdOri['deltaDroiteActive'] = 0
        # range de la série
        self.dateDebut = self.sdOri['date'].min()
        self.dateFin = self.sdOri['date'].max()
#         self.debOri  = calculDateDiff(dateOriConst, self.dateDebut)
        self.finOri  = self.sdOri.shape[0]
        # toutes les dates de la série
        self.listDate= list(self.sdOri.date.dt.strftime('%d.%m.%Y').unique())
        # pour introduire un cliquet
        self.startCalculate = 0
        # init
        self.sdOri['prevTrendPost'] = 0
        self.sdOri['prevDeltaPost'] = 0
        self.sdOri['indexDroite'] = 0



    ##################################################################
    # activeDroites : sous ensemble des droites actives au jour de l etude
    #                 filtre sur: - dateOfStudyOri
    #                 
    ##################################################################

    def activeDroites(self, dateOfStudyOri):
        self.dfTrend['isActiv'] = np.where(self.dfTrend['activDateFromOri'] <= dateOfStudyOri,True,False)


    ##################################################################
    # bestDroite : identifier la meilleure droite
    #
    # Critères de départ: - Droite coupée le moins de fois
    #                     - Droite la plus récente
    #                     - Droite avec coeff a le plus fort
    #
    #                     HyperParamètres
    ##################################################################

    def bestDroite(self):
        droiteRetenues= self.dfTrend[self.dfTrend['isActiv'] & self.dfTrend['isGood']]
        #print('droiteRetenues ',droiteRetenues.shape[0])
        # print(droiteRetenues[['dateDeb','dateFin','hit','deltaMax']])
        #droiteRetenues['indexTrend'] = droiteRetenues.index.tolist()[0]
        # Droites les moins touchées
        minHit = droiteRetenues['hit'].min()
        droiteRetenuesParMinHit = droiteRetenues[droiteRetenues['hit']==minHit]
        
        # Droite la plus récente
        laPlusRecente = droiteRetenuesParMinHit['dateFin'].max()
        droiteRetenueParDate = droiteRetenuesParMinHit[droiteRetenuesParMinHit['dateFin'] == laPlusRecente]
        laPlusHaussiere = droiteRetenueParDate['a'].max()
        
        # print(laPlusHaussiere)
        droiteRetenueParCoeffa = droiteRetenueParDate[droiteRetenueParDate['a'] == laPlusHaussiere]
         
        dateDeb = droiteRetenueParCoeffa.iloc[0]['dateDeb']
        valDeb = droiteRetenueParCoeffa.iloc[0]['valDeb']
        dateFin = droiteRetenueParCoeffa.iloc[0]['dateFin']
        valFin = droiteRetenueParCoeffa.iloc[0]['valFin']
        indexDeb = droiteRetenueParCoeffa.iloc[0]['indexDeb']
        indexFin = droiteRetenueParCoeffa.iloc[0]['indexFin']
        activDateFromOri = droiteRetenueParCoeffa.iloc[0]['activDateFromOri']
        # print('parCoeff',droiteRetenueParCoeffa.index.tolist()[0])
        indexDroite = droiteRetenueParCoeffa.index.tolist()[0]
        
        
        d=droiteTrend(dateDeb, valDeb, dateFin, valFin, indexDeb,indexFin,activDateFromOri,indexDroite)
        d.coeff()
       
        # print(d.a)
        return d
        

    ###############################################################
    #   calculLesDroites : Combinaisons des PB pour former
    #                les points de def des droites
    #                et les droites
    #   Output   : liste des Droites avec coeff a et b  calculés
    #              dfTrend          -> DataFrame des Droites
    #
    #   Parametre: inExtreme. Si Creux alors lesDroites = Supports
    #                         Si Top alors LesDroites  = Résistance
    #
    #   
    ###############################################################

    def calculLesDroites(self, inExtreme,horizonPost):
        
        #dfTrend = pd.DataFrame(columns = ['dateDeb', 'valDeb','dateFin', 'valFin','daysFromOri'])
        self.lesDroites = []
        for i in range(len(inExtreme)):
            for j in range(i+1,len(inExtreme)):
                dateDeb = inExtreme.iloc[i]['date']
                valDeb = inExtreme.iloc[i]['fLow']
                dateFin = inExtreme.iloc[j]['date']
                valFin = inExtreme.iloc[j]['fLow']

                indexDeb = self.sdOri.index[self.sdOri['date']==dateDeb].tolist()[0]
                indexFin = self.sdOri.index[self.sdOri['date']==dateFin].tolist()[0]

                droite = droiteTrend(dateDeb,valDeb,dateFin,valFin,indexDeb,indexFin,0,0)
                # setActivationDate definira la date à partir de laquelle la droite est active
                droite.setActivationDate(horizonPost)
                droite.coeff()
                self.lesDroites.append(droite)
        
        # Transformation de la liste d objets droiteTrend en DataFrame
        self.dfTrend = pd.DataFrame([x.as_dict() for x in self.lesDroites])
            
        return self.dfTrend

    ##################################################################
    # les deltas ne sont mis a jour que 20 jours après la def de la droite trend
    ##################################################################

    def delta2T1(self,bestDroite):
        global dateOriConst
        decalDelta = 20
        
        a = bestDroite.iloc[0]['a']
        b = bestDroite.iloc[0]['b']
        dateFin  = bestDroite.iloc[0]['dateFin']
        finDroite  = calculDateDiff(dateOriConst, dateFin)
        # print('a ',a,'b ',b, 'finDroite ', finDroite)
        #self.sdOri['prevTrend'] = a*self.sdOri['daysFromOri'] + b
        # self.sdOri['deltaDroiteActive'] = (self.sdOri['fClose']/self.sdOri['prevTrend']) - 1

        self.sdOri['prevDroiteActive'] = np.where(self.sdOri['daysFromOri']>(finDroite+decalDelta), \
                                               a*self.sdOri['daysFromOri'] + b,self.sdOri['prevDroiteActive'])
        
        self.sdOri['deltaDroiteActive'] = np.where(self.sdOri['daysFromOri']>(finDroite+decalDelta), \
                                              (self.sdOri['fClose']/self.sdOri['prevDroiteActive']) - 1,self.sdOri['deltaDroiteActive'])




    def dumpDroites2Excel(self):
        xlsFile = 'data/' + self.stockName + '_dtes.xls'
        self.dfTrend.to_excel(xlsFile)
       
    def dumpExcel(self):
        xlsFile = 'data/' + self.stockName + '_1.xls'
        self.sdOri.to_excel(xlsFile)
        
    def dumpCSVJulien(self):
        csvFile = 'data/csv/' + self.stockName + '_1.csv'
        self.sdOri[['symbol','date','prevDeltaPost']].to_csv(csvFile)    



    ###############################################################
    #   hitTrend : calcul pour chaque Droite le nombre de fois
    #              que la courbe la coupe
    #
    #               avec un tolérance de 0,5% 
    #
    #  dateOfStudyOri : le jour pour lequelle on fait la recherche
    ###############################################################  
  
  
    def hitTrend(self,dateOfStudyOri):
        lap1 = time.time()
        for i in range(self.dfTrend.shape[0]):
           # filtre sur date
            if (self.dfTrend.iloc[i]['isActiv'] & (not self.dfTrend.iloc[i]['isDead'])):               
                self.dfTrend.loc[i,'hit'] = 0
                dateDeb = self.dfTrend.iloc[i]['dateDeb']
                valDeb = self.dfTrend.iloc[i]['valDeb']
                dateFin = self.dfTrend.iloc[i]['dateFin']
                valFin = self.dfTrend.iloc[i]['valFin']
                indexDeb = self.dfTrend.iloc[i]['indexDeb']
                indexFin = self.dfTrend.iloc[i]['indexFin']
                activDateFromOri = self.dfTrend.iloc[i]['activDateFromOri']
                indexDroite = self.dfTrend.iloc[i].index.tolist()[0]

                d=droiteTrend(dateDeb, valDeb, dateFin, valFin, indexDeb,indexFin,activDateFromOri,indexDroite)
                d.coeff()
                
                currHitCurve = d.isHit(self,dateOfStudyOri)
                # print(currHitCurve, ' ' , d.a, ' ', d.b)
                
                deltaMax = d.valeursCalculees(self,dateOfStudyOri)
                
                if deltaMax > -0.005:
                    self.dfTrend.loc[i,'hit'] = 0
                else:
                    self.dfTrend.loc[i,'hit'] = currHitCurve
                    
                self.dfTrend.loc[i,'deltaMax'] = d.valeursCalculees(self,dateOfStudyOri)

        lap2 = time.time()
        print('lap2 stock1.hitTrend: ',( lap2 - lap1))
                    

    ###############################################################
    #   isCreux : Recherche un creux sur l'intervalle
    #   [horizonAnte:horizonPost]
    #
    #   Output:  DF des creux
    #      index       date     daysFromOri     fLow
    # 0     101    2017-07-07          394   50.5358
    # 1     132    2017-08-21          425   49.3461 
    #
    ###############################################################

    def isCreux(self,horizonAnte,horizonPost):
        df_ext = self.sdOri
        A = ['fLow']
        vectAnte = []
        vectPost = []

        # Production des colonnes 
        for i in range (1,horizonAnte+1):
            colAnte = 'fLow_ante' + str(i)
            df_ext[colAnte] = df_ext['fLow'].shift(i)
            A.append(colAnte)

        for i in range (1,horizonPost+1):
            colPost = 'fLow_post' + str(i)
            df_ext[colPost] = df_ext['fLow'].shift(-i)
            A.append(colPost)

        df_ext.dropna(inplace=True)
       
        # calcul des max et écarts sur slice
        df_ext['nivoMin'] = df_ext[A].values.min(1)

        # df_ext.info()
        # on ne retient que les max de chaque slice mobile
        df_ext['extrem'] = np.where(df_ext['nivoMin']==df_ext['fLow'],'Min','')

        # du ménage
        self.df_PB = df_ext[df_ext['extrem']=='Min'][['date','fLow']]
        self.df_PB = self.df_PB.reset_index()
        
        
        df_ext=df_ext[['date','fLow']]        
        return self.df_PB
        
    ###############################################################
    #   END - stock.isCreux() 
    ###############################################################

    ###############################################################
    #   isDeadDroite : Filtre les droites sur certaines conditions
    #
    #   Parametres: nombre de hits (5)
    #               
    #
    ###############################################################

    def isDeadDroite(self):
        condition = (self.dfTrend['hit'] >= 5)
        
        self.dfTrend['isDead'] = np.where(condition,True,False)
 


    ###############################################################
    #   isGoodDroite : Filtre les droites sur certaines conditions
    #
    #   Parametres: nombre de hits (5)
    #               ecart cours/droite   (-0.02 = -2%)
    #
    ###############################################################

    def isGoodDroite(self, dateOfStudyOri):
        condition = (self.dfTrend['hit'] < 15) & \
                    (self.dfTrend['deltaMax'] > -1.02) & \
                    (self.dfTrend['activDateFromOri'] <= dateOfStudyOri)
        
        self.dfTrend['isGood'] = np.where(condition,True,False)
  



    ###############################################################
    #   printLesDroites : impression des supports, juste pour contrôle
    #                      formatage très lent 
    ###############################################################
    
    def printLesDroites(self):
        nbSupport = len(self.lesDroites)
        if nbSupport > 0:
            for i in range(nbSupport):
                print("{:5.0f}".format(i), ' ',"{:8.4f}".format(self.lesDroites[i].a),  \
                      "{:9.4f}".format(self.lesDroites[i].b),' ', \
                      "{:5.0f}".format(self.lesDroites[i].dayFromOri),' ', \
                      "{:%d-%m-%Y}".format(self.lesDroites[i].dateDeb),' ', \
                      "{:%d-%m-%Y}".format(self.lesDroites[i].dateFin))
        else:
            print('no lesDroites')

    #####################################################################
    #   Lecture des fichiers de droites produits par readInit.py   
    #####################################################################

    def readDroitesXLS(self):
        xlsFile = 'data/droites/' + self.stockName + '_dtes.xls'
        self.dfTrend = pd.read_excel(xlsFile)
        self.dfTrend['isGood'] = True
        self.dfTrend['isDead'] = False

    #####################################################################
    #   activDateFromOri du second creux de la serie
    #   avant pas possible de calculer une droite    
    def setStartEstim(self):
        self.startEstim = self.sdOri.iloc[0]['activDateFromOri']

    ###############################################################
    #  Production de fichiers de controles
    #   - index de Droite électionnée À l instant t
    #   - valeurs calculées par la droite : prevTrendPost
    #   - Delta / cours : prevDeltaPost

    def vCPDump(self):
        xlsFile = 'data/' + self.stockName + '_calculees.xls'
        self.sdOri.dropna(inplace=True)
        self.sdOri.to_excel(xlsFile,columns =['symbol','date','fLow','prevTrend',\
                                            'prevDelta','prevTrendPost','prevDeltaPost', 'indexDroite'])

    # Rendement à 20 jours 
    def y20d(self):
        self.sdOri['c20'] = self.sdOri['fClose'].shift(-20)
        self.sdOri.dropna(inplace=True)
        self.sdOri['y20d'] = self.sdOri['c20']/self.sdOri['fClose'] - 1


    ################################################################
    #  valeurs calculées APRES l'activation de droite:
    #  dateOri du second creux + horizonPost + 1 jours
    #  pour calculer les écarts après définiton
    ################################################################

    def valeursIndividuellesPost(self,bestDroite,i):
        self.sdOri.loc[i,'prevTrendPost'] = bestDroite.a*i + bestDroite.b        
        self.sdOri.loc[i,'prevDeltaPost'] = self.sdOri.loc[i,'fLow']/self.sdOri.loc[i,'prevTrendPost']-1
        self.sdOri.loc[i,'indexDroite'] =   bestDroite.indexDroite


#############################################################################
#  END - Class serieStock
#############################################################################

#############################################################################
#
#   Class trend : pour les trend
#
#############################################################################       

class droiteTrend:
    def __init__(self, dateDeb, valDeb, dateFin, valFin, indexDeb,indexFin,activDateFromOri, indexDroite,a=0,b=0):
        self.dateDeb = dateDeb
        self.valDeb = valDeb
        self.dateFin = dateFin
        self.valFin = valFin
        self.indexDeb = indexDeb
        self.indexFin = indexFin
        self.activDateFromOri = activDateFromOri 
        self.indexDroite = indexDroite
        self.a = a
        self.b = b

    
    # pour conversion list -> DataFrame
    def as_dict(self):
        return {
            'dateDeb': self.dateDeb,
            'valDeb': self.valDeb,
            'dateFin': self.dateFin,
            'valFin': self.valFin,
            'indexDeb': self.indexDeb,
            'indexFin' : self.indexFin,
            'activDateFromOri': self.activDateFromOri,
            'indexDroite': self.indexDroite,
            'a' : self.a,
            'b' : self.b
            }    

    ################ INUTILE ?
    def setActivationDate(self,horizonPost):
        self.activDateFromOri = self.indexFin + horizonPost + 1
        

    # les coeff de la droite
    def coeff(self):
        
        self.a = (self.valFin-self.valDeb)/(self.indexFin-self.indexDeb)
        self.b = self.valFin - self.a*self.indexFin
        # return self.a, self.b
        
        
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #     
    # la droite coupe-t-elle la courbe?
    # 
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def isHit(self, stock,dateOfStudyOri):
        stock.sd['prevTrend'] = 0
        stock.sd['hit'] = 0

        stock.sd['prevTrend'] = self.a*stock.sd.index + self.b
        stock.sd['hit'] = np.where((stock.sd['prevTrend'].values > stock.sd['fLow'].values) & \
                                (stock.sd['prevTrend'].values < stock.sd['fHigh'].values) & \
                                ( self.indexDeb < stock.sd.index) & \
                                ( dateOfStudyOri > stock.sd.index),1,0)
  
        currHitCurve = stock.sd[stock.sd['hit']==1]['hit'].sum()
        stock.sd['prevTrend'] = 0
        # le nombre d'intersection Droite/Courbe
        return currHitCurve

    ################################################################
    #  valeursCalculees entre 0 et dateOfStudyOri
    #  pour évaluer la validité de la droite
    ################################################################
    

    def valeursCalculees(self, stock,dateOfStudyOri):
        # init
        stock.sd['prevTrend'] = 0
        # calcul des valeurs de la droite sur la période d étude
        # entre la date de dévbut de la droite = self.indexDeb
        # et dateOfStudyOri
        stock.sd['prevTrend'] = np.where((self.indexDeb <= stock.sd.index) & (dateOfStudyOri > stock.sd.index),self.a*stock.sd.index + self.b,0)

        stock.sd['prevDelta'] = np.where((stock.sd['prevTrend']!=0),(stock.sd['fLow']/stock.sd['prevTrend'])-1,0)

        # sauvegarde de la cassure maximale
        deltaMax = stock.sd[stock.sd['prevTrend']!=0]['prevDelta'].min()
        
#         xlsFile = 'data/' + stock.stockName + '_delta.xls'
#         stock.sd.to_excel(xlsFile)
        
        return deltaMax

    ################################################################
    #  valeurs calculées APRES l'activation de droite:
    #  dateOri du second creux + horizonPost + 1 jours
    #  pour calculer les écarts après définiton
    ################################################################


    def valeursCalculeesPost(self, stock, dateOfStudyOri,i):
        # init
        # calcul des valeurs de la droite sur la période d étude
        # date de début des calculs
        startCalculate = max(stock.startCalculate,self.activDateFromOri,stock.lastActivOri)
        # màJ de la valeur cliquet 
        stock.startCalculate = startCalculate
        stock.sd['prevTrendPost'] = np.where((startCalculate < stock.sd.index) & (dateOfStudyOri > stock.sd.index),\
                                             self.a*stock.sd.index + self.b,stock.sd['prevTrendPost'])
        
        stock.sd['prevDeltaPost'] = np.where((startCalculate < stock.sd.index) & (dateOfStudyOri > stock.sd.index),\
                                             (stock.sd['fLow']/stock.sd['prevTrendPost'])-1,stock.sd['prevDeltaPost'])
        
        stock.sd['indexDroite'] = np.where((startCalculate < stock.sd.index) & (dateOfStudyOri > stock.sd.index),\
                                           self.indexDroite,stock.sd['indexDroite'])


#     def vCPDump(self):
#         xlsFile = 'data/' + stock.stockName + '_calculees' + str(i) + '.xls'
#         stock.sd.to_excel(xlsFile,columns =['symbol','date','fLow','prevTrend',\
#                                             'prevDelta','prevTrendPost','prevDeltaPost', 'indexDroite'])
        


#############################################################################
#
#   Class ancrage : pour les points d ancrage des droites
#
#
#############################################################################       

class ancrage:
    def __init__(self, dateAncrage, nivoAncrage):
        self.dateAncrage = dateAncrage
        self.nivoAncrage = nivoAncrage
     
    def calculB(self, coeffA):
        global dateOriConst
        
        nbDayAncrage = calculDateDiff(dateOriConst,self.dateAncrage)
        self.bAncrage = self.nivoAncrage-coeffA*nbDayAncrage


#############################################################################
#
#  Class seriePB : serie de minimun
#
#   Input           : dataFrame
#   
#   Output:  dataFrame des PB
#
#   parametres : horizon d échantillonage
#                dateStudy : la date de l'étude
#
#   15.02.2022 : il faudra sans doute virer dateStudy
#                pour l'instant dateStudy="08.01.2030"
#                pour tout prendre
#
#############################################################################

class seriePB:
    def __init__(self, df_ext_source):
        #self.dateStudy = dt.datetime.strptime(dateStudy, "%d.%m.%Y")
        self.df_ext = df_ext_source.copy()
        #self.df_ext = self.df_ext[self.df_ext['date']<self.dateStudy]
        # print('seriePB ',dateStudy)


    ###############################################################
    #   lastDroite : sélectionne la meilleure droite
    #                - isHit le plus faible
    #                - dernier Point = le plus récent
    #                - plus grand a
    #
    #   ToDo : intégrer la date d'etude
    ###############################################################

    def lastDroite(self, dfTrend,stock):
        global dateOriConst
        
        dfTrend['a'] = 0
        dfTrend['b'] = 0
        dfTrend['isHit'] = 0

        startIsHit = time.time()
        for i in range(len(dfTrend)):
            if dfTrend.iloc[i]['isPourrie'] != 1:
                #print('i dans serieDB.lastDroite(): ',i,' ', time.time() - startIsHit)
                d1 = droiteTrend(dfTrend.iloc[i]['dateDeb'],dfTrend.iloc[i]['valDeb'], \
                                 dfTrend.iloc[i]['dateFin'],dfTrend.iloc[i]['valFin'])

                           # Les coeff y = a*x + b
                d1.coeff()
                dfTrend.loc[i,'a'] = d1.a
                dfTrend.loc[i,'b'] = d1.b
                #print('i dans serieDB.lastDroite() - iloc: ',i,' ', time.time() - startIsHit)
     
                dfTrend.loc[i,'isHit'] = d1.isHit(stock,self.dateStudy)
                #print('i dans serieDB.lastDroite() -isHIT: ',i,' ', time.time() - startIsHit)
 
        # print('Fin isHit: ', time.time() - startIsHit)
        # dans un Trend UP on ne retient que les Droites ascendantes
        dfTrendUP = dfTrend[dfTrend['a']>0]
        
        if dfTrendUP.shape[0] > 0:
            minHit  = dfTrendUP['isHit'].min()
            # print(minHit)
            # on ne retient que les Droites qui ne coupent pas la courbe ou le moins possible
            # si aucune Droite ne reste vierge
            newDF = dfTrendUP[dfTrendUP['isHit']==minHit]           
            # on prend la plus croissante
            data_last_row = newDF.iloc[newDF['a'].argmax():, :]
        else:   
            minHit  = dfTrend['isHit'].min()
            # print(minHit)
            # on ne retient que les Droites qui ne coupent pas la courbe ou le moins possible
            # si aucune Droite ne reste vierge
            newDF = dfTrend[dfTrend['isHit']==minHit]            
            # on prend la plus croissante
            data_last_row = newDF.iloc[newDF['a'].argmax():, :]
            
        # print(data_last_row)
#        data_last_row = newDF.iloc[len(newDF.index) - 1:, :]
        data_last_row  = pd.DataFrame()
        data_last_row = data_last_row.append(newDF.iloc[newDF['a'].argmax(), :])
        
        return data_last_row
        
 ###############################################################
#   END - seriePB.lastDroite() 
###############################################################       
        
        
        
        
        