import pyodbc, os, sys, argparse, csv

class WriteDataToSql:

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
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
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
        
        sql = 'CREATE TABLE ' + TableName + ' ([DateTime] DATETIME2, [DgnName] VARCHAR(300), [Result] NVARCHAR(25), [Notes] NVARCHAR(600), [BimSizeInMB] FLOAT, [ViewsStatus] NVARCHAR(25), [StreamName] NVARCHAR(25))'
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
    # bsimethod                                     Maha Nasir                      09/2018
    #-------------------------------------------------------------------------------------------
    def dataExists(self,tableName,Date,DgnName,Result,Notes,BimSize,ViewStatus,Stream):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE DateTime='" + Date + "' and  DgnName='" + DgnName + "' and Result='" + Result + "' and Notes= '"+ Notes +"' and BimSizeInMB = '" + BimSize + "' and ViewsStatus = '" + ViewStatus + "' and StreamName = '" + Stream + "';"
        count = self.getValue(sql)  
        if count > 0:
            exists = True
        return exists

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    #-------------------------------------------------------------------------------------------
    def readDataFromViewVerCsv(self,ViewVerCsv):

        dict = {}
        #Reading the csv
        csvfile = open(ViewVerCsv, 'r')
        reader = csv.reader(csvfile, delimiter=',')
        reader.next()
        for row in reader:
            dgnName = row[0]
            viewStatus = row[1]
         
            dict[dgnName] = viewStatus

        return dict
        
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    #-------------------------------------------------------------------------------------------
    def insertData(self,csv_path,tableName,Stream,vvCsv):

        dict = self.readDataFromViewVerCsv(vvCsv)
        
        #Reading the csv
        ViewStatus = ''
        csvfile = open(csv_path, 'r')
        reader = csv.reader(csvfile, delimiter=',')
        reader.next()
        for row in reader:
            Date = row[0]
            DgnName = row[1]
            Result = row[2]
            if Result == 'FAIL':
                continue
            Notes = row[3]
            if Notes.find("']") != -1:
                Notes = Notes.split("']")[0]
            BimSize = row[4]

            #Finding schema name for the respective dgn
            for k,v in dict.iteritems():
                if k.split('_')[0] == DgnName.split('_')[0]:
                    ViewStatus = v.strip()

            #Checks if the data already exists
            if not self.dataExists(tableName,Date,DgnName,Result,Notes,BimSize,ViewStatus,Stream):
                #Inserts data in db if it doesn't exists
                sql = "INSERT INTO " +tableName+ "(DateTime,DgnName,Result,Notes,BimSizeInMB,ViewsStatus,StreamName) VALUES ('" + Date + "','" + str(DgnName) + "','" + str(Result) + "','" + str(Notes) + "'," + BimSize + ",'" + str(ViewStatus) + "','" + str(Stream)+"');"
                self.executeQuery(sql)
                db.commit()
              
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir                       09/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--streamName", help="The stream name for which the job is being run", required=True)
parser.add_argument("--reportPath", help="Path to the output_report csv created after the run", required=True)
parser.add_argument("--viewVerCsvPath", help="Path to the ViewVerification csv created after the test", required=True)
parser.add_argument("--tableName", help="Name of the table you want to create", required=True)

args = parser.parse_args()

stream = args.streamName
report = args.reportPath
viewCsv = args.viewVerCsvPath
tableName = args.tableName

#Verifying if the report exists
if not os.path.exists(report):
    print 'The path provided for the Output_report.csv not valid. Exiting.'
    exit()

#Verifying if the dataset csv exists
if not os.path.exists(viewCsv):
    print 'The path provided for the dataset csv is not valid. Exiting.'
    exit()
        
#Database connectivity
obj = WriteDataToSql()
db , cursor = obj.databaseConnectivity()

# Create Table if its not presesnt in the database
TableName = obj.getTableName(tableName)

if not TableName:
    obj.createTable(tableName)
else:
    print 'Table ' + tableName + ' already exists in the database.'
    
#Reading the data from the csv
obj.insertData(report,tableName,stream,viewCsv)
cursor.close()
db.close()