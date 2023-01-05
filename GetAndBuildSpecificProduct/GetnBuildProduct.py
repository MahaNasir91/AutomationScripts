import os
import subprocess
import sys
import shutil
import argparse
import time
    
#Global variables
CurrentDate = time.strftime("%Y-%m-%d")
DestFolder = r"\\ASIA19789\ConverterTesting\Workspace\Build"

def runCommand(command):
    print 'Running command:' + command
    result = subprocess.call(command, shell=True)
    if(result != 0):
        print("Error: GetnBuild.py Failed with return status:" + str(result))
        exit(-1)

def RoboCopy(folderPath):
    cmd = 'Robocopy "'+folderPath+'" "'+DestFolder+'" /MIR'
    print 'Running command: ' + cmd
    status = subprocess.call(cmd,shell=True)
    if(status == 0 or status ==2):
        print("Robocopy did not copy")
        exit(-1)
    if(status > 7):
        print("Error:Robocopy failed with status code." + str(status) +"Exiting")
        exit(-1)
    print("Robocopy successfull")
    
#Entry Point of script

#Verifying the number of args
if (len(sys.argv) != 4):
    print 'Wrong number of arguments.'
    print '\n\n\n **********SYNTAX********** \n\n\n'
    print 'Syntax: GetnBuildProduct.py arg1 arg2 arg3'
    print 'arg1 = Root for which you want to build the product. \narg2 = Build command you want to run. \narg3 = Wether you want to clean the worspace or not.\n' 
    print 'Usage: GetnBuildProduct.py C:\BSW\Bim0200-Conversion "bb -p Ecdb-Gtest -r Ecdb -f Ecdb b --tmrb" yes'
    print 'Existing with status 1\n'
    sys.exit(1)

Root = sys.argv[1]
BuildCommand = sys.argv[2]
x = BuildCommand.split('-p')[-1]
PartName = x.split('-r')[0]
if (not PartName == ''):
    PartName = PartName.strip()
    print 'PartName' + PartName
else:
    'PartName cant be empty. Exiting'
    sys.exit(1)
CleanWorkspace = sys.argv[3]

#GetnBuild the required Product 
cmd = 'C:\dgndbtestingscripts\CommonTasks\GetnBuild.py '+ Root +' "' + BuildCommand + '" ' + CleanWorkspace 
runCommand(cmd)

#Required product folder path   
RequiredProductFolderPath = os.path.join(Root , "out\Winx64\Product" , PartName)
print 'Required Product name path is: ' + RequiredProductFolderPath
     
if(not os.path.exists(RequiredProductFolderPath)):
    print("Error:" + PartName + " not found. Stopping execution")
    exit(1)
else:
    print 'Continuing further execution.'

RoboCopy(RequiredProductFolderPath)