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
        
        sql = 'CREATE TABLE ' + TableName + ' ([Date] DATETIME, [Platform] NVARCHAR(25), [Stream] NVARCHAR(25), [Component] NVARCHAR(100), [Passing] INT, [Failing] INT, [Disabled] INT, [PassingWithRepeat] INT, [FailingWithRepeat] INT, [DisabledWithRepeat] INT , [NoOfRepeats] INT , [FailingTestDetails] NVARCHAR(1000))'
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
    def dataExists(self,tableName,Date,PlatformName,Stream,ComponentName,PassingTests,FailingTests,DisabledTests):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE Date='" + str(Date) + "' and Platform='" + PlatformName + "' and  Stream='" + Stream + "'  and Component='" + ComponentName + "' and Passing='" + str(PassingTests) + "' and Failing= '"+ str(FailingTests) +"' and Disabled = '" + str(DisabledTests) + "';"
        count = self.getValue(sql)  
        if count > 0:
            exists = True
        return exists

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       12/2018
    #-------------------------------------------------------------------------------------------
    def dataExistsForFailedTests(self,tableName,Date,PlatformName,ComponentName,FailingTestsString):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE Date='" + str(Date) + "' and Platform='" + PlatformName + "' and Component='" + ComponentName + "' and FailingTestDetails = '" + str(FailingTestsString) + "';"
        count = self.getValue(sql)  
        if count > 0:
            exists = True
        return exists
    

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # Read the excel sheet
    #-------------------------------------------------------------------------------------------
    def insertData(self,exSheet,tableName,PlatformName):
        
        #Open a workbook 
        workbook = xlrd.open_workbook(exSheet)

        #Loads only current sheets to memory
        workbook = xlrd.open_workbook(exSheet, on_demand = True)

        # Load a specific sheet by name
        sheet = workbook.sheet_by_name('Summary')

        #Reading data from the excel sheet
        Stream = sheet.cell(0,7).value
        Date = sheet.cell(1,7).value

        month = Date.split('/')[0]
        date = Date.split('/')[1]
        year = Date.split('/')[2]

        Date = month + ' ' + date + ' ' + year
        
        Date = datetime.strptime(Date,'%m %d %Y')

        rowCount = sheet.nrows
        iter = rowCount - 9
     
        for j in range(iter):
            ComponentName = sheet.cell(9+j,0).value
            
            PassingTests = sheet.cell(9+j,3).value
            if(not PassingTests):
                PassingTests = 0
            else:
                PassingTests = int(PassingTests)
                
            FailingTests = sheet.cell(9+j,4).value
            if(not FailingTests):
                FailingTests = 0
            else:
                FailingTests = int(FailingTests)
                
            DisabledTests = sheet.cell(9+j,5).value
            if(not DisabledTests):
                DisabledTests = 0
            else:
                DisabledTests = int(DisabledTests)
                
            PassingTestsWithRepeat = sheet.cell(9+j,7).value
            if(not PassingTestsWithRepeat):
                PassingTestsWithRepeat = 0
            else:
                PassingTestsWithRepeat = int(PassingTestsWithRepeat)
                
            FailingTestsWithRepeat = sheet.cell(9+j,8).value
            if(not FailingTestsWithRepeat):
                FailingTestsWithRepeat = 0
            else:
                FailingTestsWithRepeat = int(FailingTestsWithRepeat)
                
            DisabledTestsWithRepeat = sheet.cell(9+j,9).value
            if(not DisabledTestsWithRepeat):
                DisabledTestsWithRepeat = 0
            else:
               DisabledTestsWithRepeat = int(DisabledTestsWithRepeat)

            NoOfRepeat = sheet.cell(7,7).value.split(' ')[-1]
            
            #Checks if the data already exists
            if not self.dataExists(tableName,Date,PlatformName,Stream,ComponentName,PassingTests,FailingTests,DisabledTests):
                #Inserts data in db if it doesn't exists
                sql = "INSERT INTO " +tableName+ "(Date,Platform,Stream,Component,Passing,Failing,Disabled,PassingWithRepeat,FailingWithRepeat,DisabledWithRepeat,NoOfRepeats) VALUES ('" + str(Date) + "','" + str(PlatformName) + "','" + str(Stream) + "','" + str(ComponentName) + "','" + str(PassingTests) + "','" + str(FailingTests) + "','" + str(DisabledTests) + "','" + str(PassingTestsWithRepeat) + "','" + str(FailingTestsWithRepeat) + "','" + str(DisabledTestsWithRepeat) +"','" + str(NoOfRepeat)+"');"
                self.executeQuery(sql)
                db.commit()

        return Date

     
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        12/2018
    # Read the excel sheet
    #-------------------------------------------------------------------------------------------
    def insertFailingTests(self,exSheet,tableName,Date):

        #Open a workbook 
        workbook = xlrd.open_workbook(exSheet)

        #Loads only current sheets to memory
        workbook = xlrd.open_workbook(exSheet, on_demand = True)
        
        # Loading failing test details sheet
        sheet1 = workbook.sheet_by_name('Failing Tests Detail')

        #Reading data from the sheet
        rowCount1 = sheet1.nrows
        List = []
        
        #Reading the failing tests of each component from the sheet and storing them into the database
        for i in range(rowCount1):
            if(i==0):
                continue

            Comp_Name = sheet1.cell(i,0).value
            
            if(Comp_Name):
                TestName = sheet1.cell(i,3)
                List.append({'ComponentName':Comp_Name,'TestName':TestName})
                counter = i
                    
            else:
                Comp_Name = sheet1.cell(counter,0).value
                TestName = sheet1.cell(i,3)
                List.append({'ComponentName':Comp_Name,'TestName':TestName})               



        Dict = {}
        CompName = {item['ComponentName'] for item in List}
        for name in CompName:
            CompList = []
            for i in range(len(List)):
                ComponentName = List[i]['ComponentName']
                TestName = List[i]['TestName'].value.strip()

                if(name == ComponentName):
                    CompList.append(TestName)

            Dict[name]=CompList

            
        for item in Dict:
            count = 0
            FailingTestsString = ''
            CompName = item
            FailingTestList = Dict[item]
         
            for i in FailingTestList:
                FailingTestsString = FailingTestsString + i + '\n'
                
            if not self.dataExistsForFailedTests(tableName,Date,platformName,CompName,FailingTestsString):       
                sql = "UPDATE " +tableName+ " SET FailingTestDetails='" + str(FailingTestsString) + "' WHERE Component='" + str(CompName) + "';"
                self.executeQuery(sql)
                db.commit()
        
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir                       12/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--platform", help="Name of the platform for which you are running the Gtest", required=True)
parser.add_argument("--reportPath", help="Path to the output_report csv created after the run", required=True)
parser.add_argument("--tableName", help="Name of the table you want to create for gtest repeat", required=True)



args = parser.parse_args()

platformName = args.platform
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
DateOfExec = obj.insertData(report,tableName,platformName)
obj.insertFailingTests(report,tableName,DateOfExec)
cursor.close()
db.close()