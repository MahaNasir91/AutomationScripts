#--------------------------------------------------------------------------------------
#
#     $Source: Performance/ElementCRUD/ModifiedPerformanceScripts/AddDataToArchiveDb.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
import sys
import xlrd
import sqlite3
import os
import math

'''
def getSQLiteDate(date1):
    date_parts = date1.split('-')
    day1 = date_parts[0]
    if len(day1) == 1:
        day = "0" + day1
    else:
        day = day1
    month1 = date_parts[1]
    if len(month1) == 1:
        month = "0" + month1
    else:
        month = month1
    date2 = date_parts[2] + "-" + month + "-" + day
    return date2
'''
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def getTableName(c):
    tableName = ""
    buffer = 'SELECT name FROM sqlite_master WHERE type="table" AND name="Archive"'
    try:
        c.execute(buffer)
        for row in c:
            tableName = row[0]
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer
    return tableName

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def createTable(c):
    buffer = 'CREATE TABLE [Archive] ([Operation] TEXT, [Element] TEXT, [DbSize] TEXT, [API] TEXT, [Stream] TEXT, [Date] DATETIME, [Speed] INTEGER, [Platform] TEXT, [Device] TEXT)'
    try:
        c.execute(buffer)
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def insertData(c, sheet, stream, date, platform, device):
    count = 0
    for row_idx in range(0, sheet.nrows):    # Iterate through rows
        for col_idx in range(0, sheet.ncols):  # Iterate through columns
            cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            if (cell_obj.value == 'PerformanceFixtureCRUD') and (sheet.cell(row_idx, col_idx + 1).value in TestsToAdd):
                #Operation
                operation = sheet.cell(row_idx, col_idx + 1).value[8:]
                #Element
                desc = sheet.cell(row_idx, col_idx + 2).value
                print desc
                descParts = desc.split("'")
                element = descParts[1]
                #DbSize
                descP2 = desc.split(":")
                descP3 = descP2[1].split("]")
                dbSize = descP3[0].strip()
                print dbSize
                dbWrite = dbSizes[dbSize]
                #API
                if descParts[0].find('"') == -1:
                    descP1 = descParts[0].split(' ')
                    level = descP1[0]
                else:
                    descP1 = descParts[0].split('"')
                    descP4 = descP1[1].split(' ')
                    level = descP4[0]
                    
                if level == "Element":
                    level = "ElementAPI"
                #Speed
                speed = sheet.cell(row_idx, col_idx + 3).value
                speed1 = int(math.ceil(speed))

                #Write to the Db now
                try:
                    buffer = 'INSERT INTO Archive ([Operation], [Element], [DbSize], [API], [Stream], [Date], [Speed], [Platform], [Device]) VALUES ("' + str(operation) + '","' + str(element) + '","' + str(dbWrite) + '","' + str(level) + '","'+ str(stream) + '","' + date + '","' + str(speed1) + '","' + platform + '","' + device +'")'
                    c.execute(buffer)
                    count = count + 1
                except sqlite3.Error as e:
                    print "An error occurred:", e.args[0]
                    print "The command was: ", buffer
    return count            

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def updateData(c, sheet, stream, date, platform, device):
    count = 0
    for row_idx in range(0, sheet.nrows):    # Iterate through rows
        for col_idx in range(0, sheet.ncols):  # Iterate through columns
            cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            if (cell_obj.value == 'PerformanceFixtureCRUD') and (sheet.cell(row_idx, col_idx + 1).value in TestsToAdd):
                #Operation
                operation = sheet.cell(row_idx, col_idx + 1).value[8:]
                #Element
                desc = sheet.cell(row_idx, col_idx + 2).value
                descParts = desc.split("'")
                element = descParts[1]
                #DbSize
                descP2 = desc.split(":")
                descP3 = descP2[1].split("]")
                dbSize = descP3[0].strip()
                dbWrite = dbSizes[dbSize]
                #API
                if descParts[0].find('"') == -1:
                    descP1 = descParts[0].split(' ')
                    level = descP1[0]
                else:
                    descP1 = descParts[0].split('"')
                    descP4 = descP1[1].split(' ')
                    level = descP4[0]
                    
                if level == "Element":
                    level = "ElementAPI"
                #Speed
                speed = sheet.cell(row_idx, col_idx + 3).value
                speed1 = int(math.ceil(speed))

                #Write to the Db now
                try:
                    buffer = 'UPDATE Archive SET Speed=' + str(speed1) + ' WHERE Stream="' + str(stream) + '" and API = "'+ str(level) +'" and DbSize="' + str(dbWrite) + '" and Element="' + str(element) + '" and Date = "' + date + '" and Operation="' + str(operation) +'"'
                    c.execute(buffer)
                    if c.rowcount == 1:
                        #print buffer
                        count = count + 1
                except sqlite3.Error as e:
                    print "An error occurred:", e.args[0]
                    print "The command was: ", buffer
    return count

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def dataExists(c, stream, date, platform, device):
    exists = False
    count = 0
    try:
        buffer = 'SELECT count(*) FROM Archive WHERE Stream="' + str(stream) + '" and API = "ElementAPI" and DbSize="Large" and Element="'+mostComplexElementName+'" and Date = "' + date + '" and Platform = "' + platform + '" and Device ="' + device + '"'
        c.execute(buffer)
        for row in c:
            count = row[0]
        if count > 0:
            exists = True
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer
    return exists

## Entry Point of script    
if len(sys.argv) < 6:
    print '***** ERROR Script not executed *****'
    print 'Correct usage: AddDataToDb.py PerfResults.xlsx Archive.db'
    print 'i.e. first argument is the Excel sheet and second is the Db to be used'
    sys.exit()
    
fileName = sys.argv[1]
dbName = sys.argv[2]
SmallDbSize = sys.argv[3]
MediumDbSize = sys.argv[4]
LargeDbSize = sys.argv[5]

dbSizes = {SmallDbSize : 'Small', MediumDbSize : 'Medium', LargeDbSize : 'Large'}
#Hardcoded list of tests that we add. We ignore all other tests in the fixture if any
TestsToAdd = ['ElementsInsert', 'ElementsSelect', 'ElementsUpdate', 'ElementsDelete']

conn = sqlite3.connect(dbName)
c = conn.cursor()

# Create Table if it is not there
if not getTableName(c) == "Archive":
    createTable(c)
    
#Read data from Analysis file and store in Db
xl_workbook = xlrd.open_workbook(fileName)
xl_sheet = xl_workbook.sheet_by_name('Summary')
xl_sheet_Curr = xl_workbook.sheet_by_name('Current')
xl_sheet_Ben = xl_workbook.sheet_by_name('Benchmark')
currCount = benCount = 0

##First Let's inert Current Run's data
#Stream, Date, Platform and Device
stream = xl_sheet.cell(5,3).value
platform = xl_sheet.cell(6,3).value
device = xl_sheet.cell(7,3).value
date = xl_sheet.cell(8,3).value.strip()
stream = stream.lower()

if stream in ('dgndb61-16Q2', 'dgndb61-16Q4'):
    mostComplexElementName = 'Element4'
elif stream in ('bim0200', 'bim2-0R1' , 'bim0200dev'):
    mostComplexElementName = 'PerfElementSub3'

if dataExists(c, stream, date, platform, device):
    currCount = updateData(c, xl_sheet_Curr, stream, date, platform, device)
else:
    currCount = insertData(c, xl_sheet_Curr, stream, date, platform, device)

##Now Update the Benchmark data in Db
#Stream, Date, Platform and Device
stream = xl_sheet.cell(5,5).value
platform = xl_sheet.cell(6,5).value
device = xl_sheet.cell(7,5).value
date = xl_sheet.cell(8,5).value.strip()

if dataExists(c, stream, date, platform, device):
    benCount = updateData(c, xl_sheet_Ben, stream, date, platform, device)
else:
    benCount = insertData(c, xl_sheet_Ben, stream, date, platform, device)
     
conn.commit()
conn.close()

print ''
print '***************************************************************'
print 'Total Current records inserted             : ' + str(currCount)
print 'Total Benchmark records inserted or updated: ' + str(benCount)
print '***************************************************************'