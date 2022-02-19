import pandas as pd
from datetime import timedelta
import datetime as dt
import time
import numpy as np
<<<<<<< HEAD
from os import walk

# arbitraire mais nécessaire a la vectorisation
dateOriConst = dt.datetime.strptime("02.01.2008", "%d.%m.%Y")
=======


# arbitraire mais nécessaire a la vectorisation
dateOriConst = dt.datetime.strptime("02.01.2016", "%d.%m.%Y")
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c

#############################################################
# calcul dateDiff en éliminant les WE
# inputs: datetime
# output: timedelta.days
#
# ToDo :  ajout des jours fériés!
#
#############################################################

def calculDateDiff(ObjDebut,ObjFin):

    #traitement samedi, dimache
    deltaSamedi = dt.timedelta(days=1)
    deltaDimanche = dt.timedelta(days=1)

    #Difference entre date
    timedelta = ObjFin - ObjDebut

    #init
    delta=dt.timedelta(days=1)
    currDate=ObjDebut

    while currDate.date() < ObjFin.date():
        weekDay=currDate.weekday()
    
        if weekDay==5:
            timedelta=timedelta-deltaSamedi
        elif weekDay==6:
            timedelta=timedelta-deltaDimanche
        
        currDate = currDate + delta
        
    # print(timedelta.days)
    return timedelta.days

#############################################################
# END calculDateDiff
#############################################################


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
        self.sdOri.drop(['high','low','open'], axis=1,inplace=True)
        self.sdOri.date = pd.to_datetime(self.sdOri.date, format="%Y-%m-%d")
        self.sdOri = self.sdOri.reset_index()
        
    # gros calcul à stocker    
    def initDateDiff(self):
        global dateOriConst
        self.sdOri['daysFromOri'] = 0
<<<<<<< HEAD
        print('LEM ',len(self.sdOri))
        #for i in range(10):
        for i in range(len(self.sdOri)):
            self.sdOri.loc[i,'daysFromOri'] = calculDateDiff(dateOriConst,self.sdOri.iloc[i]['date'])
            print('df',calculDateDiff(dateOriConst,self.sdOri.iloc[i]['date']))
=======
        #for i in range(10):
        for i in range(len(self.sdOri)):
            self.sdOri.loc[i,'daysFromOri'] = calculDateDiff(dateOriConst,self.sdOri.iloc[i]['date'])
            
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
 
    def dumpExcel(self):
        xlsFile = 'data/' + self.stockName + '.xls'
        self.sdOri.to_excel(xlsFile)
<<<<<<< HEAD
        
=======
    
       
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
    def readXLS(self):
        xlsFile = 'data/' + self.stockName + '.xls'
        self.sdOri = pd.read_excel(xlsFile)
     
    # Rendement à 20 jours 
    def y20d(self):
        self.sdOri['c20'] = self.sdOri['fClose'].shift(-20)
        self.sdOri.dropna(inplace=True)
        self.sdOri['y20d'] = self.sdOri['c20']/self.sdOri['fClose'] - 1
        
    def rangeSerie(self):
        global dateOriConst
        
        debut = self.sdOri['date'].min()
        fin = self.sdOri['date'].max()
        debOri  = calculDateDiff(dateOriConst, debut)
        finOri  = calculDateDiff(dateOriConst, fin)
        return debOri, finOri
        

#############################################################################
#
#  Class serieStock : pour les cotations d'un seul actif
#
#   Input           : data/XXXXXX.xls
#                    
#############################################################################

class serieStock:
    # chargement du xls prétraité par readinit.py 
    def __init__(self, stockName):
        self.stockName = stockName
        xlsFile = 'data/' + self.stockName + '.xls'
        self.sd = pd.read_excel(xlsFile)
        self.sd.date = pd.to_datetime(self.sd.date, format="%Y-%m-%d")
<<<<<<< HEAD
=======
        self.sd['prevDroiteActive'] = 1
        self.sd['deltaDroiteActive'] = 0

>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
        
    def dumpExcel(self):
        xlsFile = 'data/' + self.stockName + '_1.xls'
        self.sd.to_excel(xlsFile)
<<<<<<< HEAD
             
=======
        
    def dumpCSVJulien(self):
        csvFile = 'data/' + self.stockName + '_1.csv'
        self.sd[['symbol','date','deltaDroiteActive']].to_csv(csvFile)    
              

>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
    # Rendement à 20 jours 
    def y20d(self):
        self.sd['c20'] = self.sd['fClose'].shift(-20)
        self.sd.dropna(inplace=True)
        self.sd['y20d'] = self.sd['c20']/self.sd['fClose'] - 1
        
    def rangeSerie(self):
        global dateOriConst
        
        debut = self.sd['date'].min()
        fin = self.sd['date'].max()
        debOri  = calculDateDiff(dateOriConst, debut)
        finOri  = calculDateDiff(dateOriConst, fin)
        return debOri, finOri
<<<<<<< HEAD
      
    def delta2T1(self,bestDroite):
        a = bestDroite.iloc[0]['a']
        b = bestDroite.iloc[0]['b']
        print('a ',a,'b ',b)
        self.sd['prevTrend'] = a*self.sd['daysFromOri'] + b
        self.sd['deltaTrend'] = (self.sd['fClose']/self.sd['prevTrend']) - 1
=======

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
        #self.sd['prevTrend'] = a*self.sd['daysFromOri'] + b
        # self.sd['deltaDroiteActive'] = (self.sd['fClose']/self.sd['prevTrend']) - 1

        self.sd['prevDroiteActive'] = np.where(self.sd['daysFromOri']>(finDroite+decalDelta), \
                                               a*self.sd['daysFromOri'] + b,self.sd['prevDroiteActive'])
        
        self.sd['deltaDroiteActive'] = np.where(self.sd['daysFromOri']>(finDroite+decalDelta), \
                                              (self.sd['fClose']/self.sd['prevDroiteActive']) - 1,self.sd['deltaDroiteActive'])

        # self.sd[self.sd['daysFromOri']<(finDroite+20)]['deltaTrend'] = 0
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
         

#############################################################################
#
#   Class trend : pour les trend
#
#   Input File  :
#
#############################################################################       

class droiteTrend:
    def __init__(self, dateDeb, valDeb, dateFin, valFin):
        self.dateDeb = dateDeb
        self.valDeb = valDeb
        self.dateFin = dateFin
        self.valFin = valFin
    
    # les coeff de la droite
    def coeff(self):
        global dateOriConst
        
        self.a = (self.valFin-self.valDeb)/calculDateDiff(self.dateDeb, self.dateFin)
        self.b = self.valFin- self.a*calculDateDiff(dateOriConst, self.dateFin)
        # return self.a, self.b

    # la droite coupe-t-elle la courbe?
    # ToDo : Contrainte de date
<<<<<<< HEAD
    def isHit(self, stock):
        global dateOriConst
        
=======
    def isHit(self, stock,dateStudy):
        global dateOriConst

>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
        debOri, finOri = stock.rangeSerie()
        
        stock.sd['prevTrend'] = 0
        stock.sd['hit'] = 0

        stock.sd['prevTrend'] = self.a*stock.sd['daysFromOri'] + self.b
        stock.sd['hit'] = np.where((stock.sd['prevTrend'] > stock.sd['fLow']) & \
                                (stock.sd['prevTrend'] < stock.sd['fHigh']) & \
                                ( self.dateDeb < stock.sd['date']) & \
<<<<<<< HEAD
                                ( self.dateFin != stock.sd['date']),1,0)
  
        currHitCurve = stock.sd[stock.sd['hit']==1]['hit'].sum()
        
=======
                                ( self.dateFin != stock.sd['date']) & \
                                ( dateStudy > stock.sd['date']),1,0)
  
        currHitCurve = stock.sd[stock.sd['hit']==1]['hit'].sum()
        stock.sd['prevTrend'] = 0
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
        # le nombre d'intersection Droite/Courbe
        return currHitCurve
        

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
#############################################################################

class seriePB:
    def __init__(self, df_ext_source,dateStudy):
        self.dateStudy = dt.datetime.strptime(dateStudy, "%d.%m.%Y")
        self.df_ext = df_ext_source.copy()
        self.df_ext = self.df_ext[self.df_ext['date']<self.dateStudy]
<<<<<<< HEAD
=======
        # print('seriePB ',dateStudy)
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
   
###############################################################
#   isCreux : Recherche un creux sur l'intervalle
#   [horizonAnte:horizonPost]
#
#   Output:  DF
#
###############################################################

    def isCreux(self,horizonAnte,horizonPost):
        A = ['fLow']
        vectAnte = []
        vectPost = []

        # Production des colonnes 
        for i in range (1,horizonAnte+1):
            colAnte = 'fLow_ante' + str(i)
            self.df_ext[colAnte] = self.df_ext['fLow'].shift(i)
            A.append(colAnte)

        for i in range (1,horizonPost+1):
            colPost = 'fLow_post' + str(i)
            self.df_ext[colPost] = self.df_ext['fLow'].shift(-i)
            A.append(colPost)

        self.df_ext.dropna(inplace=True)
       
        # calcul des max et écarts sur slice
        self.df_ext['nivoMin'] = self.df_ext[A].values.min(1)

        # df_ext.info()
        # on ne retient que les max de chaque slice mobile
        self.df_ext['extrem'] = np.where(self.df_ext['nivoMin']==self.df_ext['fLow'],'Min','')

        # du ménage
        df_PB = self.df_ext[self.df_ext['extrem']=='Min'][['date','fLow']]
        df_PB = df_PB.reset_index()
        
        self.df_ext=self.df_ext[['date','fLow']]        
        return df_PB
        
###############################################################
#   END - seriePB.isCreux() 
###############################################################

###############################################################
#   lesDroites : Combinaisons des PB pour former
#                les points de def des droites
###############################################################

    def lesDroites(self, inCreux):
        
        dfTrend = pd.DataFrame(columns = ['dateDeb', 'valDeb','dateFin', 'valFin',])
        
        for i in range(len(inCreux)):
            for j in range(i+1,len(inCreux)):
                dateDeb = inCreux.iloc[i]['date']
                valDeb = inCreux.iloc[i]['fLow']
                dateFin = inCreux.iloc[j]['date']
                valFin = inCreux.iloc[j]['fLow']
                new_row = {'dateDeb':dateDeb, 'valDeb':valDeb, 'dateFin':dateFin, 'valFin':valFin}
                dfTrend = dfTrend.append(new_row, ignore_index=True)
            
        return dfTrend

###############################################################
#   END - seriePB.lesDroites() 
###############################################################

###############################################################
#   lastDroite : sélectionne la meilleure droite
#                - isHit le plus faible
#                - dernier Point = le plus récent
<<<<<<< HEAD
=======
#                - plus grand a
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
#
#   ToDo : intégrer la date d'etude
###############################################################

    def lastDroite(self, dfTrend,stock):
        global dateOriConst
        
        dfTrend['a'] = 0
        dfTrend['b'] = 0
        dfTrend['isHit'] = 0

        for i in range(len(dfTrend)):
            d1 = droiteTrend(dfTrend.iloc[i]['dateDeb'],dfTrend.iloc[i]['valDeb'], \
                             dfTrend.iloc[i]['dateFin'],dfTrend.iloc[i]['valFin'])

            # Les coeff y = a*x + b
            d1.coeff()
<<<<<<< HEAD

            dfTrend.loc[i,'a'] = d1.a
            dfTrend.loc[i,'b'] = d1.b

            dfTrend.loc[i,'isHit'] = d1.isHit(stock)


        # on ne retient que les Droites qui ne coupent pas la courbe 
        newDF = dfTrend[dfTrend['isHit']<1]
        
        # on prend la plus croissante
        data_last_row = newDF.iloc[newDF['a'].argmax():, :]
#        data_last_row = newDF.iloc[len(newDF.index) - 1:, :]
#         data_last_row  = pd.DataFrame()
#         data_last_row = data_last_row.append(newDF.loc[35])
=======
            dfTrend.loc[i,'a'] = d1.a
            dfTrend.loc[i,'b'] = d1.b
            dfTrend.loc[i,'isHit'] = d1.isHit(stock,self.dateStudy)


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
>>>>>>> 24849f6b7aedab1d63eb57088d05bb0ba3fa456c
        
        return data_last_row
        
 ###############################################################
#   END - seriePB.lastDroite() 
###############################################################       
        
        
        
        
        