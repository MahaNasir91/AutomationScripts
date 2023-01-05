import os
import sys

# Run any console command   
def runCommand( cmd ):
	print "Running commad : ", cmd
	result = os.system(cmd)
	print "Commad execution status : ", result
	return result
	

print " "
print " *** SharePoint Reporting ***" 
print 'inside ExecuteUnitTestsUWP.py'
srcPath=str(sys.argv[1])
print 'source path '+srcPath
streamName=str(sys.argv[2])
print 'stream '+streamName
reportScriptPath=str(sys.argv[3])
print 'report script path '+reportScriptPath
print " "


print "ChangeSet: python bentleybuild\BentleyBuild.py in -g v"
cmd = srcPath + r"src\BentleyBuild\bentleybuild.py in -g v"
result = runCommand(cmd)


print "Get: "+"python BentleyBuild\\bentleybuild.py -v6 -s 'DgnClientSdk;firebug' -a winrtx64 -t " + streamName + " get"
cmd = srcPath + r"\src\BentleyBuild\bentleybuild.py -v6 -s DgnClientSdk;firebug -a winrtx64 -t " + streamName + " get"
result = runCommand(cmd)


print "Build: "+"python BentleyBuild\\bentleybuild.py -v6 -s 'DgnClientSdk;firebug' -a winrtx64 -t " + streamName + " b --tmrb"
cmd = "echo y | call " + srcPath + r"\src\BentleyBuild\bentleybuild.py -v6 -s DgnClientSdk;firebug -a winrtx64 -t " + streamName + " b --tmrb"
result = runCommand(cmd)

os.system(reportScriptPath+"\WinRTx64UnitTestsReport.py "+streamName+" "+srcPath)


