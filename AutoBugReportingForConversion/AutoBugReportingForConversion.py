#--------------------------------------------------------------------------------------
#
#     $Source: CommonTasks/AutoBugReportingForConversion.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------

import os, time, shutil, sys , csv, subprocess, argparse
import xml.etree.ElementTree as ET
from ReportWorkItemVsts import VSTS
vsts=VSTS()

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    06/2018
#-------------------------------------------------------------------------------------------
#Walks through the dataset directory and locates the given file
def locateFile(DatasetDir, FileName):
    for (dirpath, dirnames, filenames) in os.walk(DatasetDir):
        for filename in filenames:
            if filename == FileName:
                file_path = os.path.join(dirpath , filename)
                return file_path

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    06/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--csvPath", help="Path of the Conversion Csv(Output_report.csv) created after conversion", required=True)
parser.add_argument("--workspaceRoot", help="Workspace/Output root", required=True)
parser.add_argument("--datasetDir", help="Path to the dataset directory.", required=True)
parser.add_argument("--conversionFolderPath", help="Path of the folder where the issues file are being created", required=True)

args = parser.parse_args()
    
CsvPath = args.csvPath
WorkspaceRoot = args.workspaceRoot
DatasetDir = args.datasetDir
ConversionFolder = args.conversionFolderPath

#Verifying the CSV path
if(not os.path.exists(CsvPath)):
    print 'CSV not found. Exiting.'
    sys.exit(1)

#Verifying the dataset folder
if(not os.path.exists(DatasetDir)):
    print 'The given dataset directory doesnt exists. Exiting.'
    sys.exit(1)

#Verifying the conversion folder
if(not os.path.exists(ConversionFolder)):
    print 'Conversion folder doesnt exists. Exiting.'
    sys.exit(1)

#Getting the environment variable to report workitem on vsts
AccessToken = os.environ['Access_Token']

#Deleting csv if it already exists
CsvForBugReporting = os.path.join(WorkspaceRoot, 'FailingFilesForAutoBugReporting.csv')
if (os.path.exists(CsvForBugReporting)):
    os.remove(CsvForBugReporting)
    
#Creating a csv for all the failing dgns    
f = open(CsvForBugReporting,'wb')
fw = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
fw.writerow(['Date', 'FileName' , 'ConversionStatus' , 'FailureType'])

#Reading the conversion csv given by the user, locating the failing dgns and copying them to a seperate csv. 
with open(CsvPath , 'rb') as ConversionCsv:
    counter = 0
    Reader = csv.DictReader(ConversionCsv , delimiter=',')
    for row in Reader:
        DgnName = row['Name']
        FailureType =  row['Notes']
        ConversionStatus = row['Result']
        Date = row['Date'].split(' ')[0]

        if ConversionStatus == 'FAIL':
            counter += 1
            fw.writerow([Date, DgnName , ConversionStatus , FailureType])

    f.close()
        
    if (counter == 0):
        print 'No errors found in report.'
        os.remove(CsvForBugReporting)
        exit(0)
        

#If no csv present them exit script, as there are no defects to report
if (not os.path.exists(CsvForBugReporting)):
    print 'Csv report not created as there werent any failures in conversion. Therefore exiting.'
    exit(0)

#Reading the csv file for bug reporting
with open(CsvForBugReporting , 'rb') as BugReport:
    list = []
    Reader = csv.DictReader(BugReport , delimiter=',')
    for row in Reader:
        FileName = row['FileName']
        ConversionStatus =  row['ConversionStatus']
        FailureType = row['FailureType']
        RunDate = row['Date']

        #Setting fields for VSTS item
        IterationPath = 'iModelTechnologies\\DevTools'
        FoundIn = '02.00.00.01'
        RequestorName = 'ReportFailingConversionFiles'
        AssignedTo = 'Carole MacDonald'

        #Skips files having DiskIo or DigitalRights failures
        if(FailureType != None):
            failureReason = FailureType.split(',')[0]

            #If the failure type is already in te list then skip the rest of the loop
            if failureReason in list:
                continue

            #Adding failure reasons to a list
            list.append(failureReason)

            if (failureReason == 'DiskIO' or failureReason == 'DigitalRights'):
                continue
                           
        #Setting VSTS title and steps to reproduce
        if DgnName.lower().endswith('.dgn'):
            if(FailureType != None): 
                failureReason = FailureType.split(',')[0]
                VSTS_Title = 'DgnV8Converter: ' + FileName + ' failed to convert due to ' + failureReason
                print VSTS_Title
            else:
                VSTS_Title = 'DgnV8Converter: ' + FileName + ' failed to convert.'
                print VSTS_Title

            Steps = 'This dgn was converted using the source code of ' + RunDate + '. Please see the attached dgn and the issues file.'
            
        elif DgnName.lower().endswith('.dwg'):
            VSTS_Title = 'DwgConverter: ' + FileName + ' failed to convert.'
            Steps = 'This dwg was converted using the source code of ' + RunDate + '. Please see the attached dwg and the issues file.'

        #Set field values for VSTS item
        vsts.set_accesstoken(AccessToken)
        vsts.set_title(VSTS_Title)
        vsts.set_iterationpath(IterationPath)
        vsts.set_foundin(FoundIn)
        vsts.set_requestor(RequestorName)
        vsts.set_assignedto(AssignedTo)
        vsts.set_steps_to_reproduce(Steps)
        
        #This will report the defect
        vsts_number = vsts.report_workitem()
        
        #Locating dgnFile
        conversion_file = locateFile(DatasetDir, FileName)
        if (conversion_file == None):
            print 'The dgn/dwg file is not present in the provided dataset directory. Exiting'
            exit(1)

        #Uploading conversion file as attachment with the VSTS
        url=vsts.UploadAttachment(conversion_file,FileName)
        vsts.AddAttachmentToWorkItem(url, vsts_number)
            
        #Locating their respective issues file
        IssuesFileName = os.path.splitext(FileName)[0] + '.ibim-issues'
        Issue_file = locateFile(ConversionFolder, IssuesFileName)
        if (Issue_file == None):
            print 'The issues file is not present in the provided folder. Exiting'
            exit(1)

        #Uploading issues file as attachment with the VSTS
        url_Issues=vsts.UploadAttachment(Issue_file,IssuesFileName)
        vsts.AddAttachmentToWorkItem(url_Issues, vsts_number)
