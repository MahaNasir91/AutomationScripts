#--------------------------------------------------------------------------------------
#
#     $Source: CommonTasks/GetnBuild.py $
#
#  $Copyright: (c) 2017 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
from datetime import datetime
import os ,sys ,time
from subprocess import call

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha.Nasir    02/2018
#-------------------------------------------------------------------------------------------
# Run any console command   
def runCommand( cmd ):
	print "Running commad : ", cmd
	result = os.system(cmd)
	print "Commad execution status : ", result
	return result
	
cmd = "ipconfig /flushdns"
runCommand(cmd)

if len(sys.argv) != 4 : 
    print "Too Few Arguments : Please Provide StreamPath, Build Command and whether to clean code or not"
    print 'GetnBuild.py C:\BSW\DgnDb06 "bb -p DgnPlatform:GTest-DgnPlatform-TestCollection-Performance -r DgnPlatform b --tmrb" cleanYes'
    print 'Exiting with status 1'
    sys.exit(1);

streamPath = sys.argv[1]
buildCommand = sys.argv[2]
clean = sys.argv[3]
print "Starting Get and Build for: [" , streamPath.split('\\')[-1], "]"

#Determine the pull Command from the build Command
pullCmd = buildCommand[(buildCommand.find('bb ') + 3):buildCommand.find(' b ')]

Counter = 0
while True:
	Counter += 1
	if len(pullCmd) > 0: # we need Custom pull
		cmd = "call bb.bat " + pullCmd + " pull"
	else:
		cmd = "call bb.bat pull"
	result = runCommand(cmd)
	if 'yes' in clean.lower():
		cmd = "call bb.bat hg revert -a"
		result = runCommand(cmd)
		cmd = "call bb.bat hg update -C"
		result = runCommand(cmd)
	#result = 0 
	#result = 1
	if result is 1:
		#Wait 
		if Counter == 3 :
			print 'Pull FAILED . ALREADY Tried 3 times . Will not try again Today'
			print 'Get.py Exiting with status' , 1
			sys.exit(1)
		print 'Pull Failed : Will re-try in 1 minute !!!'
		time.sleep(60)
	else:
		break

while True:
	cmd = "echo y | call " + buildCommand
	print cmd
	result = runCommand(cmd)
	#if the build failed
	if result is 1:
		print 'Build Failed'
		print 'Build.py Exiting with status' , 1
		sys.exit(1)
	else:
		break

print 'GetnBuild Completed'
print 'GetnBuild.py Exiting with status' , 0
sys.exit(0)
