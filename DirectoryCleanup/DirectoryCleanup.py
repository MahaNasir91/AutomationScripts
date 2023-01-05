import os
import sys
import argparse
import fnmatch
import shutil
import stat

def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )
    
parser = argparse.ArgumentParser()

parser.add_argument("--dirPath",help = "Path of the directory from where you want to delete the folders.", required=True)
parser.add_argument("--folderCount",help = "The number of folder/enteries you want to keep in the directory.", required=True) #The rest of them will be deleted (Based on the creation date).

args = parser.parse_args()
    
DirPath = args.dirPath
FolderCount = args.folderCount

#Checks if the given folder path is a valid path
if(not os.path.exists(DirPath)):
    print 'Please provide a valid path. Exiting.'
    sys.exit(1)

#Storing the folder names in a list
list = []
for folder in os.listdir(DirPath):
    if fnmatch.fnmatch(folder, '[0-9]*-[0-9]*-[0-9]*'):
        list.append(folder)

#Checks if the folder count is greater than length of the list
if(len(list) <= int(FolderCount)):
    print '\n ***The folder count in the provided directory is not adequate to delete any folder*** \n'
    sys.exit()
    
#Storing the names of the folders to delete, in a new list
folderCountToDelete = len(list) - int(FolderCount)
    
folderListToDelete = []
folderListToDelete = list[:folderCountToDelete]

#Deleting the extra folders
for folder in folderListToDelete:
    folderPath = os.path.join(DirPath , folder)
    if(os.path.exists(folderPath)):
       shutil.rmtree(folderPath, onerror = remove_readOnly)
       print 'Deleted folder: ' + folder