import os
import subprocess
import sys
import shutil
import argparse
import time
import stat
from Trigger import JenkinsJob 

'''
    Input:  (required) --root : Path of the stream for which you are building the product,
            (required) --productName : Name of the product that you need to build eg DgnV8Converter,
            (required) --remoteJenkinsJobName    : Name of the job to build remotely via Jenkins  
'''

#Adding arguments
parser = argparse.ArgumentParser()
parser.add_argument("--root", help="Path of the stream for which you are building the product", required=True)
parser.add_argument("--productName", help="Name of the product that you need to build", required=True)
parser.add_argument("--remoteJenkinsJobName", help="Name of the job to build remotely via Jenkins", required=True)

args = parser.parse_args()

#Getting the values of arguements
Root = args.root
ProductName = args.productName
RemoteJenkinsJobName = args.remoteJenkinsJobName
    
#Global variables
scriptsRoot = 'E:\dgndbtestingscripts\Jenkins'
JenkinsAuthenticationFilePath = 'C:\Users\Maha.Nasir\Desktop\Jenkins.auth'
CurrentDateFolderPath = os.path.join(Root, time.strftime("%Y-%m-%d"))
BuildDirectoryPath = 'E:\ConverterTesting\Workspace\Build'

def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )
    
def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: Command failed with return status:" + str(result))
        exit(-1)
    else:
        print 'Ran task successfully.'

def RoboCopy(source , dest):
    cmd = 'Robocopy "'+source+'" "'+dest+'" /MIR'
    print 'Running command: ' + cmd
    status = subprocess.call(cmd,shell=True)
    if(status == 0 or status ==2):
        print("Robocopy did not copy")
        exit(1)
    if(status > 7):
        print("Error:Robocopy failed with status code." + str(status) +"Exiting")
        exit(1)
    print("Robocopy successfull")

#Deletes and recreates the Build directory
if(os.path.exists(BuildDirectoryPath)):
    shutil.rmtree(BuildDirectoryPath , onerror = remove_readOnly)
os.mkdir(BuildDirectoryPath)
  
#Making a folder by the current date in the given stream folder
if(os.path.exists(CurrentDateFolderPath)):
    shutil.rmtree(CurrentDateFolderPath , onerror = remove_readOnly)
print '\nCurrent date folder path: ' + CurrentDateFolderPath    
os.mkdir(CurrentDateFolderPath)

#Creating a folder by the name of the required product in the current date folder
os.mkdir(os.path.join(CurrentDateFolderPath, ProductName))
ProductDirectory = os.path.join(CurrentDateFolderPath, ProductName)
if(not os.path.exists(ProductDirectory)):
    print ProductName + ' folder not created. Exiting with status 1.'
    sys.exit(1)

#Triggers Jenkins remote job to GetnBuild the required product
Jenkins_Job = JenkinsJob(RemoteJenkinsJobName)
Jenkins_Job.set_authFile(JenkinsAuthenticationFilePath)
Jenkins_Job.set_waitForFinish(True)
status = Jenkins_Job.runJob()
    
#Robocopying the products to Performance machine
RoboCopy(BuildDirectoryPath , ProductDirectory)