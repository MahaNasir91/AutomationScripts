import argparse
import os
import sys
import time
import shutil
import subprocess
import csv

def GetLatestFolderInDirectory(Path):
    list = []
    if(os.path.exists(Path)):
        for root in os.listdir(Path):
            list.append(root)
    latestFolder = list[-1]
    print '\nLast Element of list:' + latestFolder
    return latestFolder

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

def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit(-1)
    else:
        print 'Ran task successfully.'

def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

def rundateFromCSV(csv_path):
    csvfile = open(csv_path, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    reader.next()
    for row in reader:
        return row[0].split(' ')[0]
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--workspaceRoot", help="Path of the Stream", required=True)
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
    JenkinsFolderPath = os.path.join(ScriptsRoot , 'Jenkins')
    JenkinsAuthenticationFilePath = 'C:\Users\Maha.Nasir\Desktop\Jenkins.auth'
    productName = 'RealDwgImporter'
    RemoteJenkinsJob ='Bim0200_Winx64_Desktop_BuildDwgConverter'
    StreamPath = os.path.join(WorkspaceRoot, 'Dwg', StreamName)
    CurrentDateFolderPath = os.path.join(StreamPath, time.strftime("%Y-%m-%d"))
    buildFolderPath = os.path.join(WorkspaceRoot , 'Workspace' , 'Build')
    datasetFolderPath = os.path.join(WorkspaceRoot , 'Dwg' , 'DataSet' ,'DWG_Dataset')
    outputDir = os.path.join(CurrentDateFolderPath, 'ConvertedFiles')
    customizedXml = os.path.join(ScriptsRoot , 'DwgConversion' ,'Customize.xml')
    datasetCsvPath = os.path.join(ScriptsRoot, 'DwgConversion' , 'DataSetForDwgConversion.csv')
    OutputCsvPath = os.path.join(outputDir, "Output_report.csv")
    TableName = 'csdk_dwgconversion_archive'
    
    #Trigger job on jenkins to get & build DwgConverter for Bim0200.
    cmd = JenkinsFolderPath + '\GenericGetnBuild.py --root ' + StreamPath + ' --productName ' + productName + ' --remoteJenkinsJob ' + RemoteJenkinsJob
    print '\nRunning command: ' + cmd + '\n'
    runCommand(cmd)
    
    #Verifying if the required exe is present or not
    DwgConverterFolderPath = os.path.join(CurrentDateFolderPath , 'RealDwgImporter')
    print DwgConverterFolderPath
    if(not os.path.exists(DwgConverterFolderPath)):
        print 'DwgConverter folder is not created. Exiting.'
        sys.exit(1)
        
    DwgExePath = os.path.join(DwgConverterFolderPath, 'DwgImporter.exe')
    print '\n\n' + DwgExePath
    if(not os.path.exists(DwgExePath)):
        print("Error:DwgImporter.exe missing. Stopping execution")
        exit(-1)

    #Making folder for the converted files
    if(os.path.exists(outputDir)):
        print 'Output folder already exists. Recreating it.'
        shutil.rmtree(outputDir, onerror = remove_readOnly)

    os.mkdir(outputDir)
    if(not os.path.exists(outputDir)):
        print 'Output folder not created. Exiting.'
        sys.exit()
        
    #DwgConversion
    print "\n\n\n\n ********** Converting Files *********\n\n\n"

    #Changing the current directory to cater proper Dwg conversion.
    modifiedDir = os.path.join(CurrentDateFolderPath , productName)
    currentWorkingDir = os.getcwd()
    print '\nCurrent working directory:' + currentWorkingDir
    os.chdir(modifiedDir)
    modDir = os.getcwd()
    print '\nModified directory path:' + modDir
       
    cmd = "E:\dgndbtestingscripts\DgnV8Conversion\BulkDgnV8Conversion.py --input=\""+datasetFolderPath+"\" --output=\""+outputDir+"\" --converter=\""+DwgExePath+"\" --custom=\""+customizedXml+"\""
    if customizedXml is not None:
        cmd = cmd + " --custom="+customizedXml
    runCommand(cmd)

    print "\n\n\n\n ********** Creating Report File *********\n\n\n"
    
    if (not os.path.exists(datasetCsvPath)):
        print 'Please provide a valid dataset csv path. Exiting.'
        sys.exit(1)
    
    #Verifying if the Output_report.csv is already present. Deleting it if it does.
    if not os.path.exists(OutputCsvPath):
        print 'Output_report.csv not found. Exiting.'
        exit()
    
    #Generating report
    SqlScript = os.path.join(ScriptsRoot, 'DgnV8Conversion' , 'WriteDataToSqlForPerfMachine.py')
    cmd = SqlScript + " --streamName=\""+StreamName+"\" --reportPath=\""+OutputCsvPath+"\" --datasetCsvPath=\""+datasetCsvPath+"\" --tableName=\""+TableName+"\""
    runCommand(cmd)