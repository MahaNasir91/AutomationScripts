#--------------------------------------------------------------------------------------
#
#     $Source: Performance/ElementCRUD/ModifiedPerformanceScripts/RunCrudPerformanceTask.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
import sys, sqlite3, xlsxwriter, datetime, os, argparse, subprocess, time, shutil , csv, fnmatch
from os.path import normpath, basename

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    05/2018
#-------------------------------------------------------------------------------------------
def GetBenchmarkFolder(folder):
    list=[]
    for root in os.listdir(folder):
        if fnmatch.fnmatch(root, '[0-9]*-[0-9]*-[0-9]*'):
            list.append(root)

    if len(list) > 1:
        benchmarkDate = list[-2]
    else:
        benchmarkDate = None
    return benchmarkDate

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    05/2018
#-------------------------------------------------------------------------------------------
def RenameReport(oldReportPath, newReportPath):
    os.rename(oldReportPath , newReportPath)
    return newReportPath


#-------------------------------------------------------------------------------------------
#                                    Maha Nasir    05/2018
#                                   Entry point of script
#-------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument("--scriptsRoot", help="Path to the dgndbtesting repo", required=True)
parser.add_argument("--workspaceRoot", help="Workspace/Output root", required=True)

args = parser.parse_args()

ScriptsRoot = args.scriptsRoot    
WorkspaceRoot = args.workspaceRoot

if (not os.path.exists(WorkspaceRoot)):
    print 'Worksapce/output root path is not valid. Please provide a valid path. Exiting'
    exit()
      
#Global variables
conversionDir = os.path.join(ScriptsRoot, 'DgnV8Conversion')
sys.path.append(conversionDir)
print conversionDir
from Run import createDirectory, rundateFromCSV, runCommand

RemoteJenkinsJob = 'Bim0200_Winx64_Desktop_BuildTestCollectionPerformance'
JenkinsAuthenticationFilePath = 'C:\Users\Maha.Nasir\Desktop\Jenkins.auth'
CurrentDateFolderPath = os.path.join(WorkspaceRoot, time.strftime("%Y-%m-%d"))
DirectoryCleanupScript = os.path.join(ScriptsRoot ,'CommonTasks' , 'DirectoryCleanup.py')
productName = 'GTest-DgnClientFx-TestCollection-Performance'
StreamName = 'Bim0200'

#Deleting folders in the directory to free disk space.
cmd = DirectoryCleanupScript + ' --dirPath ' + WorkspaceRoot + ' --folderCount 2'
runCommand(cmd)

#Making a folder by the current date
if os.path.exists(CurrentDateFolderPath):
    shutil.rmtree(CurrentDateFolderPath)
createDirectory(CurrentDateFolderPath)

#Creating a folder in the current date folder to place the Gtest-ClientFx-Performance
GtestFolder = os.path.join(CurrentDateFolderPath, productName)
createDirectory(GtestFolder)

#Trigger job on jenkins to get & build Converter for Bim0200.
cmd = ScriptsRoot + '\Jenkins\GenericGetnBuild.py --root ' + WorkspaceRoot + ' --productName ' + productName + ' --remoteJenkinsJob ' + RemoteJenkinsJob
print '\nRunning command: ' + cmd + '\n'
runCommand(cmd)
    
#Verifying performance exe
if(os.path.exists(GtestFolder)):
    for file in os.listdir(GtestFolder):
        if (file == 'DgnPerformance.exe'):
            PerformanceExePath = os.path.join(GtestFolder , file)
            print 'PerformanceExe Path is:' + PerformanceExePath
else:  
    print 'PerformanceExe not found. Build not successfull. Exiting.'
    sys.exit(1)

#Checking if a benchmark csv is present
benchMarkFolder = GetBenchmarkFolder(WorkspaceRoot)
print 'Taking ' + benchMarkFolder + ' folder as a benchmark folder for performance.'
if(benchMarkFolder == None):
    print 'Folder count less than 1. Exiting, because performance needs a benchmark csv to continue'
    exit()

PerformanceCsv_Benchmark = os.path.join(WorkspaceRoot, benchMarkFolder, 'PerformanceResults_Current.csv')
print PerformanceCsv_Benchmark
if (not os.path.exists(PerformanceCsv_Benchmark)):
    print 'Benchmark csv not found. Exiting'
    exit()

#Copying the csv in the current date folder and renaming it to Benchmark csv
shutil.copy(PerformanceCsv_Benchmark , CurrentDateFolderPath)
oldReportName = os.path.join(CurrentDateFolderPath, 'PerformanceResults_Current.csv')
newBenchmarkReport = os.path.join(CurrentDateFolderPath, 'PerformanceResults_Benchmark.csv')
RenameReport(oldReportName, newBenchmarkReport)

#Running performance tests
PerfExe = os.path.join(GtestFolder , 'DgnPerformance.exe')
cmd = PerfExe + ' --gtest_filter=PerformanceFixtureCRUD.Elements* --gtest_repeat=10 --timeout=-1'
runCommand(cmd)

#Verifying Performance Current csv
GtestPerformanceFolder = os.path.split(PerfExe)[0]
PerformanceCsv_Current = os.path.join(GtestPerformanceFolder , 'run' , 'Output' , 'PerformanceTestResults' , 'PerformanceResults.csv')
if(not os.path.exists(PerformanceCsv_Current)):
    print 'Performance current csv not found. Performance run didnt complete successfully'
    exit()

#Copying Current Performance csv in the workspace
shutil.copy(PerformanceCsv_Current , CurrentDateFolderPath)
oldName = os.path.join(CurrentDateFolderPath, 'PerformanceResults.csv')
newCurrentReport = os.path.join(CurrentDateFolderPath, 'PerformanceResults_Current.csv')
RenameReport(oldName, newCurrentReport)

#Reading the run dates from the current and benchmark CSV's
CurrentDate = rundateFromCSV(newCurrentReport)
BenchmarkDate = rundateFromCSV(newBenchmarkReport)

CurrentDate = CurrentDate.split("T")[0]
BenchmarkDate = BenchmarkDate.split("T")[0]

#Creating Performance Analysis report from the given csv's
PerfAnalysisReportName = 'Analysis_' + CurrentDate + '_' + BenchmarkDate + '.xlsx'
print PerfAnalysisReportName

CurrentDetails = StreamName + '_Winx64_Desktop_' + CurrentDate
BenchmarkDetails = StreamName + '_Winx64_Desktop_' + BenchmarkDate

#Running python script to create a combined analysis report the current and benchmark run
PerfAnalysisReportPath = os.path.join(CurrentDateFolderPath, PerfAnalysisReportName)
PerformanceSummaryScript = os.path.join(ScriptsRoot,'Performance', 'ElementCRUD' , 'PerformanceTestSummary.py')
cmd = PerformanceSummaryScript + ' --current=' + newCurrentReport + ' --benchmark=' + newBenchmarkReport + ' --output=' + PerfAnalysisReportPath + ' --currDetail=' + CurrentDetails + ' --benDetail=' + BenchmarkDetails
runCommand(cmd)

print 'Performance Analysis Report path: ' + PerfAnalysisReportPath

#Copying Json file to the current date folder
JsonFile = os.path.join(CurrentDateFolderPath, 'GTest-DgnClientFx-TestCollection-Performance' , 'Assets', 'PerformanceTestData' , 'ElementCrud.json')
if (not os.path.exists(JsonFile)):
    print 'Unable to find json file on the given path. Exiting'
    exit(1)
    
shutil.copy(JsonFile , CurrentDateFolderPath)