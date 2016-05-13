# -*- coding: utf-8 -*-
"""
Created on Mon Oct 05 08:16:16 2015
Series of caluclations to get dividend features.

Cluster features in pairs and threes using K-means 
algorithm. Plot clusters for assessment.

Merge results of clustering with a SQL table.
@author: kristencutler
"""
import pandas as pd
import sys
import pyodbc
import numpy 
import datetime as dt
import sklearn.cluster as skl


def strip(text):
    return text.strip()

def datetime(text):
    return dt.datetime.strptime(text, '%Y-%m-%d')
    

class Divs(object):   
    def __init__(self): 
        self.locateData()
        self.makeDF() 
        self.standardDev()
        self.consecAmounts()        
        self.changeOverIssue()        
        self.decreaseAmounts()        
        self.totalYearAmount()
        self.makeStatsDF()

    def locateData(self):
        """Command to get dividends data from SQL database"""
        if sys.platform == 'win32':
            self.location = r'C:\Users\kristencutler\Documents\CLGroup\divHist\dividends.csv'
        if sys.platform == 'linux2':
            cnxn = pyodbc.connect('DSN=SFODEVDB1038; UID=research; PWD=@bcd432!')
            cursor = cnxn.cursor()

            cursor.execute(""" 
            SELECT ticker, dvd_ex_dt, dps, dvd_freq
            FROM [ResearchWS].[dbo].[Dividend_Archive]
            WHERE dvd_type = 'Regular Cash' or dvd_type = 'Partnership Dis' or dvd_type = 'Interest on Cap'""")
            
            data = cursor.fetchall()
            locationlist = []
            for row in data:
                secondList = [strip(row[0]), datetime(row[1]), row[2], row[3]]
                locationlist.append(secondList)
                self.location = locationlist        
        
    def makeDF(self):
        """Construct a dataframe"""
        if sys.platform == 'win32':
            self.df = pd.read_csv(self.location, names=['Symbol','Date','Amount','Frequency'], header=0, converters={'Symbol':strip, 'Date':datetime}) 
        if sys.platform == 'linux2':
            self.df = pd.DataFrame(self.location, columns=['Symbol', 'Date', 'Amount', 'Frequency']) 	

    def standardDev(self):
        """Standard deviation per symbol""" 
        symbol = self.df['Symbol'] 
        self._standardDev = []
        for sym in numpy.unique(symbol): 
                symData = self.df[self.df.Symbol==sym]  
                std = symData.Amount.std()
                self._standardDev.append(std)    
    
    def consecAmounts(self):
        """Number of consecutive payments starting at most recent date""" 
        symbol = self.df['Symbol'] #symbol column from df
        self._consecTimes = []
        for sym in numpy.unique(symbol): #gets unique symbols 
            count = 0            
            symAmount = self.df.Amount[self.df.Symbol==sym].tolist() 
            while count < len(symAmount)-1:
                if symAmount[count] == symAmount[count+1]: 
                    count += 1
                else:
                    break 
            self._consecTimes.append(float(count))
            
    def changeOverIssue(self):
        """Times dividendss changed divided by total number of dividends issued"""
        self._divsChanges = []
        symbol = self.df['Symbol']
        for sym in numpy.unique(symbol):
            count, totalChanges = 0, 0
            symAmount = self.df.Amount[self.df.Symbol==sym].tolist()            
            while count < len(symAmount)-1:
                if symAmount[count] != symAmount[count+1]:
                    totalChanges +=1
                count += 1
            self._divsChanges.append(float(totalChanges)/len(symAmount))     

    def decreaseAmounts(self):
        """Number of times divs decreased over total number of amounts issued 
        and 1 divided by todays date less the last decreased date"""
        symbol = self.df['Symbol'] 
        self._decreases = [] #if amount decreases - count the num times it decreases and divide by total amount 
        self._decreaseTime = [] #1 / todays time - date of less 
        for sym in numpy.unique(symbol):  
            count, time, flag, calc = 0, 0, 0, 0              
            symDates = self.df.Date[self.df.Symbol==sym].tolist()             
            symAmount = self.df.Amount[self.df.Symbol==sym].tolist() 
            while count < len(symAmount)-1:
                if symAmount[count] > symAmount[count+1]: 
                    flag += 1
                    time = ((dt.datetime.today() - symDates[count]).days)
                    #calc = 1/float(time)                    
                    calc = numpy.exp(-time/180.)
                count += 1
            self._decreases.append(flag/float(len(symAmount)))
            self._decreaseTime.append(calc)

    def totalYearAmount(self):
        """Calulates a yearly total amount per symbol"""
        symbol = self.df['Symbol']
        self._totalAmount = []
        for sym in numpy.unique(symbol):
            symData = self.df[['Date', 'Amount']][self.df.Symbol==sym] 
            symData['Years']=[date.year for date in symData.Date]
            symYrs = numpy.unique(symData.Years)
            totalYrList = []            
            for yr in symYrs: 
                totalYr = sum(symData.Amount[symData.Years==yr])    
                totalYrList.append(totalYr)
            yrStd = numpy.std(totalYrList)
            yrMean = numpy.mean(totalYrList)
            yrFinal = (float(yrStd) / yrMean) * 100 
            self._totalAmount.append(yrFinal)
        
    def makeStatsDF(self):        
        symbols = numpy.unique(self.df['Symbol'])
        self.dfstats = pd.DataFrame() 
        self.dfstats['Symbol'] = symbols
        self.dfstats['Std'] = self._standardDev
        self.dfstats['Consec'] = self._consecTimes
        self.dfstats['Changes'] = self._divsChanges 
        self.dfstats['Decreases'] = self._decreases
        self.dfstats['Decrease Time'] = self._decreaseTime
        self.dfstats['Total Amount'] = self._totalAmount
    
def makePlot(x, y):
    """Plot 2 features without cluster"""
    plt.scatter(x, y, s=100)
    plt.xlabel(x.name)
    plt.ylabel(y.name) 
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    if x.name == 'Std':
        plt.xlim(0,0.5)
    if x.name == 'Decrease Times':
        plt.xlim(0,0.8)
    if x.name == 'Decrease Last Time':
        plt.xlim(0,0.01)
    if y.name == 'Decrease Last Time': 
        plt.ylim(0,0.015)
    if x.name == 'Consec':
        plt.xlim(0,50)
    if y.name == 'Consec':
        plt.ylim(0,50)
    if y.name == 'Total Amount':
        plt.ylim(0,50)
    #plt.axis([0,3,0,3])
    plt.show()

def makeHist(features):
    """Histogram for each feature"""
    if features.name == 'Std' or features.name == 'Decreases':
        plt.hist(features, bins=(0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30))
    elif features.name == 'Consec':
        plt.hist(features, bins=(0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60, 63, 66, 67, 70))
    elif features.name == 'Decrease Time':
        plt.hist(features, bins=(0.0000, 0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.0010))
    else:
        plt.hist(features, 10, normed=1, cumulative=False)
    plt.ylabel(features.name)
    plt.show()
    
def makeCluster(features):
    """KMeans algorithm to create 2 clusters"""
    features_avg = features - features.mean() #data normalization  
    features_std = features.std() #data normalization
    features_norm = features_avg/features_std #data normaliztion
    clusterer = skl.KMeans(n_clusters=2, n_init=1, init=numpy.array([[0.0, 0.6, 0.0],[1.0, 6.0, 0.0]]))
    cluster_labels = clusterer.fit_predict(features_norm)
    return cluster_labels

def plotCluster(feature, feature2, groups):
    """Plot 2 clustered features"""
    colors = ['#00ff00' if num == 0 else '#0000ff' for num in groups]
    plt.xlabel(feature.name)
    plt.ylabel(feature2.name) 
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    if feature.name == 'Std':
        plt.xlim(0,0.5)
    if feature.name == 'Decrease Times':
        plt.xlim(0,0.8)
    if feature.name == 'Decrease Last Time':
        plt.xlim(0,0.01)
#    if feature2.name == 'Decrease Last Time': 
#        plt.ylim(0,0.05)
    if feature.name == 'Consec':
        plt.xlim(0,50)
    if feature2.name == 'Consec':
        plt.ylim(0,50) 
    if feature.name == 'Total Amount':
        plt.xlim(0,100)
    if feature2.name == 'Total Amount':
        plt.ylim(0,100)
    plt.scatter(feature, feature2, c=colors)      
    plt.show() 
    
def plot3Cluster(feature, feature2, feature3, groups):
    """Plot 3 features in 2 clusters"""    
    plt.figure(1,figsize=(15,10))
    ax1 = plt.axes(projection='3d')
    ax1.scatter(feature, feature2, feature3, c=groups, s=50)
    ax1.azim = 105
    ax1.elev = 15
    ax1.set_xlabel(feature.name)
    ax1.set_ylabel(feature2.name)
    ax1.set_zlabel(feature3.name)
    
def analyzeCluster(dividends):    
    """Loops through all features to create clusters and plot"""
    x = [dividends.dfstats['Std'], dividends.dfstats['Consec'], dividends.dfstats['Changes'], dividends.dfstats['Decreases'], dividends.dfstats['Decrease Time'], dividends.dfstats['Total Amount']]    
    y = [y.fillna(0) for y in x] #replace Nan values with 0
    x = y
    for feature in range(len(x)): 
        #column = column[~numpy.isnan(column)] #for hisroram
        #makeHist(column)
        feature2 = 1
        while feature2 < len(x): 
            if feature == feature2:
                feature2 += 1
                continue
            features = pd.concat([x[feature], x[feature2]], axis=1)
            groups = makeCluster(features)
            plotCluster(x[feature], x[feature2], groups)
            #makePlot(x[feature1], x[feature2])
            feature2 += 1


def initTemp(symbols, groups):
        """Create SQL temp table"""
        symbol = symbols
        value = groups
        date = dt.date.today().strftime("%Y-%m-%d")  
        
        if sys.platform == 'win32':
            cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=SFODEVDB1038\RESEARCHDB;PORT=1433;DATABASE=ResearchWS;UID=researchwriter;PWD=@bcd432!')
        if sys.platform == 'linux2':
            cnxn = pyodbc.connect('DSN=SFODEVDB1038;UID=researchwriter;PWD=@bcd432!')
            cursor = cnxn.cursor()
        
        cursor.execute(""" IF OBJECT_ID('tempdb..#divstemp') IS NOT NULL DROP TABLE #divstemp;
            
            CREATE TABLE #divstemp (symbol varchar(10), consistent_div_flag tinyint, date_added date);""")
        
        for sym, val in zip(symbol, value):
            cursor.execute("""INSERT INTO #divstemp (symbol, consistent_div_flag, date_added) VALUES (?, ?, ?)""", sym, int(val), date)
        cnxn.commit()
        return cursor, cnxn 

def mergeTable(cursor, cnxn):
      """Merges temp table onto Dividends_Consistency"""
      cursor.execute("""MERGE INTO [ResearchWS].[dbo].[Dividends_Consistency] AS T
                  USING #divstemp AS S
                  ON (T.Symbol = S.symbol)
                  WHEN MATCHED THEN
                  UPDATE SET T.Consistent_Div_Flag=S.consistent_div_flag, T.Date_Added=S.date_added
                  WHEN NOT MATCHED THEN
                  INSERT (Symbol, Consistent_Div_Flag, Date_Added)
                  VALUES (S.symbol, S.consistent_div_flag, S.date_added);""")  
      cnxn.commit()
      cnxn.close()

        
def main():
    return 
            
if __name__=="__main__":
    dividends=Divs()
    
#    import pickle
#    dividends = pickle.load(open("divs.pick", "rb"))
 
#   dividends = pickle.dump(dividends, open('divs.pick', 'wb'))

    if sys.platform == 'win32':
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        #cluster & plot 2 features 
        #analyzeCluster(dividends)
        #plot 3 specific features
        features = dividends.dfstats[['Changes', 'Decreases', 'Decrease Time']]
        groups = makeCluster(features)
        plot3Cluster(dividends.dfstats['Changes'].fillna(0), dividends.dfstats['Decreases'].fillna(0), dividends.dfstats['Decrease Time'].fillna(0), groups)
    
    if sys.platform == 'linux2':
       symbols = dividends.dfstats['Symbol']
       features = dividends.dfstats[['Decreases', 'Decrease Time', 'Changes']]
       groups = makeCluster(features)
       cursor, connection = initTemp(symbols, groups)
       mergeTable(cursor, connection)





    
