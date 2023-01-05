import pyodbc, os, sys, argparse, xlrd , math
from datetime import datetime

class WriteUnitTestDataToSql:

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    #-------------------------------------------------------------------------------------------
    def __init__(self):
        self.server = 'isbprddb01'
        self.database = 'ImodelTools'
        self.username = 'sa'
        self.password = 'qwe123!@#'


    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # Python Connectivity to SQL server
    #-------------------------------------------------------------------------------------------
    def databaseConnectivity(self):
        print 'Connecting....'
        conn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        print 'connected...'
        cursor = conn.cursor()
        return conn, cursor

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
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
    # bsimethod                                     Maha Nasir                        09/2018
    # To create an archive table in the database
    #-------------------------------------------------------------------------------------------
    def createTable(self,TableName):
        
        sql = 'CREATE TABLE ' + TableName + ' ([Date] DATETIME, [Platform] NVARCHAR(25), [Device] NVARCHAR(25), [Branch] NVARCHAR(25), [TestCount] INTEGER, [Passing] INTEGER, [Failing] INTEGER, [Disabled] INTEGER)'
        self.executeQuery(sql)

        db.commit()
        print 'Table ' + TableName + ' successfully created.'
        
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
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
    # bsimethod                                     Maha Nasir                       09/2018
    #-------------------------------------------------------------------------------------------
    def getValue(self, query):     
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1
    
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    #-------------------------------------------------------------------------------------------
    def dataExists(self,tableName,Date,Platform,Device,Branch,TestCount,Passing,Failing,Disabled):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE Date='" + Date + "' and Platform='" + Platform + "' and Device='" + Device + "' and  Branch='" + Branch + "' and  TestCount='" + str(TestCount) + "' and Passing='" + str(Passing) + "' and Failing= '"+ str(Failing) +"' and Disabled = '" + str(Disabled) + "';"
        count = self.getValue(sql)  
        if count > 0:
            exists = True
        return exists
    
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # Read the excel sheet
    #-------------------------------------------------------------------------------------------
    def insertData(self,exSheet,tableName,Stream):
        
        #Open a workbook 
        workbook = xlrd.open_workbook(exSheet)

        #Loads only current sheets to memory
        workbook = xlrd.open_workbook(exSheet, on_demand = True)

        # Load a specific sheet by name
        sheet = workbook.sheet_by_name('query')

        rowCount = sheet.nrows

        for j in range(rowCount - 1):

            BranchName = sheet.cell(1+j,0).value
            Platform = sheet.cell(1+j,1).value
            Device = sheet.cell(1+j,2).value
            DateTime = datetime(*xlrd.xldate_as_tuple(sheet.cell(1+j,3).value, workbook.datemode))
            Date = DateTime.strftime("%m/%d/%y")
            TotalTests = int(sheet.cell(1+j,4).value)
            PassingTests = int(sheet.cell(1+j,5).value)
            FailingTests = int(sheet.cell(1+j,6).value)
            DisabledTests = int(sheet.cell(1+j,7).value)


            #Checks if the data already exists
            if not self.dataExists(tableName,Date,Platform,Device,BranchName,TotalTests,PassingTests,FailingTests,DisabledTests):

                #Inserts data in db if it doesn't exists
                sql = "INSERT INTO " +tableName+ "(Date,Platform,Device,Branch,TestCount,Passing,Failing,Disabled) VALUES ('" + Date + "','" + str(Platform) + "','" + str(Device) + "','" + str(BranchName) + "','" + str(TotalTests) + "','" + str(PassingTests) + "','" + str(FailingTests) + "','" + str(DisabledTests) + "');"
                self.executeQuery(sql)
                db.commit()

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir                       09/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--streamName", help="The stream name for which the job is being run", required=True)
parser.add_argument("--reportPath", help="Path to the output_report csv created after the run", required=True)
parser.add_argument("--tableName", help="Name of the table you want to create", required=True)

args = parser.parse_args()

stream = args.streamName
report = args.reportPath
tableName = args.tableName

#Verifying if the report exists
if not os.path.exists(report):
    print 'The path provided for the excel report is not valid. Exiting.'
    exit()
      
#Database connectivity
obj = WriteUnitTestDataToSql()
db , cursor = obj.databaseConnectivity()

# Create Table if its not presesnt in the database
TableName = obj.getTableName(tableName)

if not TableName:
    obj.createTable(tableName)
else:
    print 'Table ' + tableName + ' already exists in the database.'

#Reading the data from the csv
obj.insertData(report,tableName,stream)
cursor.close()
db.close()