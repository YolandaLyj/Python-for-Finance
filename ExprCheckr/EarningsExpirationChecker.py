# -*- coding: utf-8 -*-
"""
Created on Wed Sep 09 11:04:43 2015

@author: kristencutler

Compares earnings running in autotrader with 
estimated earnings. Earning dates are flagged
when estimated date is outside of the earning date
expiration period. 

"""

import os
import inspect
import csv
import pyodbc
import sys
import datetime as dt
from operator import itemgetter
curPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parPath = os.path.abspath(os.path.join(curPath,'..'))
if parPath not in sys.path:
    sys.path.append(parPath) 
#adds all folders in current directory to path
from Common import emailMessage

def getEarn():
    """SSH and SCP commands to get all earnings and confirmed earnings in AT"""
    if sys.platform == 'win32': 
        print('run commands file to get cag data off at')
        os.system("""Putty -ssh autotrader@10.217.7.57 -P 22 -pw Pr0dus3r -m C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\commands.txt""")
        print('copy all lag to expr checker folder')        
        os.system("""pscp -pw Pr0dus3r autotrader@10.217.7.57:tmpEarnAll.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\ALL_AT_EARNINGS_CAG.csv""")    
        print('copy conf lag to expr checker folder')        
        os.system("""pscp -pw Pr0dus3r autotrader@10.217.7.57:tmpEarnConf.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\Conf_AT_EARNINGS_CAG.csv""")
        print('run commands file to get lag data off at')        
        os.system("""Putty -ssh lag@10.217.7.85 -P 22 -pw Pr0dus3r -m C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\commands.txt""")
        print('copy ALL lag earnings to file')        
        os.system("""pscp -pw Pr0dus3r lag@10.217.7.85:tmpEarnAll.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\ALL_AT_EARNINGS_LAG.csv""")    
        print('copy CONF lag earnings to file')        
        os.system("""pscp -pw Pr0dus3r lag@10.217.7.85:tmpEarnConf.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\Conf_AT_EARNINGS_LAG.csv""")
        
    elif sys.platform == 'linux2':
        print('get all lag earnings off at')        
        os.system("""sshpass -p Pr0dus3r ssh lag@10.217.7.85 \"atutil csvSettings CUH.iref etc_common/SettingsDescriptorSigma.xml -in CUH.settings -to_csv -e '.*earningdates'>tmpEarnAll.csv\" """)
        print('get all lag confirmed off at')        
        os.system("""sshpass -p Pr0dus3r ssh lag@10.217.7.85 \"atutil csvSettings CUH.iref etc_common/SettingsDescriptorSigma.xml -in CUH.settings -to_csv -e '.*confirmedEarnings'>tmpEarnConf.csv\" """)
        print('copy all lag to expr checker folder')        
        os.system("""sshpass -p Pr0dus3r scp lag@10.217.7.85:tmpEarnAll.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/ALL_AT_EARNINGS_LAG.csv""")
        print('copy conf lag to expr checker folder')        
        os.system("""sshpass -p Pr0dus3r scp lag@10.217.7.85:tmpEarnConf.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/Conf_AT_EARNINGS_LAG.csv""")   
        print('get all cag earnings off at')        
        os.system("""sshpass -p Pr0dus3r ssh autotrader@10.217.7.57 \"atutil csvSettings CUH.iref etc_common/SettingsDescriptorSigma.xml -in CUH.settings -to_csv -e '.*earningdates'>tmpEarnAll.csv\" """)
        print('get conf cag earnings off at')        
        os.system("""sshpass -p Pr0dus3r ssh autotrader@10.217.7.57 \"atutil csvSettings CUH.iref etc_common/SettingsDescriptorSigma.xml -in CUH.settings -to_csv -e '.*confirmedEarnings'>tmpEarnConf.csv\" """)
        print('copy all cag to expr checker folder')
        os.system("""sshpass -p Pr0dus3r scp autotrader@10.217.7.57:tmpEarnAll.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/ALL_AT_EARNINGS_CAG.csv""")
        print('copy conf cag to expr checker folder')        
        os.system("""sshpass -p Pr0dus3r scp autotrader@10.217.7.57:tmpEarnConf.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/Conf_AT_EARNINGS_CAG.csv""")         
    
def getEst():
    """SCP command to get estimated earnings from AT"""
    if sys.platform == 'win32':     
        os.system('pscp -pw Pr0dus3r autotrader@10.217.7.57:dates/today/estimated_earnings.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\estimated_earnings_CAG.csv')
        os.system('pscp -pw Pr0dus3r lag@10.217.7.85:dates/today/estimated_earnings.csv C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\estimated_earnings_LAG.csv')
    elif sys.platform == 'linux2':
        os.system("""sshpass -p Pr0dus3r scp autotrader@10.217.7.57:dates/today/estimated_earnings.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/estimated_earnings_CAG.csv""")        
        os.system("""sshpass -p Pr0dus3r scp lag@10.217.7.85:dates/today/estimated_earnings.csv /home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/estimated_earnings_LAG.csv""") 
    print('imported estimated earnings')
    
 
        
def getAllocations():
    """SVN command to update list of allocations"""
    if sys.platform == 'win32':
        os.system('tortoiseproc.exe /command:update /path:"D:\\autotrader\\etc_lag\\trader" /closeonend:2')
        os.system('tortoiseproc.exe /command:update /path:"D:\\autotrader\\etc_autotrader\\trader" /closeonend:2')
    elif sys.platform == 'linux2':
        os.system('svn up /home/autotrader/dev/source/autotrader/etc_autotrader/trader/CUH_symbols.csv')
        os.system('svn up /home/autotrader/dev/source/autotrader/etc_autotrader/trader/CUH_symbols.csv')
    print('imported allocations')
       

def getTraderNames(badge):
    """Gets list of pairs (trader names, symbol) from SQL server.
    Returns a dictionnary of symbols and trader names.
    """  
    print('entered trader names fn', badge)
    if sys.platform == 'win32': 
        tpath = 'C:\Users\kristencutler\Documents\ClGroup\\ExpirationChecker\\tradernames.csv'    
        tradesym = {} 
        with open(tpath, 'rb') as t:    
            reader = csv.reader(t)
            for row in reader:
                tradesym[row[0]] = row[1]
            return tradesym
    
    elif sys.platform == 'linux2':
        tradesym = {}
        if badge == 'CAG':
            account = '42427300D7'
        elif badge == 'LAG':
            account = '42428300D6'
    
        if sys.platform == 'win32':
            cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=SFODEVDB2037\RESEARCHDB;PORT=1433;DATABASE=ResearchWS;UID=research;PWD=@bcd432!')
        if sys.platform == 'linux2':
            cnxn = pyodbc.connect('DSN=SFODEVDB2037;UID=research;PWD=@bcd432!')
            cursor = cnxn.cursor()

        cursor.execute("""
            SELECT Symbol, Member
            FROM [ResearchWS].[dbo].[AccountSplitMember]
            WHERE trDate = CAST(GETDATE() AS DATE)  AND Account = '""" + account + "'" )
        tradernamelist = cursor.fetchall()
   
        for sublist in tradernamelist:
            tradesym[sublist[0]] = sublist[1]
        return tradesym

    
    print('imported trader names')

    return tradesym

def importEarnings(badge):
    """Returns confirmed earnings dictionary of symbol and AT earnings dates and 
    estimated earnings dictionary of symbol and estimated earnings dates.
    """
    if sys.platform == 'win32':
        if badge == 'CAG':
            fpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\estimated_earnings_CAG.csv'
            gpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\ALL_AT_EARNINGS_CAG.csv'
            lpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\Conf_AT_EARNINGS_CAG.csv'
        elif badge == 'LAG':
            fpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\estimated_earnings_LAG.csv'
            gpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\ALL_AT_EARNINGS_LAG.csv' 
            lpath = 'C:\Users\kristencutler\Documents\ClGroup\ExpirationChecker\Conf_AT_EARNINGS_LAG.csv'
    elif sys.platform == 'linux2':
        if badge == 'CAG':
            fpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/estimated_earnings_CAG.csv'
            gpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/ALL_AT_EARNINGS_CAG.csv'
            lpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/Conf_AT_EARNINGS_CAG.csv'
        elif badge == 'LAG':
            fpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/estimated_earnings_LAG.csv'
            gpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/ALL_AT_EARNINGS_LAG.csv'
            lpath = '/home/autotrader/dataScraping/BloombergDataScraping/ExpirationChecker/Conf_AT_EARNINGS_LAG.csv'

    estimated, allearnings, confirmed, finalconf = {}, {}, {}, {}
    
    with open(fpath, 'rb') as f:  
        #dict for estimated earnings 
        reader = csv.reader(f)
        for row in reader:
            symbol = row[0]
            dt_val = dt.datetime.strptime(row[1].strip(), '%Y%m%d')
            if symbol not in estimated:
                estimated[symbol] = [dt_val]
            else:
                estimated[symbol].append(dt_val)
             
    with open(gpath, 'rb') as g:
        #dict for all earnings in AT
        reader = csv.reader(g)
        #next(reader, None)
        lines = g.readlines()[1:]        
        #get list of values and create values as datetime
        for row in lines: 
            symbol = row[0:22].split(' ')[0]
            data = row[22:]            
            for line in data.split(' '): #  split on space for both files 
                if len(line) > 8:
                    group = line.split(',')   
                    dt_val = dt.datetime.strptime(group[0].strip(), '%Y%m%d')
                else:
                    if line.strip() == '':
                        continue
                    else:
                        dt_val = dt.datetime.strptime(line.strip(), '%Y%m%d')
                if symbol not in allearnings:
                    allearnings[symbol] = [dt_val]
                else:
                    allearnings[symbol].append(dt_val)
                                                        
    with open(lpath, 'rb') as l:
        #dict for confirmed earnings in AT
        reader = csv.DictReader(l)
        for row in reader: #get list of values and create values as datetime 
            confirmed.setdefault(row['symbol'].split()[0], 
                    [dt.datetime.strptime(i, '%Y%m%d')
                    for i in row['confirmedEarnings'].split()])  
    
                           
    for symbol in allearnings.keys():
        #get final dict of AT earnings 
        allset = set(allearnings[symbol])
        if symbol in confirmed and confirmed[symbol] != ['']:
            confirmedset = set(confirmed[symbol])
            finalconfset = allset - confirmedset
        else:
            finalconfset = allset
        finalconf[symbol] = list(finalconfset)
        print('created confirmed & estimated dict')
    return finalconf, estimated
       
def getExpr(finalconf, estimated):
    """Gets before and after expr date for every date in confirmed earnings
    and estimated earnings.
    
    Returns confirmedexprs dictionary of date and expirations and 
    estimatedexprs dictionary of date and expirations.
    """
    confirmedexprs, estimatedexprs = {}, {}
 
    for date in finalconf:
        if date < dt.datetime.today() + dt.timedelta(days=90):
            confirmedexpr1 = FirstMthWeekdayOfMonth(date.year, date.month, 4) + dt.timedelta(days=14)         
            if date <= confirmedexpr1: #date of symbol is before expiration date one
                if date.month == 1: #checks if expir date one is in jan
                    tempmonth, tempyear = 12, date.year-1 #changes month to dec and year before
                else:
                    tempmonth, tempyear = date.month-1, date.year #subtract one month
                confirmedexpr2 = FirstMthWeekdayOfMonth(tempyear, tempmonth, 4) + dt.timedelta(days=14) 
            else:
                if date.month == 12: #checks if expir date in dec 
                    tempmonth, tempyear = 1, date.year+1 #changes month to jan and one year ahead
                else:
                    tempmonth, tempyear = date.month + 1, date.year #add one month
                confirmedexpr2 = FirstMthWeekdayOfMonth(tempyear, tempmonth, 4) + dt.timedelta(days=14)
                confirmedexprs[date] = (confirmedexpr1, confirmedexpr2) #dict of exprs keyed on date
    print('created dict of confirmed expr dates')     
    for date in estimated:
            estexpr1 = FirstMthWeekdayOfMonth(date.year, date.month, 4) + dt.timedelta(days=14)         
            if date <= estexpr1:
                if date.month == 1:
                    tempmonth, tempyear = 12, date.year-1
                else:
                    tempmonth, tempyear = date.month-1, date.year
                estexpr2 = FirstMthWeekdayOfMonth(tempyear, tempmonth, 4) + dt.timedelta(days=14)
            else:
                if date.month == 12:
                    tempmonth, tempyear = 1, date.year+1
                else:
                    tempmonth, tempyear = date.month + 1, date.year
                estexpr2 = FirstMthWeekdayOfMonth(tempyear, tempmonth, 4) + dt.timedelta(days=14)
                estimatedexprs[date] = (estexpr1, estexpr2)       
    print('created dict of est expr dates')
    return estimatedexprs, confirmedexprs 

def compareExpr(estimatedexprs, confirmedexprs, symbol):
    """Check expiration dates of each date and flags date 
    with expiration dates that match.
    
    Return a list of lists of symbol, AT date, estimated date
    and expiration date.
    """    
    final, result = [], []    
    for confdate in confirmedexprs:
        [confirmedexprs[confdate]].sort()
        confexfirst = confirmedexprs[confdate][0]
        confexlast = confirmedexprs[confdate][1]
        for estdate in estimatedexprs:
            [estimatedexprs[estdate]].sort()
            estexfirst = estimatedexprs[estdate][0]
            estexlast = estimatedexprs[estdate][1] 
            if confexfirst == estexlast: #first unconfirmed matches last estimated
                result = [symbol, confdate, estdate, confexfirst] 
                final.append(result)
            if confexlast == estexfirst: #last unconfirmed matches first estimated 
                result = [symbol, confdate, estdate, confexlast]
                final.append(result)
    print('compared expr dates')
    return final
   
def FirstMthWeekdayOfMonth(year, month, M):
    day = dt.datetime(year=year, month=month, day=1)
    day += dt.timedelta(days=((7+M-day.weekday())%7))
    assert day.weekday()==M
    return day
               
def makeEmail(badge, tradernames, resultlist): 
    """Adds trader name to each list in resultlist. 
    
    Adds * to any symbol that is unallocated. Removes a symbol 
    if it is not assigned to a trader and unallocated.
    
    Makes a table for each list in result list with HTML.
    """     
    if sys.platform == 'win32':
        if badge == 'CAG':
            rpath = 'C:\Users\kristencutler\Documents\ClGroup\\etc_autotrader\\trader\\CUH_symbols.csv'
        elif badge == 'LAG':
            rpath = 'C:\Users\kristencutler\Documents\ClGroup\\etc_lag\\trader\\CUH_symbols.csv'
    elif sys.platform == 'linux2':
        if badge == 'CAG':
            rpath = '/home/autotrader/dev/source/autotrader/etc_autotrader/trader/CUH_symbols.csv'
        elif badge == 'LAG':
            rpath = '/home/autotrader/dev/source/autotrader/etc_lag/trader/CUH_symbols.csv'
            
    allocations = {}  
                   
    for sublist in resultlist: 
        symbol = sublist[0] 
        if symbol in tradernames.keys(): 
            sublist.insert(0, tradernames[symbol]) #matches trader name to symbol 
        else:
            sublist.insert(0, ' ')
               
    with open(rpath, 'rb') as r:    
        reader = csv.reader(r)
        for row in reader:
            allocations[row[1]] = row[2] 

    for sublist in resultlist:
       ticker = sublist[1]
       if not ticker in allocations or allocations[ticker] == '':
           sublist[1] += '*'  #adds * to unallocated ticker
    resultlist.sort(key=itemgetter(0, 1))  
    
    table = """<html><head>
    <meta http-equiv="Content-Type" content="text/html; charset=us-ascii"><style>
    table,th, td
    {
    border:1px solid black;
    border-collapse:collapse;
    }
    th, td
    {
    font-size: 10pt; padding:5px; 
    }
    th
    {
    text-align:center;
    }
    </style>
    </head>
    Displays earnings events when autotrader earnings date and <br>
    estimated earnings cross an expiration. <br> 
    * = unallocated <br> 
    <body>
    <table width="480">
    <col width = 100>
    <col width = 80>
    <col width = 100>
    <col width = 100>
    <col width = 100>
    <tr bgcolor="C0D7EB">
    <th> Name </th> 
    <th> Ticker </th>
    <th> AT  </th> 
    <th> EXPR </th>
    <th> EST </th> 
    </tr>"""
                  
    # #FFFFFF" "#F0FFFF" #D8D8D8             
    last = ' '
    color = ["#FFFFFF", "#D8D8D8" ]    
    #index = 0
    for sublist in resultlist: 
        if sublist[0] == ' ' and sublist[1][-1] == '*':
            continue
        if sublist[0] != last and sublist[0] != ' ':
	        #index = 0 if index == 1 else 1            
                #color.reverse()
                temp = color[1]
                color[1] = color[0]
                color[0] = temp        
        name = """<tr bgcolor=""" + color[0] +  """> <td>""" + sublist[0] + """</td>"""                
        other = """<td>""" + sublist[1] + """</td> <td>"""  + \
                dt.datetime.strftime(sublist[2], '%m-%d-%Y') + \
                """</td> <td>""" + dt.datetime.strftime(sublist[4], '%m-%d-%Y') + """</td> <td>""" + \
                dt.datetime.strftime(sublist[3], '%m-%d-%Y') + """</td>"""         
        last = sublist[0]
        table += name + other + """</tr>""" 
    return table
        
def main():
    getEarn()   
    getEst()    
    getAllocations() 
    
    accounts = ['CAG', 'LAG']      
    for badge in accounts:
       tradernames = getTraderNames(badge)
       finalconf, estimated = importEarnings(badge)
       resultlist = []    
       for symbol in finalconf:
           if symbol in estimated:
               estimatedexprs, confirmedexprs  = getExpr(finalconf[symbol], estimated[symbol]) 
               result = compareExpr(estimatedexprs, confirmedexprs, symbol)
               if result == []: #checks for empty result list 
                   continue
               resultlist.append(result) 
       resultlist = [x for y in resultlist for x in y] #flattens final list   
       email = makeEmail(badge, tradernames, resultlist)
       maintenance = False
       if maintenance:
         if badge == 'LAG':
               emailMessage.SendEmail('kristen.cutler@cutlegrouplp.com', 'ian.schultz@cutlergrouplp.com', 'kristen.cutler@cutlergrouplp.com', email, 'LAG:Flagged Earnings Dates', ' ') 
               print('sent email for LAG')
         elif badge == 'CAG':
               emailMessage.SendEmail('kristen.cutler@cutlergouplp.com', 'ian.schultz@cutlergrouplp.com', 'kristen.cutler@cutlergrouplp.com', email, 'CAG:Flagged Earnings Dates', ' ')
               print('sent email for CAG')
       else:    
         if badge == 'CAG' and resultlist != []:
             emailMessage.SendEmail('kristen.cutler@cutlergouplp.com', 'Team27trading@cutlergrouplp.com', 'kristen.cutler@cutlergrouplp.com', email, 'CAG: Flagged Earnings Dates', ' ')
         elif badge == 'LAG' and resultlist != []:
             emailMessage.SendEmail('kristen.cutler@cutlergouplp.com', 'Team28trading@cutlergrouplp.com', 'kristen.cutler@cutlergrouplp.com', email, 'LAG: Flagged Earnings Dates', ' ')
    return 
            
if __name__=="__main__":
   main()

 
           


    
    
    

    
    


    
    
    
