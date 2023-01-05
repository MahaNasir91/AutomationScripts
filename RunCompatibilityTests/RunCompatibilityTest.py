import os, fnmatch, time, shutil, sys , csv
from datetime import datetime
import subprocess

#Global variables
scriptsRoot = 'E:\dgndbtestingscripts'
convertedFilesPath='E:\ConverterTesting\DgnV8'
JenkinsFolderPath = 'E:\dgndbtestingscripts\Jenkins'
RemoteJenkinsJob ='DgnDb61-16Q4_Winx64_Desktop_BuildDgnPlatform'
productName = 'DgnPlatform-Gtest'
currentDate = time.strftime("%Y-%m-%d")
Q2StableBuildPath = 'E:\CompatibilityTesting_Q2_Q3_StableBuilds\DgnDb61-16Q2_DgnPlatform-Gtest'
Q3StableBuildPath = 'E:\CompatibilityTesting_Q2_Q3_StableBuilds\DgnDb61-16Q3_DgnPlatform-Gtest'
uploadFileScript = os.path.join(scriptsRoot ,'CommonTasks')

def SearchList(list, val):
    try:
        index = list.index(val)
        return index
    except ValueError:
        return 'Not Found'

def ExecuteCompatibilityTest(workingStream, currentDate):
    activeStream = workingStream.split('\\')[-1]
    print 'Active Stream: ', activeStream
    streamCode = activeStream.split('DgnDb')[-1]
    streamsList=[]
    streamsPubList=[]
    global filePath

def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit(-1)
    else:
        print 'Ran task successfully.'
        
def GetLatestFolderInDirectory(Path):
    list = []
    if(os.path.exists(Path)):
        for root in os.listdir(Path):
            list.append(root)
    latestFolder = list[-1]
    print '\nLast Element of list:' + latestFolder
    return latestFolder

def RoboCopy(source , dest):
    cmd = 'Robocopy "'+source+'" "'+dest+'" /MIR'
    print 'Running command: ' + cmd
    status = subprocess.call(cmd,shell=True)
    if(status == 0 or status ==2):
        print("Robocopy did not copy")
        exit(1)
    if(status > 7):
        print("Error:Robocopy failed with status code " + str(status) +" .Exiting")
        exit(1)
    print("Robocopy successfull")
    
def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )
    
def ExecuteCompatibilityTest(workingStream, currentDate):
    
    activeStream = workingStream.split('\\')[-1]
    print 'Active Stream: ', activeStream
    streamCode = activeStream.split('DgnDb')[-1]
    print 'Active Stream Code: ', streamCode
    streamsList=[]
    streamsPubList=[]
              
    #Get list of streams to test in current stream
    compatibilityRoot = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\Assets\Documents\DgnDb\CompatibilityRoot')
    streamsPath = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\Assets\Documents\DgnDb\CompatibilityRoot')
    streamName= workingStream.split('\\')[-1]
    
    print '*** Working stream Name is:' + streamName + ' ***'
    
    if streamName == 'DgnDb61-16Q4':
        if not os.path.exists(streamsPath):
            os.mkdir(streamsPath)

        #Deleting all the sub files and folders
        for root, dirs, files in os.walk(streamsPath):
            for folder in dirs:
                folderPath= os.path.join(streamsPath + '\\' + folder)
                shutil.rmtree(folderPath , onerror = remove_readOnly)
        streamQ2= os.path.join(streamsPath, 'DgnDb61-16Q2')
        os.mkdir(streamQ2)
                
    else:
        if streamName == 'DgnDb61-16Q2':
             for root, dirs, files in os.walk(streamsPath):
                 for folder in dirs:
                    folderPath= os.path.join(streamsPath + '\\' + folder)
                    shutil.rmtree(folderPath, onerror = remove_readOnly)
                    print 'Deleted Folder:' + folderPath + '\n'
             streamQ4= os.path.join(streamsPath , 'DgnDb61-16Q4')
             os.mkdir(streamQ4)
                        
             #Deleting the tiff files created in the Output folder as a result of the conversion of DgnDb61-16Q4 files
             Q4ConvertedFiles= os.path.join(convertedFilesPath, 'DgnDb61-16Q4')
             latestFolder = GetLatestFolderInDirectory(Q4ConvertedFiles)

             Q4Files= os.path.join(convertedFilesPath, 'DgnDb61-16Q4' , latestFolder , 'ConvertedFiles')
             for file in os.listdir(Q4Files):
                 if file.endswith('.itiff64'):
                     print 'Tiff FileName: ' + file
                     TiffFile= os.path.join(Q4Files, file)
                     os.remove(TiffFile)
                        
        elif streamName == 'DgnDb61-16Q3':
             for root, dirs, files in os.walk(streamsPath):
                 for folder in dirs:
                    folderPath= os.path.join(streamsPath + '\\' + folder)
                    shutil.rmtree(folderPath , onerror = remove_readOnly)
             streamQ2= os.path.join(streamsPath , 'DgnDb61-16Q2')
             os.mkdir(streamQ2)
	
    for subDirName in os.listdir(streamsPath):
        streamsList.append(subDirName)
    print 'List Of Streams To Be Tested: ', streamsList

    for i in range(len(streamsList)):
        exeFoldersPath = os.path.join(convertedFilesPath, streamsList[i])
        list=[]
        for root in os.listdir(exeFoldersPath):
            if fnmatch.fnmatch(root, '[0-9]*-[0-9]*-[0-9]*'):
                list.append(root)
        streamsPubList.append(os.path.join(exeFoldersPath, list[-1]))
    print streamsPubList
    
    for i in range(len(streamsList)):
        destFolderPath = os.path.join(compatibilityRoot, streamsList[i])
        srcDir = os.path.join(streamsPubList[i], 'PassingFiles')

        print 'SrcDir: ', srcDir
        print 'DestPath: ', destFolderPath

        for file in os.listdir(srcDir):
            filePath=os.path.join(srcDir, file)
            
            if file.endswith('.idgndb') or file.endswith('ibim'):
                if os.path.isfile(filePath):
                    shutil.copy2(filePath, destFolderPath)
                 
    #Run Tests
    cmd = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\DgnPlatformTest.exe --gtest_filter=BackwardsCompatibilityTests.OpenDgndbInCurrent')
    runCommand(cmd)
    
    #Preserve results
    if activeStream == 'DgnDb61-16Q4':
        rawCSVFilePath = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\\run\\Output\\BackwardsCompatibilityTests\\CompatibilityResults_'+activeStream+'.csv')
    else:
        rawCSVFilePath = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\\run\\Output\\CompatibilityResults_'+activeStream+'.csv')

    shutil.copy(rawCSVFilePath, os.path.join(workingStream, currentDate, 'CompatibilityResults_'+activeStream+'.csv'))

    #also move to temp folder for summary generation
    shutil.copy(rawCSVFilePath, os.path.join(tmpFolderPath, 'CompatibilityResults_'+activeStream+'.csv'))
    
    #Delete DgnDb's copied to Compatibility Root and to the output folder to save space.
    for i in range(len(streamsList)):
        destFolderPath = os.path.join(compatibilityRoot, streamsList[i])
        if os.path.exists(destFolderPath):
            shutil.rmtree(destFolderPath)
            time.sleep(60)
        print 'creating folder again: ', destFolderPath
        os.system('mkdir ' + destFolderPath)
    
    outputRoot = os.path.join(workingStream, currentDate, 'DgnPlatform-Gtest\\run\\Output')
    if os.path.exists(outputRoot):
        shutil.rmtree(outputRoot)
   
#Entry Point of script
if (len(sys.argv)!=2):
    print 'Wrong number of arguments'
    print 'Usage: RunCompatibilityTest.py E:\CompatibilityTesting'
    print 'Existing with status 1'
    sys.exit(1)

workingRoot = sys.argv[1]
currentDate = time.strftime('%Y-%m-%d')
dirName = workingRoot.split('CompatibilityTesting')[0]
tmpFolderPath = os.path.join(workingRoot, 'tmp')

#Creating the current date folders in the given working streams
Q2Dir = os.path.join(workingRoot, 'DgnDb61-16Q2' , currentDate)
Q3Dir = os.path.join(workingRoot, 'DgnDb61-16Q3' , currentDate)
Q4Dir = os.path.join(workingRoot, 'DgnDb61-16Q4' , currentDate)

#Q2 directory
if(os.path.exists(Q2Dir)):
    shutil.rmtree(Q2Dir , onerror = remove_readOnly)    
os.mkdir(Q2Dir)

#Q3 directory
if(os.path.exists(Q3Dir)):
    shutil.rmtree(Q3Dir , onerror = remove_readOnly)
os.mkdir(Q3Dir)

#Q4 directory
if(os.path.exists(Q4Dir)):
    shutil.rmtree(Q4Dir , onerror = remove_readOnly)
os.mkdir(Q4Dir)

#Robocopy the stable build of DgnDb61-16Q2 and DgnDb61-16Q3
if os.path.exists(Q2Dir):
    destPathQ2 = os.path.join(Q2Dir, 'DgnPlatform-Gtest')
    os.mkdir(destPathQ2)
    RoboCopy(Q2StableBuildPath , destPathQ2)

if os.path.exists(Q3Dir):
    destPathQ3 = os.path.join(Q3Dir, 'DgnPlatform-Gtest')
    os.mkdir(destPathQ3)
    RoboCopy(Q3StableBuildPath , destPathQ3)

#Creating a folder to temporarily hold the files for manipulation using easy paths.
if os.path.exists(tmpFolderPath):
    shutil.rmtree(tmpFolderPath)
    os.system('mkdir ' + tmpFolderPath)
    
#Trigger GetnBuild job on jenkisn for DgnDb61-16Q4. Since Q2 & Q3 are stable now, we are using the previous stable run instead of building them for every run.
Q4DirPath = os.path.join(workingRoot, 'DgnDb61-16Q4')
cmd = JenkinsFolderPath + '\GenericGetnBuild.py --root ' + Q4DirPath + ' --productName ' + productName + ' --remoteJenkinsJob ' + RemoteJenkinsJob
runCommand(cmd)

#Executes compatibility test
ExecuteCompatibilityTest(os.path.join(workingRoot, 'DgnDb61-16Q2'), currentDate)
ExecuteCompatibilityTest(os.path.join(workingRoot, 'DgnDb61-16Q3'), currentDate)
ExecuteCompatibilityTest(os.path.join(workingRoot, 'DgnDb61-16Q4'), currentDate)

#Creating Archive folder to hold the Summary reports of the runs
archiveFolder = os.path.join(workingRoot, 'Archive')
if not os.path.exists(archiveFolder):
    os.system('mkdir ' + archiveFolder)
   
#Genereating summary for the Compatibility run
CompatibilityReportScript = 'E:\dgndbtestingscripts\Compatibility\CompatibilityReport.py'
SummaryReportPath = os.path.join (archiveFolder , 'CompatibilitySummary_'+currentDate+'.xlsx')

cmd = CompatibilityReportScript + ' ' + tmpFolderPath + ' ' + currentDate + ' ' + SummaryReportPath
runCommand(cmd)

#Copying Compatiblity summary report from archive to the Compatibility Testing folder and renaming it so as to upload it on sharepoint.
newReportName = os.path.join (workingRoot , 'CompatibilitySummary.xlsx')
if(os.path.exists(newReportName)):
    os.remove(newReportName)
shutil.copyfile(SummaryReportPath , newReportName)

#Upload the results on sharePoint
cmd = uploadFileScript + '\UploadFile.py E:\CompatibilityTesting\CompatibilitySummary.xlsx Summary E:\dgndbtestingscripts\CommonTasks'
runCommand(cmd)