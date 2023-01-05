import sys
import datetime
import os
import fnmatch
import re
import argparse
import subprocess

#-------------------------------------------------------------------------------------------
#                           Maha.Nasir                 2017
#-------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--path", help = "DgnDbTestingScript path (exp:D:\test\DgnDbTestingScripts)", required=True)

if (len(sys.argv)==2):
    args = parser.parse_args() 
    path=args.path
    path=path.replace('\\','\\\\')
    os.chdir(path)

    print "\n*** Directory %s" %os.getcwd()
    if (os.path.exists(path)):

        print "\n *** List of Modified\Untracked files *** \n"
        cmd="hg status"
        os.system(cmd)

        print "\n *** Checking and deleting untracked files *** \n"
        cmd="hg purge --all"
        os.system(cmd)

        print "\n *** Checking local changes *** \n"
        output = subprocess.check_output(["hg", "status", "-m"])
        #Getting file names that have local changes
        files = [line.split(' ', 1)[1] for line in output.split('\n') if line != '']
        if not files:
            print " *** No local changes found *** \n"
            print "\n *** Pull and Update DgnDbTestingScripts Repository *** \n"
            os.system("hg pull")#Pull DgnDbTestingScripts Repository
            print "\n *** Pull Completed *** \n"         
            status=os.system("hg update")#Update DgnDbTestingScripts Repository
            if status!= 0:
                print " *** Abort update: Local changes present *** "
                print " *** Please resolve the conflicts first *** "
                sys.exit(1)#replace 0 to 1 to make the build fail
            print " status is %s" %status
            print "\n *** Update Completed *** \n"
        else:
            print "\n *** Local changes found *** \n"
            #for filename in files:
                #print "Changed File = %s"%filename
            print "\n *** Reverting local changes *** \n" 
            cmd="hg revert --all --no-backup"
            os.system(cmd)
                        
else:
    print "Error: Arguments are not entered or not correct."

