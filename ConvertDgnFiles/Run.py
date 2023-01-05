#-------------------------------------------------------------------------------------------
#                                     Maha Nasir                               10/2017
#-------------------------------------------------------------------------------------------
import argparse
import os
import sys
import time
import shutil
import subprocess
import csv
import stat

#Common Scripts to be used by any task
scriptsDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
commonScriptsDir = os.path.join(scriptsDir, 'CommonTasks')
sys.path.append(commonScriptsDir)
import FindStream


def GetLatestFolderInDirectory(Path):
    list = []
    if(os.path.exists(Path)):
        for root in os.listdir(Path):
            list.append(root)
    latestFolder = list[-1]
    print '\nLast Element of list:' + latestFolder
    return latestFolder

def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit(-1)
    else:
        print 'Ran task successfully.'

def RoboCopy(SourcePath, DestinationPath):
    cmd = 'Robocopy "'+SourcePath+'" "'+DestinationPath+'" /MIR'
    print 'Running command: ' + cmd
    status = subprocess.call(cmd,shell=True)
    if(status == 0 or status ==2):
        print("Robocopy did not copy")
        exit(-1)
    if(status > 7):
        print("Error:Robocopy failed with status code." + str(status) +"Exiting")
        exit(-1)
    print("Robocopy successfull")

def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

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
        
def rundateFromCSV(csv_path):
    csvfile = open(csv_path, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    reader.next()
    for row in reader:
        return row[0].split(' ')[0]
    
if __name__ == "__main__":
    
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
    RemoteJenkinsJob ='Bim0200_Winx64_Desktop_BuildConverter'
    JenkinsAuthenticationFilePath = 'C:\Users\Maha.Nasir\Desktop\Jenkins.auth'
    productName = 'DgnV8Converter'
    currentDate = time.strftime("%Y-%m-%d")
    CurrentDateFolderPath = os.path.join(StreamPath, currentDate)
    outputDir = os.path.join(CurrentDateFolderPath, 'ConvertedFiles')
    customizedXml = os.path.join(ScriptsRoot, 'DgnV8Conversion', 'Customize.xml')
    datasetFolderPath = os.path.join(WorkspaceRoot, 'DgnV8' , 'DataSet')
    DatasetCsvPath = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'DatasetForConversion.csv')
    OutputCsvPath = os.path.join(outputDir, "Output_report.csv")
    TableName = 'csdk_dgnv8conversion_archive'
    uploadFileScript = os.path.join(ScriptsRoot ,'CommonTasks')
    
    if(not os.path.exists(StreamPath)):
        print 'StreamPath doesnt exists. Please provide a valid stream name.'
        sys.exit(1)
    
    #Deleting folders in the directory to free disk space.
    cmd = uploadFileScript + "\DirectoryCleanup.py --dirPath " + StreamPath + ' --folderCount 2'
    runCommand(cmd)
    
    #Making a folder by the current date in the Bim0200-Conversion folder
    createDirectory(CurrentDateFolderPath)

    #Creating DgnV8Converter folder in the current date folder
    createDirectory(os.path.join(CurrentDateFolderPath, 'DgnV8Converter'))

    #Creating a folder for the converted files in the current date folder
    createDirectory(outputDir)
        
    #Trigger job on jenkins to get & build Converter for Bim0200.
    cmd = ScriptsRoot + '\Jenkins\GenericGetnBuild.py --root ' + StreamPath + ' --productName ' + productName + ' --remoteJenkinsJob ' + RemoteJenkinsJob
    print '\nRunning command: ' + cmd + '\n'
    runCommand(cmd)
      
    #Verifying if Converter exe is present or not
    DgnV8ConverterFolder = os.path.join(CurrentDateFolderPath, 'DgnV8Converter')
    ConverterExePath = os.path.join(DgnV8ConverterFolder, 'DgnV8Converter.exe')
    if(not os.path.exists(ConverterExePath)):
        print("Error:DgnV8Converter.exe missing. Stopping execution")
        exit(-1)
    
    #Conversion
    print "\n\n\n\n ********** Converting Files *********\n\n\n"
    
    cmd = ScriptsRoot + "\DgnV8Conversion\BulkDgnV8Conversion.py --input=\""+datasetFolderPath+"\" --output=\""+outputDir+"\" --converter=\""+ConverterExePath+"\" --custom=\""+customizedXml+"\""
    if customizedXml is not None:
        cmd = cmd + " --custom="+customizedXml
    runCommand(cmd)

    #Sorts the Passing/Failing files in their respective folders after conversion
    OutputReportPath = os.path.join(outputDir , 'Output_report.csv')

    if (not os.path.exists(CurrentDateFolderPath)):
        print 'Directory path for creating Passing/Failing folder not found. Exiting.'
        sys.exit(1)
        
    PostConversionScript =  os.path.join(ScriptsRoot , 'Compatibility' , 'PostConversionSorting.py')
    cmd = PostConversionScript + ' ' + OutputReportPath + ' ' + outputDir + ' ' + CurrentDateFolderPath
    runCommand(cmd)

    #Creating folder to place the failing files after reconversion
    FolderForRecheckingFailingFiles = os.path.join(CurrentDateFolderPath, 'ReconfirmingFailingFiles')
    createDirectory(FolderForRecheckingFailingFiles)
    
    #Re-run conversion for confirming the crashes
    CrossCheckingScript = os.path.join(ScriptsRoot , 'DgnV8Conversion' , 'CrosscheckFailingDgns.py')

    #Generating report
    SqlScript = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'WriteDataToSqlForPerfMachine.py')
    cmd = SqlScript + " --streamName=\""+StreamName+"\" --reportPath=\""+OutputCsvPath+"\" --datasetCsvPath=\""+DatasetCsvPath+"\" --tableName=\""+TableName+"\""
    runCommand(cmd)