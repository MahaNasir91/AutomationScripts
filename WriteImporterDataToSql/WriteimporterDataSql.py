import pyodbc, os, sys, argparse, csv


class WriteDataToSql:

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # -------------------------------------------------------------------------------------------
    def __init__(self):
        self.server = 'isbprddb01'
        self.database = 'ItgImportersmoke'
        self.username = 'sa'
        self.password = 'qwe123!@#'
    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # Python Connectivity to SQL server
    # -------------------------------------------------------------------------------------------
    def databaseConnectivity(self):
        print 'Connecting....'
        conn = pyodbc.connect(
            'DRIVER={SQL Server Native Client 11.0};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        print 'connected...'
        cursor = conn.cursor()
        return conn, cursor

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # To execute asql query
    # -------------------------------------------------------------------------------------------
    def executeQuery(self, query):
        try:
            print 'Executing query: ' + query
            cursor.execute(query)

        except pyodbc.Error as e:
            print "An error occurred:", e.args[0]
            print "The command was: ", query
            exit()

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                        09/2018
    # To create an archive table in the database
    # -------------------------------------------------------------------------------------------
    def createTable(self, TableName):

        sql = 'CREATE TABLE ' + TableName + ' ([DateTime] DATETIME2, [DgnName] VARCHAR(300), [SchemaName] VARCHAR(100),[ShouldFail] VARCHAR(25), [Result] NVARCHAR(25), [Notes] NVARCHAR(600), [DgnSizeInMB] FLOAT, [BimSizeInMB] FLOAT, [Elements] INT, [Time] INT,[StreamName] NVARCHAR(25),[Version] VARCHAR(100))'
        self.executeQuery(sql)

        db.commit()
        print 'Table ' + TableName + ' successfully created.'

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    # -------------------------------------------------------------------------------------------
    def getTableName(self, TableName):
        tableName = ""
        try:
            sql = "SELECT * FROM information_schema.tables WHERE table_type = 'base table' AND table_name=?"
            cursor.execute(sql, TableName)
            for row in cursor:
                tableName = row[0]

        except pyodbc.Error as e:
            print "An error occurred:", e.args[0]
            print "The command was: ", sql
            exit()

        return tableName

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    # -------------------------------------------------------------------------------------------
    def getValue(self, query):
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha.Nasir    09/2018
    # -------------------------------------------------------------------------------------------
    def dataExists(self, tableName, Date, DgnName, SchemaName, ShouldFail, Result, Notes, DgnSize, BimSize,replacelement,replacetime, Stream,allLogs):
        exists = False
        count = 0
        sql = "SELECT count(*) FROM " + tableName + " WHERE DateTime='" + Date + "' and  DgnName='" + DgnName + "'  and  SchemaName='" + SchemaName + "' and  ShouldFail='" + ShouldFail + "' and Result='" + Result + "' and Notes= '" + Notes + "' and DgnSizeInMB = '" + DgnSize + "' and BimSizeInMB = '" + BimSize +"' and Version = '" + allLogs +  "'and Elements = '" + replacelement + "'and time = '" + replacetime +"' and StreamName = '" + Stream +"';"
        count = self.getValue(sql)
        if count > 0:
            exists = True
        return exists

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    # -------------------------------------------------------------------------------------------
    def readDatasetCsv(self, datasetCsv, elementsCsv):

        dict = {}
        dict2 = {}
        # Reading the csv
        csvfile = open(datasetCsv, 'r')
        reader = csv.reader(csvfile, delimiter=',')
        csvfile = open(elementsCsv, 'r')
        reader.next()
        reader2 = csv.reader(csvfile, delimiter=',')
        #reader2.next()
        with open('D:\\fish\\PowerBi\\version.csv') as my_file:
            for line in my_file:
                allLogs = line
                allLogs = allLogs.rstrip("\x00\n\r")
                allLogs = allLogs.rstrip()

        for row in reader:
            dgnName = row[0]
            schemaName = row[3]
            shouldFail = row[1]
            dgnSize = row[6]
            dgnSize = dgnSize.rstrip("\n\r")

            if dgnSize.find('KB') != -1:
                dgnSize = str(float(dgnSize.split(' ')[0]) / 1000)

            elif dgnSize.find('MB') != -1:
                dgnSize = dgnSize.split(' ')[0]

            dict[dgnName] = schemaName, dgnSize, shouldFail
        for row in reader2:
            dgnName2 = row[0].replace('ibim', 'dgn')
            bingo = dict[dgnName2]
            elements = row[1]
            re = elements.replace("element", "")
            time = row[2]
            rt = time.replace("millisecs", "")
            dict2[dgnName2] = bingo[0], bingo[1], bingo[2], re, rt,allLogs

        return dict2

    # -------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                       09/2018
    # -------------------------------------------------------------------------------------------
    def insertData(self, csv_path, tableName, Stream, datasetCsv,elementsCsv):

        dict2 = self.readDatasetCsv(datasetCsv,elementsCsv)
        schemaName = ''
        shouldFail = ''
        dgnSize = '0'
        replacelement = ''
        replacetime = ''
        allLogs=''

        # Reading the csv
        csvfile = open(csv_path, 'r')
        reader = csv.reader(csvfile, delimiter=',')
        reader.next()
        for row in reader:
            Date = row[0]
            DgnName = row[1]
            Result = row[2]
            Notes = row[3]
            if Notes.find("']") != -1:
                Notes = Notes.split("']")[0]
            BimSize = row[4]

            # Finding schema name for the respective dgn
            for k, v in dict2.iteritems():
                if k == DgnName:
                    schemaName = v[0]
                    dgnSize = v[1]
                    shouldFail = v[2]
                    replacelement=v[3]
                    replacetime=v[4]
                    allLogs=v[5]

            # Checks if the data already exists
            if not self.dataExists(tableName, Date, DgnName, schemaName, shouldFail, Result, Notes, dgnSize, BimSize,replacelement,replacetime,
                                   Stream,allLogs):
                # Inserts data in db if it doesn't exists
                sql = "INSERT INTO " + tableName + "(DateTime,DgnName,SchemaName,ShouldFail,Result,Notes,DgnSizeInMB,BimSizeInMB,Version,Elements,Time,StreamName) VALUES ('" + Date + "','" + str(
                    DgnName) + "','" + str(schemaName) + "','" + str(shouldFail) + "','" + str(Result) + "','" + str(
                    Notes) + "'," + dgnSize + "," + BimSize + ",'" + allLogs + "','" + replacelement + "','" + replacetime + "','" + str(Stream) + "');"
                self.executeQuery(sql)
                db.commit()


# -------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir                       09/2018
# -------------------------------------------------------------------------------------------
# Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--streamName", help="The stream name for which the job is being run", required=True)
parser.add_argument("--reportPath", help="Path to the output_report csv created after the run", required=True)
parser.add_argument("--datasetCsvPath", help="Path to the dataset csv", required=True)
parser.add_argument("--elmentsCsvPath", help="Path to the dataset csv", required=True)
parser.add_argument("--tableName", help="Name of the table you want to create", required=True)

args = parser.parse_args()

stream = args.streamName
report = args.reportPath
datasetCsv = args.datasetCsvPath
elementsCsv = args.elmentsCsvPath
tableName = args.tableName

# Verifying if the report exists
if not os.path.exists(report):
    print 'The path provided for the Output_report.csv not valid. Exiting.'
    exit()

# Verifying if the dataset csv exists
if not os.path.exists(datasetCsv):
    print 'The path provided for the dataset csv is not valid. Exiting.'
    exit()

# Database connectivity
obj = WriteDataToSql()
db, cursor = obj.databaseConnectivity()

# Create Table if its not presesnt in the database
TableName = obj.getTableName(tableName)

if not TableName:
    obj.createTable(tableName)
else:
    print 'Table ' + tableName + ' already exists in the database.'

# Reading the data from the csv
obj.insertData(report, tableName, stream, datasetCsv,elementsCsv)
cursor.close()
db.close()