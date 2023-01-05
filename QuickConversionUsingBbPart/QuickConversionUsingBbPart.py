#--------------------------------------------------------------------------------------
#
#     $Source: DgnV8Conversion/QuickConversionUsingBbPart.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------

import os, time, shutil, sys , csv, argparse
from Run import runCommand, createDirectory, remove_readOnly, rundateFromCSV

#Entry point of the script
parser = argparse.ArgumentParser()

parser.add_argument("--workspaceRoot", help="Path to the soutce folder of the tree for which you want to run the conversion", required=True)
parser.add_argument("--convertedDgnsFolder", help="Path to the folder containing the converted dgns", required=True)
parser.add_argument("--streamName", help="Name of the stream for which you want to run the conversion. If not given, it determines itself.")
parser.add_argument("--datasetCsvPath", help="Path to the dataest csv", required=True)
parser.add_argument("--operation", help="Specify the operation you have performed ie DwgConversion,DgnV8Conversion", required=True)
parser.add_argument("--datasetDir", help="Directory containing the dgns to be converted.", required=True)

args = parser.parse_args()

WorkspaceRoot = args.workspaceRoot
ConvertedDgnsFolder = args.convertedDgnsFolder
StreamName = args.streamName
DatasetCsvPath = args.datasetCsvPath
Operation = args.operation
DatasetDir = args.datasetDir
   
#Global variables
ScriptsRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
commonScriptsDir = os.path.join(ScriptsRoot, 'CommonTasks')
sys.path.append(commonScriptsDir)
import FindStream

commonScriptsDir = os.path.join(ScriptsRoot, 'CommonTasks')
DirectoryCleanupScript = os.path.join(commonScriptsDir , 'DirectoryCleanup.py')
CurrentDateFolderPath = os.path.join(WorkspaceRoot, time.strftime("%Y-%m-%d"))
OutputCsvPath = os.path.join(ConvertedDgnsFolder , 'Output_report.csv')
TableName = 'csdk_qc_archive' 

if StreamName == None:
    TeamConfigPath = os.path.join(os.getenv('SrcRoot'), 'teamConfig', 'treeConfiguration.xml')
    StreamName = FindStream.FindStreamDetails(TeamConfigPath)
        
#Checking if the QuickConversion was successful or not.
if not os.path.exists(ConvertedDgnsFolder):
    print 'The bb part didnt run successfully. Exiting.'
    exit()

#Checking if dataset directory is a valid path.
if not os.path.exists(DatasetDir):
    print 'The dataset directory path is not valid. Exiting.'
    exit()

SqlScript = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'WriteDataToSql')
cmd = SqlScript + " --streamName=\""+StreamName+"\" --reportPath=\""+OutputCsvPath+"\" --datasetCsvPath=\""+DatasetCsvPath+"\" --tableName=\""+TableName+"\""
runCommand(cmd)