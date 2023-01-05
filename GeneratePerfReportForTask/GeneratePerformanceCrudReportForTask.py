#--------------------------------------------------------------------------------------
#
#     $Source: Performance/ElementCRUD/ModifiedPerformanceScripts/GeneratePerformanceCrudReportForTask.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
import sys, sqlite3, xlsxwriter, datetime, os, argparse, subprocess, time, shutil , csv, fnmatch , json
from os.path import normpath, basename
from pprint import pprint

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    05/2018
#-------------------------------------------------------------------------------------------
def GetLatestFolder(folder):
    list=[]
    for root in os.listdir(folder):
        if fnmatch.fnmatch(root, '[0-9]*-[0-9]*-[0-9]*'):
            list.append(root)

    latestFolder = list[-1]
    print '\nLast Element of list:' + latestFolder
    return latestFolder

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    06/2018
#-------------------------------------------------------------------------------------------
def FindFile(directory, subsringToMatch):
    for file in os.listdir(directory):
        if file.startswith(subsringToMatch):
            print 'File Name:' + file
            return file

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    06/2018
#-------------------------------------------------------------------------------------------
def RunCommand(cmd):
    result = os.system(cmd)
    if (result != 0):
        print 'Error executing command: ' + cmd + ' .Exiting.'
        exit(1)

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def getMaxDate(cursor, stream, platform='Winx64'):
    buffer = 'SELECT Max(Date) FROM Archive WHERE Stream="' + stream + '" AND Platform="' + platform + '"'
    try:
        cursor.execute(buffer)
        for row in cursor:
            return row[0]
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer  


#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def add_main_header(ws):
    global latestDate
    conn = sqlite3.connect(archiveDbPath)
    c = conn.cursor()
    buffer = 'SELECT Stream, Date FROM Archive WHERE Date=(SELECT MAX(Date) FROM Archive WHERE Stream="' +activeStream+ '")'
    try:
        c.execute(buffer)
        for row in c:
            stream = row[0]
            lastDate = row[1]
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer

    ws.write(0,6, 'Performance Analysis', headingFormat2)
    ws.write(2,4, 'Stream:', headingFormat2)
    ws.write(2,5, stream, headingFormat2)
    ws.write(2,8, 'Dated:', headingFormat2)
    ws.write(2,9, lastDate, headingFormat2)
    latestDate = lastDate
    
    startRow = 5
    ws.write(startRow,1, 'Click to view Charts', headingFormat2)
    notesCol = 9
    ws.write(startRow, notesCol, 'Notes', headingFormat2)
    ws.write(startRow+1, notesCol, 'All Charts show "Speed" which means operations per second.')
    
    ws.write(startRow+3, notesCol, 'Db Sizes:')
    ws.write(startRow+4, notesCol, 'Small = ' + str(SmallDbSize) + ' instances')
    ws.write(startRow+5, notesCol, 'Medium = ' + str(MediumDbSize) + ' instances')
    ws.write(startRow+6, notesCol, 'Large = ' + str(LargeDbSize) + ' instances')

    ws.write(startRow+8, notesCol, 'Element Hierarchy')
    ws.write(startRow+9, notesCol, element1+' derives from PhysicalElement. Has 3 properties')
    ws.write(startRow+10, notesCol, element2+' derives from '+element1+'. Has 3 properties')
    ws.write(startRow+11, notesCol, element3+' derives from '+element2+'. Has 3 properties')
    ws.write(startRow+12, notesCol, mostComplexElementName+' derives from '+element3+'. Has 3 properties')
    
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def add_header(ws, startCol, startRow, heading):
    ws.write(0,6, heading, headingFormat)
    link_format = wb.add_format({'color': 'blue', 'underline': 1})
    ws.write_url(0, 0, 'internal:Main!B7', link_format, "Home")
    
    ws.set_column(startCol,startCol+6,10)
    ws.write(startRow,startCol, "Stream")
    ws.write(startRow,startCol+1, "Date")
    ws.write(startRow,startCol+2, "Element")
    ws.write(startRow,startCol+3, "Db")
    ws.write(startRow,startCol+4, "API")
    ws.write(startRow,startCol+5, "Operation")
    ws.write(startRow,startCol+6, "Speed")

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def add_data(ws, startRow, startCol, row):
    numFormat = wb.add_format()
    numFormat.set_num_format('#,#')
        
    ws.write(startRow, startCol, row[4])
    ws.write(startRow, startCol+1, row[5])
    ws.write(startRow, startCol+2, row[1])
    ws.write(startRow, startCol+3, row[2])
    ws.write(startRow, startCol+4, row[3])
    ws.write(startRow, startCol+5, row[0])
    ws.write(startRow, startCol+6, row[6], numFormat)

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def execute_command(cursor, buffer, ws, startCol, startRow):
    try:
        cursor.execute(buffer)
        for row in cursor:
            add_data(ws, startRow+1, startCol, row)
            startRow = startRow + 1
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print "The command was: ", buffer
    return startRow

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def create_chart(title, type, cats, vals, xAxisName, yAxisName, chartName, labels):
    chart = wb.add_chart({'type': type ,
                          'name': chartName})
    chart.add_series({'name' : 'None',
                      'categories' : '=(' + cats + ')',
                      'values': '=(' + vals + ')',
                      'data_labels': {'value': labels}})
    chart.set_legend({'none': True})
    chart.set_title({'name': title})
    chart.set_x_axis({'name' : xAxisName,
                      'major_gridlines': {'visible': False}})
    chart.set_y_axis({'name' : yAxisName})
    chart.set_size({'width': 500, 'height': 275})
    return chart

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def chart_Element4_LargeDb_Latest(SHN, Heading):
    ws = wb.add_worksheet(SHN)
    startCol = 9
    startRow = chartRow = 2
    add_header(ws, startCol, startRow, Heading)
    
    #Read Data from Db
    conn = sqlite3.connect(archiveDbPath)
    c = conn.cursor()
    for operation in operations:
        print operation
        buffer = os.path.join('SELECT * FROM Archive WHERE Element="'+mostComplexElementName+'" AND DbSize="Large" AND API="ElementAPI" AND Platform="Winx64" AND Device="Desktop" AND Stream="' + activeStream + '" AND Date="' + getMaxDate(c, activeStream)+ '" AND Operation="' + operation + '"')
        startRow = execute_command(c, buffer, ws, startCol, startRow)
    conn.close()
    #Draw the chart
    chart = create_chart(mostComplexElementName+' - LargeDb - ' + CurrentDate, 'bar', SHN + '!$O$4:$O$7', SHN + '!$P$4:$P$7', 'Speed (Operations per second)', '', 'Elm4LgDbLatest', 1)
    ws.insert_chart(chartRow, 0, chart)

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    10/2017
#-------------------------------------------------------------------------------------------
def chart_Element4_AllDbs_Latest(SHN, Heading):
    ws = wb.add_worksheet(SHN)
    startCol = 16
    startRow = chartRow = 2
    add_header(ws, startCol, startRow, Heading)

    #Read Data from Db
    conn = sqlite3.connect(archiveDbPath)
    c = conn.cursor()
    for operation in operations:
        buffer = os.path.join('SELECT * FROM Archive WHERE Element="'+mostComplexElementName+'" AND API="ElementAPI" AND Platform="Winx64" AND Device="Desktop" AND Stream="' + activeStream + '" AND Date="' + getMaxDate(c, activeStream)+ '" AND Operation="' + operation + '"')
        startRow = execute_command(c, buffer, ws, startCol, startRow)
    conn.close()

    #Draw the chart
    chart = create_chart(mostComplexElementName+' - Insert', 'line', SHN + '!$T$4:$T$6', SHN + '!$W$4:$W$6', 'Db Size', 'Speed (Operations per second)', '', 1)
    ws.insert_chart(chartRow, 0, chart)
    chart = create_chart(mostComplexElementName+' - Read', 'line', SHN + '!$T$7:$T$9', SHN + '!$W$7:$W$9', 'Db Size', 'Speed (Operations per second)','', 1)
    ws.insert_chart(chartRow, startCol / 2, chart)
    chart = create_chart(mostComplexElementName+' - Update', 'line', SHN + '!$T$10:$T$12', SHN + '!$W$10:$W$12', 'Db Size','Speed (Operations per second)', '', 1)
    ws.insert_chart(chartRow + 14, 0, chart)
    chart = create_chart(mostComplexElementName+' - Delete', 'line', SHN + '!$T$13:$T$15', SHN + '!$W$13:$W$15', 'Db Size','Speed (Operations per second)', '', 1)
    ws.insert_chart(chartRow + 14, startCol / 2, chart)
    
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--scriptsRoot", help="Path to the dgndbtesting repository", required=True)
parser.add_argument("--workspaceRoot", help="Workspace/Output root", required=True)
parser.add_argument("--archiveDb", help="Path to the dgndbtesting repo", required=True)
parser.add_argument("--streamName", help="Specify stream name ie bim0200,bim0200dev etc", required=True)

args = parser.parse_args()

ScriptsRoot = args.scriptsRoot
WorkspaceRoot = args.workspaceRoot
archiveDbPath = args.archiveDb
activeStream = args.streamName

if (not os.path.exists(WorkspaceRoot)):
    print 'Worksapce/output root path is not valid. Please provide a valid path. Exiting'
    exit(1)
    
if (not os.path.exists(archiveDbPath)):
    print 'ArchiveDb not found on the given path. Exiting'
    exit(1)

#Global variables
element1 = 'PerfElement'
element2 = 'PerfElementSub1'
element3 = 'PerfElementSub2'
mostComplexElementName = 'PerfElementSub3'

#Gets the latest date folder in the directory
LatestFolder = GetLatestFolder(WorkspaceRoot)
LatestFolderPath = os.path.join(WorkspaceRoot, LatestFolder)

#Get the analysis report from the latest folder 
AnalysisReport = FindFile(LatestFolderPath, 'Analysis')
if AnalysisReport is None:
    print 'Analysis report no found. Exiting.'
    exit(1)

CurrentDate = AnalysisReport.split('_')[1]
BenchmarkDate = AnalysisReport.split('_')[2].split('.')[0]

AnalysisReportPath = os.path.join(LatestFolderPath , AnalysisReport)

#Reading json file and storing the Db sizes in a list
JsonFile = os.path.join(LatestFolderPath , 'ElementCrud.json')
if (not os.path.exists(JsonFile)):
    print 'Couldnt find the json file. Exiting'
    exit(1)
    
with open(JsonFile) as Json:
    data = json.load(Json)

requirements = data['CrudTestRequirement']

list = []
for iter in requirements:
    DbSize = iter['InitialCount']
    list.append(DbSize)

if (len(list) != 3):
    print 'Please provide atleast 3 db sizes to be set as small, medium and large Db.'
    exit()
    
list.sort()

SmallDbSize = list[0]
MediumDbSize = list[1]
LargeDbSize = list[2]

#Adding the data of the performance runs in the database
cmd = 'python ' + os.path.join(ScriptsRoot , 'Performance', 'ElementCRUD', 'ModifiedPerformanceScripts' , 'AddDataToArchiveDb.py') + ' ' + AnalysisReportPath  + ' ' +archiveDbPath + ' ' + str(SmallDbSize) + ' ' + str(MediumDbSize) + ' ' + str(LargeDbSize)
RunCommand(cmd)

#Generating chart
operations = ["Insert", "Select", "Update", "Delete"]
PerfSummaryPath = os.path.join(LatestFolderPath, 'PerfSummary.xlsx')
wb = xlsxwriter.Workbook(PerfSummaryPath)

headingFormat = wb.add_format({'color': 'blue',
                             'bold': 1,
                             'size': 12,
                             'align': 'left'})

headingFormat2 = wb.add_format({'color': 'green',
                             'bold': 1,
                             'size': 14,
                             'align': 'left'})

SheetName = ["ForLargeDb",
             "ImpactOfDbSize"]

SheetHeading = [mostComplexElementName+'    - LargeDb - Latest',
                mostComplexElementName+'    - Impact of Db size - Latest']

ws = wb.add_worksheet('Main')
add_main_header(ws)

for i in range(len(SheetName)):
    ws.write_url(6+i, 1, 'internal:' + SheetName[i] + '!A1', headingFormat, SheetHeading[i])
    
print '*** Adding Chart: Element4 in LargeDb - Latest'
chart_Element4_LargeDb_Latest(SheetName[0], SheetHeading[0])

print '*** Adding Chart: Element4 in All Dbs - Latest'
chart_Element4_AllDbs_Latest(SheetName[1], SheetHeading[1])

wb.close()

#Upload performace summary on sharePoint
if (not os.path.exists(PerfSummaryPath)):
    print 'Performance Summary report not created. Exiting.'
    exit(1)
    
UploadScript = os.path.join(ScriptsRoot , 'CommonTasks' , 'UploadFile.py')
cmd = UploadScript + " " +PerfSummaryPath+ "  Main E:\dgndbtestingscripts\CommonTasks"
RunCommand(cmd)