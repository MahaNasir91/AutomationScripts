import pyodbc, os, sys, argparse, xlrd , math
from datetime import datetime
import functools
from collections import Counter

class WriteGTestRepeatDataToSql:

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    #-------------------------------------------------------------------------------------------
    def __init__(self):
        self.server = 'isbprddb01'
        self.database = 'ImodelTools'
        self.username = 'sa'
        self.password = 'qwe123!@#'


    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # Python Connectivity to SQL server
    #-------------------------------------------------------------------------------------------
    def databaseConnectivity(self):
        print 'Connecting....'
        conn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        print 'connected...'
        cursor = conn.cursor()
        return conn, cursor

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # To execute asql query
    #-------------------------------------------------------------------------------------------
    def executeQuery(self,query):
            try:
                print 'Executing query: ' + query
                cursor.execute(query)
                
            except pyodbc.Error as e:
                print "An error occurred:", e.args[0]
                print "The command was: ", query
                exit()
                
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # To create an archive table in the database
    #-------------------------------------------------------------------------------------------
    def createTable(self,TableName):
        
        sql = 'CREATE TABLE ' + TableName + ' ([Date] DATETIME, [Platform] NVARCHAR(25), [Stream] NVARCHAR(25), [TestName] NVARCHAR(500), [Status] NVARCHAR(100))'
        self.executeQuery(sql)

        db.commit()
        print 'Table ' + TableName + ' successfully created.'

        
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       12/2018
    #-------------------------------------------------------------------------------------------
    def getTableName(self,TableName):
        tableName = ""
        try:
            sql =  "SELECT * FROM information_schema.tables WHERE table_type = 'base table' AND table_name=?"
            cursor.execute(sql ,TableName)
            for row in cursor:
                tableName = row[0]
                
        except pyodbc.Error as e:
            print "An error occurred:", e.args[0]
            print "The command was: ", sql
            exit()
            
        return tableName

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       12/2018
    #-------------------------------------------------------------------------------------------
    def getValue(self, query):     
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1
    
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       12/2018
    #-------------------------------------------------------------------------------------------
    def dataExists(self,tableName,Date,PlatformName,Stream,TestName,Status):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE Date='" + str(Date) + "' and Platform='" + PlatformName + "' and  Stream='" + Stream + "'  and Testname='" + TestName + "' and Status='" + str(Status) + "';"
        print sql
        count = self.getValue(sql)  
        if count > 0:
            exists = True
        return exists


    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # Read the excel sheet
    #-------------------------------------------------------------------------------------------
    def insertData(self,exSheet,tableName):
        
        #Open a workbook 
        workbook = xlrd.open_workbook(exSheet)

        #Loads only current sheets to memory
        workbook = xlrd.open_workbook(exSheet, on_demand = True)

        # Load a specific sheet by name
        sheet = workbook.sheet_by_name('Sheet1')

        #Reading data from the excel sheet
        PlatformName = sheet.cell(0,2).value.split('-')[1].split('TypeScript')[0]
        Stream = sheet.cell(2,1).value
        Date = sheet.cell(3,1).value

        month = Date.split(':')[0]
        date = Date.split(':')[1]
        year = Date.split(':')[2]

        Date = month + ' ' + date + ' ' + year
        
        Date = datetime.strptime(Date,'%m %d %Y')
        
        rowCount = sheet.nrows
        TotalTests = rowCount - 8
     
        for j in range(TotalTests):
            
            TestName = sheet.cell(8+j,0).value
            Status = sheet.cell(8+j,4).value
        
            #Checks if the data already exists
            if not self.dataExists(tableName,Date,PlatformName,Stream,TestName,Status):
                #Inserts data in db if it doesn't exists
                sql = "INSERT INTO " +tableName+ "(Date,Platform,Stream,TestName,Status) VALUES ('" + str(Date) + "','" + str(PlatformName) + "','" + str(Stream) + "','" + str(TestName) + "','" + str(Status) + "');"
                self.executeQuery(sql)
                db.commit()
        
       
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir                       12/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--reportPath", help="Path to the output_report csv created after the run", required=True)
parser.add_argument("--tableName", help="Name of the table you want to create for gtest repeat", required=True)

args = parser.parse_args()

report = args.reportPath
tableName = args.tableName


#Verifying if the report exists
if not os.path.exists(report):
    print 'The path provided for the excel report is not valid. Exiting.'
    exit()
      
#Database connectivity
obj = WriteGTestRepeatDataToSql()
db , cursor = obj.databaseConnectivity()

# Create Table if its not presesnt in the database
TableName = obj.getTableName(tableName)

if not TableName:
    obj.createTable(tableName)
else:
    print 'Table ' + tableName + ' already exists in the database.'


#Reading the data from the csv
DateOfExec = obj.insertData(report,tableName)
cursor.close()
db.close()