# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 09:02:52 2016
Script to test Regime Shift Checker class with 
different sets of data and create plots. 

@author: kristencutler
"""

import datetime
import numpy as np
from regimeshift import RegimeShiftChecker
from STARS import STARS
import matplotlib.pyplot as plt
    
def getDaysSinceJanuary(dates):
    """For a given date in a series, find the number 
    of days since January1."""
    
    daysList = []    
    
    for day in dates:
        startdate = datetime.datetime.strptime(day,  "%Y-%m-%d").date()
        jandate = datetime.date(startdate.year, 1, 1)
        daysbetween = (startdate - jandate).days    
        daysList.append(daysbetween)
    
    return daysList
    
def getNorms(days):
    """Normalize data by taking the quarterly averages
    and subtracting the corresponding average with every
    daily value."""
    
    daycount = 0
    quarterAvs = []
    dailyValues = []
    
    for num in range(4):
        av = np.mean(days[num::4])
        quarterAvs.append(av)

    for day in days:
        val = day - quarterAvs[daycount % 4] 
        dailyValues.append(val)
        daycount += 1

    return dailyValues

def makePlot(y1, x, l, p):
    """Plot results with all daily values."""
    x1 = range(len(y1))
    y2 = [0]*len(x)#np.linspace(0, 10, len(x))  
    plt.plot(x1, np.array(y1), label=p)
    plt.plot(x, np.array(y2),'ro', label=l)
    plt.autoscale(enable=True, axis=u'both', tight=False)
    plt.legend()
    plt.show()
    
def main():
    return

if __name__=="__main__":
    
    #AAMRQ
    #testdates = ["2011-01-19", "2011-04-20", "2011-07-20", "2011-10-19", "2012-02-15", "2012-04-19", "2012-07-18", "2012-10-17", "2013-01-16", "2013-04-18", "2013-07-18", "2013-10-17"]
    
    #AAPL
    #testdates = ["2008-01-22", "2008-04-23", "2008-07-21", "2008-10-21", "2009-01-21", "2009-04-22", "2009-07-21", "2009-10-19", "2010-01-25", "2010-04-20", "2010-07-20", "2010-10-18", "2011-01-18", "2011-04-20", 
#                "2011-07-19", "2011-10-18", "2012-01-24", "2012-04-24", "2012-07-24", "2012-10-25", "2013-01-23", "2013-04-23", "2013-07-23", "2013-10-28", "2014-01-27", "2014-04-23", "2014-07-22", "2014-10-20",
#                "2015-01-27", "2015-04-27", "2015-07-21", "2015-10-27", "2016-01-26"]
    
    #AAON
    testdates = ["2010-03-15", "2010-05-06", "2010-08-06", "2010-11-08", "2011-03-10", "2011-05-05", "2011-08-04", "2011-11-08", "2012-03-14", "2012-05-08", "2015-02-27", "2015-05-07", "2015-08-06", "2015-11-02", "2016-02-26"]    
    days = getDaysSinceJanuary(testdates)
    norms = getNorms(days)

#    result = STARS(norms, 2, 0.05)
#    
#    for i in result.shifts:
#        print(testdates[int(i)])
    
#    result = RegimeShiftChecker(norms, 2.0, 0.05)
#    
#    for i in result.rsiList:
#        print(testdates[int(i)])        
        
#    limit = 2.0
#    while (limit < 7.0):
#        probability = 0.05
#        while (probability < .2):
#            result = RegimeShiftChecker(norms, limit, probability)
#            makePlot(norms, result.rsiList, limit, probability)
#            probability += 0.05
#        limit += 1.0
        
    limit = 2.0
    while (limit < 7.0):
        count = 0
        probability = [0.025, 0.05, 0.1, 0.15]
        while (count < len(probability)):
            result = RegimeShiftChecker(norms, limit, probability[count])
            makePlot(norms, result.rsiList, limit, probability[count])
            count += 1
        limit += 1.0
    


        
