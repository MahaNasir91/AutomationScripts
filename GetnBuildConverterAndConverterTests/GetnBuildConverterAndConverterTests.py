#---------------------------------------------------------------------------------
#                                     Maha Nasir                               
#---------------------------------------------------------------------------------

import os
import subprocess
import sys
import shutil

if(len(sys.argv) < 2):
    print("Invalid arguments")
    exit()
root = sys.argv[1]
mode = sys.argv[2]

#Global variables
latestFolder = ''
ProductPath = os.path.join(root , 'out\Winx64\Product')
workspace = r"\\ASIA19789\ConverterTesting\Workspace\Build"
cleanWorkspace = 'yes'

print("Running on stream : " + root)

def runCommand(command):
    print 'Running command:' + command
    result = os.system(command)
    if(result != 0):
        print("Error: GetnBuild.py Failed with return status:" + str(result))
        exit(-1)

def RoboCopy(folderPath):
    cmd = 'Robocopy "'+folderPath+'" "'+workspace+'" /MIR'
    print 'Running command: ' + cmd
    status = subprocess.call(cmd,shell=True)
    if(status == 0 or status ==2):
        print("Robocopy did not copy")
        exit(-1)
    if(status > 7):
        print("Error:Robocopy failed with status code." + str(status) +"Exiting")
        exit(-1)
    print("Robocopy successfull")
           
#GetnBuild Converter 
cmd = 'C:\dgndbtestingscripts\CommonTasks\GetnBuild.py '+ root +' "' + 'bb -p DgnV8Converter -r DgnDbSync -f DgnDbSync b --tmrb' + '" ' + cleanWorkspace
runCommand(cmd)

#GetnBuild ConverterTests    
cmd = 'C:\dgndbtestingscripts\CommonTasks\GetnBuild.py '+ root + ' "'+ 'bb -p DgnV8ConverterTests -r DgnDbSync -f DgnDbSync b' + '" ' + cleanWorkspace
runCommand(cmd)

# Converter exe path   
if(mode.lower() == 'dgnv8'):
    ConverterExepath = root + "\out\Winx64\Product\DgnV8Converter"
     
if(not os.path.exists(ConverterExepath + "\DgnV8Converter.exe") ):
    print("Error:DgnV8Converter.exe missing. Stopping execution")
    exit(-1)
    
# ConverterTests exe path   
if(mode.lower() == 'dgnv8'):
    ConverterTestsExepath = root + "\out\Winx64\Product\DgnV8ConverterTests"
     
if(not os.path.exists(ConverterTestsExepath + "\DgnV8ConverterTests.exe") ):
    print("Error:DgnV8ConverterTests.exe missing. Stopping execution")
    exit(-1)

#Makes a robocopy of DgnV8Converter and DgnV8ConverterTests in the 'Build' folder on Test machine    
RoboCopy(ProductPath)