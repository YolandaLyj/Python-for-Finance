# -*- coding: utf-8 -*-
"""
Created on Mon Jan 04 12:21:33 2016

An implementation of Sequential T-test Analysis of Regime Shifts 
as described in the paper:

"A sequential algorithm for testing climate regime shifts"
S.N. Rodionov
Geophys. Rev. Ltrs. V31 N9
May 2004


@author: kristencutler
 """
 
import scipy.stats
import numpy as np
import math

class RegimeShiftChecker(object):

    def __init__(self, data, limit, probability):
        self.data = data
        self.limit = limit
        self.p = probability
        self.rsiList = []
        self.getDiff()
        self.getRegimeMean(0, self.limit)
        self.checkLimits()
  
    def getDiff(self):
        """Determine the difference between mean values of two regimes. T is 
        the value of T-distrubtion, p is probability and l is cut-off length. 
        Find the variance for every number l interval and get the average."""
        t = scipy.stats.t.interval(1.0-(self.p), 2*(int(self.limit))-2)[1]
        first, last, varianceList = 0, 10, []

        for elem in self.data:
            varianceList.append(scipy.var(self.data[first:last]))
            first += 1
            last += 1

        self.averageVar = round(np.mean(varianceList), 2)    
        self.diff = t * math.sqrt(2.0*(self.averageVar/10.0))

    def getRegimeMean(self, first, last):
        """"Calculate the mean of a regime and the levels that should be reached
        to qualify as a regime shift."""              
        self.xr1 = np.mean(self.data[int(first):int(last)])     
        self.greaterLimit = round(self.xr1 + self.diff, 2)
        self.lesserLimit = round(self.xr1 - self.diff, 2)
        self.bounds = [self.greaterLimit, self.lesserLimit]
        
    def checkLimits(self):
        """For every value starting with year l + 1, check if it exceeds
        bounds. If it does not exceed, recalculate the 
        average of the regime (call getMean) to include value (i) and previous 
        values (l - 1) else calculate the RSI."""
        currentshift = ''
        self.point = self.limit
        while (int(self.point) <= len(self.data)-1):
            if self.rsiList and self.point <= self.rsiList[0] + self.limit:
                self.getRegimeMean(self.rsiList[0], (min(self.rsiList[0] + self.limit, len(self.data)-1)))
            else:
                self.getRegimeMean(self.point - self.limit, self.point)
            if self.data[int(self.point)] > self.greaterLimit or self.data[int(self.point)] < self.lesserLimit:
                testrange = range(int(self.point), (min(int(self.point) + int(self.limit), len(self.data)-1) + 1))
                rsiflag, direction = self.calcRSI(testrange, self.bounds)
                if rsiflag and currentshift != direction:
                    self.rsiList.append(self.point)
                    currentshift = direction
            self.point += 1
    
    def calcRSI(self, sub_index, bounds):
        """Calculate the Regime Shift Index"""
        x_sign = -1 if self.data[sub_index[0]] < min(bounds) else 1
        limit = min(bounds) if self.data[sub_index[0]] < min(bounds) else max(bounds)
        RSI = 0
        for idx in sub_index:
            x_star = x_sign * (self.data[idx] - limit)
            marginal_RSI = x_star / (np.sqrt(self.averageVar) * self.limit)
            RSI += marginal_RSI
            if RSI < 0:
              return False, None
        strDir = 'up' if x_sign > 0 else 'down'
        return True, strDir
   
    
#    pdo = [.04, .79, .82, .86, .63, .73, .92, -.3, 1.36, .23, -.25, -1.11, -1.72, -.03, 0.34, -.41, -.64, -.79, -1.13, -1.07, -1.18, -.66,
#           1.05, .75, 1.29, -.05, .3, 1.07, .96, .97, .97, .08, -.26, .29, .17, 1.01, 1.79, 0, .5, 1.36, 2.03, 2.14, 1.01, -.18, .18, -1.02,
#           -.91, -.73, -.11, -2.01, -2.13, -1.54, -2.01, -.57, -1.32, .2, -2.48, -1.82, 0.25, .69, .3, 1.18, -1.29, -.33, .01, -1.24, -.82, 
#           -.2, -.95, -1.26, .61, -1.9, -1.99, -.46, -1.22, -.84, -1.14, 1.65, .34, -.58, -.11, .59, .34, .56, 1.5, 1.27, 
#           1.12, 1.88, .93, -.95, -.3, -2.02, .05, .05, 1.21, -.49, .59, .23, .83, -.32, -2., .6, .27, 2.09, .43, .44]
#    testRegime = RegimeShift(pdo, 10.0, 0.05)   
#    years = range(1900, 2006)
#    for i in testRegime.rsiList:
#        print(years[int(i)])
#    result = [1910, 1922, 1943, 1958, 1977, 1989, 2003]
