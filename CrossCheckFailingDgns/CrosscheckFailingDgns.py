#--------------------------------------------------------------------------------------
#
#     $Source: DgnV8Conversion/CrosscheckFailingDgns.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------

import os, time, shutil, sys , csv, subprocess, argparse
import xml.etree.ElementTree as ET

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    03/2018
#-------------------------------------------------------------------------------------------
#Walks through the dataset directory and copies the file from the directory to the given output location 
def locate_and_copy(DatasetDir, DgnName , OutputDir):
    for (dirpath, dirnames, filenames) in os.walk(DatasetDir):
        for filename in filenames:
            if filename == DgnName:
                file_path = os.path.join(dirpath , filename)
                if os.path.isfile(file_path):
                    shutil.copy(file_path , OutputDir)
                    print 'Copied Dgn: ' +  filename

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    03/2018
#-------------------------------------------------------------------------------------------    
def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit()
    else:
        print 'Ran task successfully.'
        
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--csvPath", help="Path of the Conversion Csv created after conversion", required=True)
parser.add_argument("--datasetDir", help="Path of the folder containing the dgns", required=True)
parser.add_argument("--workspaceRoot", help="Workspace/Output root", required=True)
parser.add_argument("--scriptsRoot", help="Dgndbtesting repository path", required=True)
parser.add_argument("--converterExe", help="Path of the DgnV8 converter exe", required=True)
parser.add_argument("--failureTypeFilter", help="To specifically convert only the dgns with the provided failure type. If no filter is provided, all the failing dgns in the provided conversion report will be converted.")

args = parser.parse_args()
    
CsvPath = args.csvPath
DatasetDir = args.datasetDir
WorkspaceRoot = args.workspaceRoot
ScriptsRoot = args.scriptsRoot
ConverterExe = args.converterExe
FailureTypeFilter = args.failureTypeFilter

#Verifying the CSV path
if(not os.path.exists(CsvPath)):
    print 'CSV not found. Exiting.'
    sys.exit(1)

#Verifying the dataset path
if(not os.path.exists(DatasetDir)):
    print 'The provided dataset path is not correct. Exiting.'
    sys.exit(1)

#Verifying the Converter Exe
if(not os.path.exists(DatasetDir)):
    print 'Provide a valid Converter Exe path.'
    sys.exit(1)

#Creating a folder to place the required dgns
OutputDir = os.path.join(WorkspaceRoot , time.strftime("%Y-%m-%d"))
if (os.path.exists(OutputDir)):
    shutil.rmtree(OutputDir)
os.mkdir(OutputDir)

#Making folders for failing dgns and a folder to hold the converted failing files after the cross check 
os.mkdir(os.path.join(OutputDir, 'ConvertedFiles'))
FailingDgnsFolder = os.path.join(OutputDir, 'FailingDgns')
os.mkdir(FailingDgnsFolder)

ConvertedFiles = os.path.join(OutputDir , 'ConvertedFiles')
if (not os.path.exists(ConvertedFiles)):
    print 'Folder not created. Exiting.'
    exit(1)
    
#Creating a csv for all the failing dgns
f = open(OutputDir+'/FailingFiles.csv','wb')
fw = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)

fw.writerow(["File Name" , "Status" , "Notes"])

#Reading the conversion csv given by the user, locating the failing dgns and copying them to a seperate folder. 
with open(CsvPath , 'rb') as ConversionCsv:
    counter = 0
    Reader = csv.DictReader(ConversionCsv , delimiter=',')
    for row in Reader:
        DgnName = row['Name']
        FailureType =  row['Notes']
        ConversionStatus = row['Result']

        if ConversionStatus == 'FAIL':
           
            #If the filter is provided
            if FailureTypeFilter:     
                if FailureType == '':
                    continue
            
                if FailureTypeFilter == FailureType:
                    locate_and_copy(DatasetDir, DgnName , FailingDgnsFolder)
                    #Writing the name and conversion status of the failing dgns in the FailingFiles csv
                    fw.writerow([DgnName , ConversionStatus , FailureType])
                    counter += 1

            #If no filter is provided, copies all of the failing dgns to the output folder        
            else:
                locate_and_copy(DatasetDir, DgnName , FailingDgnsFolder)
                #Writing the name and conversion status of the failing dgns in the FailingFiles csv
                fw.writerow([DgnName , ConversionStatus , FailureType])
                counter += 1

    #Exits if the filter provided by the user doesn't match with any of the failure type value in the csv
    if counter == 0:
        print '\nThe given filter doesnt match with any of the failure type filters. Please provide a valid value.'
        exit(1)

f.close()

#Making a copy of the CustomXml file in the output directory
CustomXmlFile = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'Customize.xml')
newXmlPath = os.path.join(OutputDir, 'Customize.xml')
if(os.path.exists(newXmlPath)):
    os.remove(newXmlPath)

shutil.copy(CustomXmlFile,OutputDir)

#Custom xml
FailingFilesCsvPath = os.path.join(OutputDir , 'FailingFiles.csv')
if(not os.path.exists(FailingFilesCsvPath)):
    print 'The custom xml doesnt exists on the given path. Provide a valid path.'
    exit(1)

#Reading the Custom xml file
CopiedXmlPath = os.path.join(OutputDir,'Customize.xml')
print 'Copied path:' + CopiedXmlPath
tree = ET.parse(CopiedXmlPath)                              
root = tree.getroot()

#Replacing the path of the Csv with the path provided by the user
customize = root.find('Customize')
data_set = customize.find('DataSetFilters')
data_set.find('path').text = FailingFilesCsvPath
tree.write(CopiedXmlPath)

print '\nDataset Csv path is set to:' + FailingFilesCsvPath

#Running the bulk conversion script to convert the failing dgns
cmd = os.path.join(ScriptsRoot, 'DgnV8Conversion', 'BulkDgnV8Conversion.py --input=') +  FailingDgnsFolder + ' --output=' + ConvertedFiles + ' --converter=' + ConverterExe + ' --custom=' + CopiedXmlPath
runCommand(cmd)

#Copying the conversion report.
ConversionReport = os.path.join(ConvertedFiles , 'Output_report.csv')
NewConversionReport = os.path.join(OutputDir , 'ConversionReport.csv')
if(os.path.exists(NewConversionReport)):
    os.remove(NewConversionReport)
shutil.copyfile(ConversionReport , NewConversionReport)

print '\nConversion report is created at: ' +  NewConversionReport

os.remove(CopiedXmlPath)