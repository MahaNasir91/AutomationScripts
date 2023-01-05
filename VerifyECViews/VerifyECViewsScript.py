#--------------------------------------------------------------------------------------
#
#     $Source: DgnV8Conversion/ViewVerificationScript/VerifyECViewsScript.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
import os
import sys
import shutil
import time
import csv
import subprocess
import xlsxwriter
import argparse
#Common Scripts to be used by any task
scriptsDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
commonScriptsDir = os.path.join(scriptsDir, 'CommonTasks')
sys.path.append(commonScriptsDir)
    
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir             08/2017
#-------------------------------------------------------------------------------------------
def createDirectory(DirPath):
    print '\nCreating directory path: ' + DirPath
    if(os.path.exists(DirPath)):
        print '\nThe directory path already exists. Recreating it.'
        shutil.rmtree(DirPath, onerror = remove_readOnly)
    os.mkdir(DirPath)
    if(not os.path.exists(DirPath)):
        print '\nDirectory creation failed. Exiting.'
        sys.exit(1)
    else:
        print 'Directory created successfully.'
        
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir             08/2017
#-------------------------------------------------------------------------------------------
def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )
            
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir             08/2017
#-------------------------------------------------------------------------------------------
def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit(-1)
    else:
        print 'Ran task successfully.'

#-------------------------------------------------------------------------------------------
# bsimethod                                     Majd.Uddin    08/2017
#-------------------------------------------------------------------------------------------
def passfailCountFromCSV(csv_path):
    passCount = 0
    failCount = 0
    csvfile = open(csv_path, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    reader.next()
    for row in reader:
        if row[1].strip() == 'PASS':
            passCount += 1
        if row[1].strip() == 'FAIL':
            failCount += 1
    return passCount, failCount

#-------------------------------------------------------------------------------------------
# bsimethod                                     Majd.Uddin    08/2017
#-------------------------------------------------------------------------------------------
def getFormats(wb):
    headingFormat = wb.add_format({'color': 'blue', 'bold': 1, 'size': 16, 'align': 'center', 'text_wrap': 1})
    heading2 = wb.add_format({'color': 'brown', 'bold': 1, 'size': 12, 'text_wrap': 1})
    headingFormat.set_align('vcenter')
    linkFormat = wb.add_format({'color': 'blue', 'underline': True})
    percentFormat = wb.add_format({'num_format' : '0%'})
    numFormat = wb.add_format({'num_format': '#,##0.#0'})
    return {'heading1': headingFormat, 'heading2': heading2, 'link': linkFormat, 'percent': percentFormat, 'num': numFormat}

#-------------------------------------------------------------------------------------------
# bsimethod                                     Majd.Uddin    08/2017
#-------------------------------------------------------------------------------------------
def generatePieChart(wb, cats, vals, chartTitle, chartName):
    chart = wb.add_chart({'type': 'pie' ,
                          'name': chartName})
    chart.add_series({'name' : 'None',
                      'categories' : '=('+ cats + ')',
                      'values': '=(' + vals + ')',
                      'points': [
                                {'fill': {'color': 'green'}},
                                {'fill': {'color': 'orange'}},
                                ],
                      'data_labels': {'value': 1, 'position': 'center', 'font': {'color': 'white', 'bold': True}}})
    chart.set_title({'name': chartTitle ,
                    'name_font': {'color': 'blue'}})
    chart.set_size({'width': 372, 'height': 400})
    return chart
#-------------------------------------------------------------------------------------------
# bsimethod                                     Majd.Uddin             01/2018
#-------------------------------------------------------------------------------------------
def genReport(csvFilePath, streamName, CurrentDateFolderPath):
    print 'Csv file found. Continuing further execution.'
   
    #Creating and formatting excel sheet
    streamName = streamName.split('-')[0]
    ExcelSheetPath = os.path.join(CurrentDateFolderPath, streamName+'ViewVerificationSummary.xlsx')
    print 'ExcelSheet Path:' + ExcelSheetPath
    runDate = os.path.basename(CurrentDateFolderPath)
    if(os.path.exists(ExcelSheetPath)):
        os.remove(ExcelSheetPath)
    workBook = xlsxwriter.Workbook(ExcelSheetPath)
    ws = workBook.add_worksheet('Summary')
    formats = getFormats(workBook)
    ws.merge_range('C2:F2', 'Converter Report', formats['heading1'])
    ws.set_column(2,5, 12.5)
    ws.write(2,2, 'Stream', formats['heading2'])
    ws.write(2,3, streamName, formats['heading2'])
    ws.write(2,4, 'Date', formats['heading2'])
    ws.write(2,5, runDate, formats['heading2'])
    ws.write(4,3, 'Passing', formats['heading2'])

    pass_count, fail_count = passfailCountFromCSV(csvFilePath)
    
    ws.write(4,4,  pass_count, formats['heading2']) #Fixed size
    ws.write(5,3, 'Failing', formats['heading2'])
    ws.write(5,4, fail_count, formats['heading2']) #Fixed Size
    chart = generatePieChart(workBook, 'Summary!D5:D6', 'Summary!E5:E6', 'ViewVerify Summary - ' + streamName + ' - ' + runDate, 'SummaryChart')
    ws.insert_chart('C8', chart)
    ws.set_column(7,7, 30)
    ws.write(10,7, 'For Details, visit the following:', formats['heading2'])
    ws.write_url(11, 7, 'internal:Details!A1', formats['link'], "Details")


    #fill in details
    workSheet= workBook.add_worksheet('Details')
    workSheet.set_column(0,0,25)
    workSheet.set_column(1,1,10)
    format = workBook.add_format({'color': 'black', 'bold': 1, 'size': 12, 'align': 'center', 'text_wrap': 1})
    workSheet.write('A1', "BimName" , format)
    workSheet.write('B1', "Status" , format)
        
    #Reading data from Csv and writing it into Excel sheet
    csvFile = open(csvFilePath, 'r')
    reader = csv.reader(csvFile , delimiter=',')
    next(reader)#To skip header
    rowCount= 1
    for row in reader:
        BimName = row[0]
        Status = row[1]
        workSheet.write(rowCount, 0 , BimName)
        workSheet.write(rowCount, 1 , Status)
        rowCount = rowCount + 1

    workBook.close()

    return ExcelSheetPath
 

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir             08/2017
#-------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--workspaceRoot", help="Path of the workspace", required=True)
    parser.add_argument("--scriptsRoot", required=True) 
    parser.add_argument("--streamName", help="Name of the stream for which you want to run the conversion. If not given, it determines itself.") 

    args = parser.parse_args()

    WorkspaceRoot = args.workspaceRoot
    ScriptsRoot = args.scriptsRoot
    StreamName = args.streamName

    if StreamName == None:
        TeamConfigPath = os.path.join(os.getenv('SrcRoot'), 'teamConfig', 'treeConfiguration.xml')
        StreamName = FindStream.FindStreamDetails(TeamConfigPath)
        
    #Global variables
    StreamPath = os.path.join(WorkspaceRoot, 'DgnV8', StreamName)
    RemoteJenkinsJob ='Bim0200_Winx64_Desktop_BuildConverterAndConverterTests'
    JenkinsAuthenticationFilePath = 'C:\Users\Maha.Nasir\Desktop\Jenkins.auth'
    currentDate = time.strftime("%Y-%m-%d")
    CurrentDateFolderPath = os.path.join(StreamPath, currentDate)
    reportSummaryPath = os.path.join(WorkspaceRoot, 'DgnV8', 'Bim0200ViewVerificationSummary')
    outputDir = os.path.join(CurrentDateFolderPath, 'ConvertedFiles')
    customizedXml = os.path.join(ScriptsRoot, 'DgnV8Conversion', 'ViewVerificationScript', 'CustomizedXmlForViewVerification.xml')
    datasetFolderPath = os.path.join(WorkspaceRoot, 'DgnV8' , 'DataSet')
    DatasetCsvPath = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'ViewVerificationScript', 'DataSetForViewVerification.csv')
    commonTaskDir = os.path.join(ScriptsRoot ,'CommonTasks')
    OutputCsvPath = os.path.join(outputDir, "Output_report.csv")
    productName = 'DgnV8ConverterAndConverterTests'
    TableName = 'csdk_viewverification_archive'

    if(not os.path.exists(StreamPath)):
        print 'StreamPath doesnt exists. Please provide a valid stream name.'
        sys.exit(1)

    #Deleting folders in the directory to free disk space.
    cmd = commonTaskDir + "\DirectoryCleanup.py --dirPath " + StreamPath + ' --folderCount 3'
    runCommand(cmd)
    
    #Making a folder by the current date in the Bim0200-ViewVerification folder
    createDirectory(CurrentDateFolderPath)

    #Creating a folder in the current date folder to place the DgnV8Converter and DgnV8COnverterTests folders
    createDirectory(os.path.join(CurrentDateFolderPath, productName))
    
    #Creating a folder for the converted files in the current date folder
    createDirectory(outputDir)
        
    #Trigger job on jenkins to get & build Converter for Bim0200.
    cmd = ScriptsRoot + '\Jenkins\GenericGetnBuild.py --root ' + StreamPath + ' --productName ' + productName + ' --remoteJenkinsJob ' + RemoteJenkinsJob
    print '\nRunning command: ' + cmd + '\n'
    runCommand(cmd)

    #Verifying that the required exe's are present
    LatestConverterFolderPath = os.path.join(CurrentDateFolderPath, productName , 'DgnV8Converter')
    print 'Converter Folder Path: ' + LatestConverterFolderPath

    LatestConverterTestsFolderPath = os.path.join(CurrentDateFolderPath, productName, 'DgnV8ConverterTests')
    print 'ConverterTests Folder Path: ' + LatestConverterTestsFolderPath

    #Verifying DgnV8Converter.exe
    if(os.path.exists(LatestConverterFolderPath)):
        for file in os.listdir(LatestConverterFolderPath):
            if (file == 'DgnV8Converter.exe'):
                ConverterExePath = os.path.join(LatestConverterFolderPath , file)
                print 'ConverterExe Path is:' + ConverterExePath
    else:  
        print 'ConverterExe not found. Please provide a valid exe path. Exiting.'
        sys.exit()
        
    #Verifying DgnV8ConverterTests.exe
    if(os.path.exists(LatestConverterTestsFolderPath)):
        for file in os.listdir(LatestConverterTestsFolderPath):
            if (file == 'DgnV8ConverterTests.exe'):
                ConverterTestsExePath = os.path.join(LatestConverterTestsFolderPath , file)
                print 'ConverterTestsExe Path is:' + ConverterTestsExePath
    else:  
        print 'ConverterTestsExe not found. Please provide a valid exe path. Exiting.'
        sys.exit()
   
    #Conversion
    DgnConversionFolderPath = os.path.join(ScriptsRoot, 'DgnV8Conversion')
    cmd = DgnConversionFolderPath + '\BulkDgnV8Conversion.py' + ' --converter=' + ConverterExePath + ' --input=' +  datasetFolderPath + ' --output=' + outputDir + ' --custom=' + customizedXml
    runCommand(cmd)

    #Sorts the Passing/Failing files in their respective folders after conversion
    if (not os.path.exists(OutputCsvPath)):
        print 'Output csv not found. Exiting.'
        sys.exit()
        
    PostConversionScript = os.path.join(ScriptsRoot, 'Compatibility' , 'PostConversionSorting.py')
    cmd = PostConversionScript + ' ' + OutputCsvPath + ' ' + outputDir + ' ' + CurrentDateFolderPath
    runCommand(cmd)
    
    #Destination folder for converted bim's
    destFolderPath = os.path.join(LatestConverterTestsFolderPath , 'TestData' , 'ibimFiles')
    print 'Destination Folder Path : ' + destFolderPath

    #Deleting all the files, if present, from the 'ibim' folder
    print 'Deleting all the files, if present, from the ibim folder'
    for file in os.listdir(destFolderPath):
        print '\nFileName: ' + file
        BimFile= os.path.join(destFolderPath, file)
        os.remove(BimFile)
        print 'Deleted File: ' + file
    
    #Copying the passing bims from the Passing folder to the ibim folder in TestData
    PassingFilesFolder = os.path.join(CurrentDateFolderPath , 'PassingFiles')
    for file in os.listdir(PassingFilesFolder):
        filePath = os.path.join(PassingFilesFolder , file)
        shutil.copy(filePath , destFolderPath)

    #Run test
    cmd = ConverterTestsExePath + " " + "--gtest_filter=DataValidation_Tests.VerifyViewsForConvertediBimFile"
    runCommand(cmd)

    #Verifying if the ViewVerification csv is created or not
    ViewCsv = os.path.join(LatestConverterTestsFolderPath , 'TestData' , 'CsvFile' , 'ViewVerification.csv')
    if not os.path.exists(ViewCsv):
        print 'The csv after test run is not created. Exiting.'
        exit()

    #Inserting the data in sql db
    SqlScript = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'ViewVerificationScript' , 'WriteDataToSqlForViewVerification.py')
    cmd = SqlScript + " --streamName=\""+StreamName+"\" --reportPath=\""+OutputCsvPath+"\" --viewVerCsvPath=\""+ViewCsv+"\" --tableName=\""+TableName+"\""
    runCommand(cmd)

if __name__ == "__main__":
    main()

