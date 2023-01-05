import os
import sys

# Run any console command   
def runCommand( cmd ):
	print "Running commad : ", cmd
	result = os.system(cmd)
	print "Commad execution status : ", result
	return result
	

srcPath=str(sys.argv[1])
streamName=str(sys.argv[2])
reportScriptPath=str(sys.argv[3])
outPath=str(sys.argv[4])


cmd = srcPath + r"src\BentleyBuild\bentleybuild.py -a x64 -s DgnClientSdkAndGist -p RunGistWinScriptTests -f Gist -r Gist p"
result = runCommand(cmd)



cmd = "echo y | call " + srcPath + r"src\BentleyBuild\bentleybuild.py b --tmr"
result = runCommand(cmd)


cmd = srcPath + r"src\BentleyBuild\bentleybuild.py -a x64 -s DgnClientSdkAndGist -p RunGistWinScriptTests -f Gist -r Gist b"
result = runCommand(cmd)

print 'report generating'
os.system(reportScriptPath+"\Win64TypeScriptTestsReport.py "+streamName+" "+outPath)
