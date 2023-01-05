import os, time, shutil, sys , csv
import subprocess

def remove_readOnly( func, path, exc_info):
    # Remove readonly for a given path
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )
   
#Entry Point of script
if (len(sys.argv)!=4):
    print 'Wrong number of arguments.'
    print 'Existing with status 1'
    sys.exit(1)

CsvReportPath = sys.argv[1] #Path where the csv report is created after conversion
ConvertedFilesFolder = sys.argv[2] #Folder path of the converted dgn's
PassFailFolderPath = sys.argv[3] #Folder path where you want to create the passing and failing folders and their csv's

#Verifying the CSV path
if(not os.path.exists(CsvReportPath)):
    print 'CSV not found. Exiting.'
    sys.exit(1)

#Creating Passing and Failing csv's
f = open(PassFailFolderPath+'/FailingFiles.csv','wb')
p = open(PassFailFolderPath+'/PassingFiles.csv','wb')
fw = csv.writer(f,delimiter=',',quoting=csv.QUOTE_MINIMAL) 
pw = csv.writer(p,delimiter=',',quoting=csv.QUOTE_MINIMAL)

fw.writerow(["File Name"])
pw.writerow(["File Name"])
     
#Placing the Passing/Failing files in their respective CSV's 
with open(CsvReportPath , 'rb') as csvFile:
    fileReader = csv.DictReader(csvFile , delimiter=',')

    for row in fileReader:
        FileName = row['Name']
        FileStatus = row['Result']
        if (FileStatus == 'FAIL'):
            fw.writerow([FileName])
        else:
            pw.writerow([FileName])

#Closing workbooks
p.close()
f.close()

#Recreating PassingFiles & FailingFiles folder so as to delete any prev. files if present in it
PassingFilesFolder = os.path.join(PassFailFolderPath , 'PassingFiles')
FailingFilesFolder = os.path.join(PassFailFolderPath , 'FailingFiles')

if(os.path.exists(PassingFilesFolder)):
        shutil.rmtree(PassingFilesFolder , onerror = remove_readOnly)
os.mkdir(PassingFilesFolder)

if(os.path.exists(FailingFilesFolder)):
        shutil.rmtree(FailingFilesFolder , onerror = remove_readOnly)
os.mkdir(FailingFilesFolder)

#Verifying the Passing and Failing csv's
PassingCsvPath = os.path.join (PassFailFolderPath , 'PassingFiles.csv')
FailingCsvPath = os.path.join (PassFailFolderPath , 'FailingFiles.csv')

if(not os.path.exists(PassingCsvPath)):
    print 'Passing csv not found.'
    sys.exit(1)

if(not os.path.exists(FailingCsvPath)):
    print 'Failing csv not found.'
    sys.exit(1)

#Reading the Passing/Failing dgn's names from the CSV's, locate them and place them in the respective folder
with open(PassingCsvPath , 'rb') as PassingCsv:
    Reader = csv.DictReader(PassingCsv , delimiter=',')
    for row in Reader:
        Name = row['File Name']
        withoutExt = os.path.splitext(Name)[0]
        withExtFileName = withoutExt + '.idgndb'
        srcPath = os.path.join(ConvertedFilesFolder , withExtFileName)
        
        #Copying passing files to PassingFiles folder 
        if (os.path.exists(srcPath)):
            shutil.copy(srcPath , PassingFilesFolder)
        else:
            withExtFileName = withoutExt + '.ibim'
            srcPath = os.path.join(ConvertedFilesFolder , withExtFileName)
            if(not os.path.exists(srcPath)):
                continue
            shutil.copy(srcPath , PassingFilesFolder)
        
with open(FailingCsvPath , 'rb') as FailingCsv:
    Reader = csv.DictReader(FailingCsv , delimiter=',')
    for row in Reader:
        Name = row['File Name']
        withoutExt = os.path.splitext(Name)[0]
        withExtFileName = withoutExt + '.idgndb'
        srcPath = os.path.join(ConvertedFilesFolder , withExtFileName)
        
        #Copying passing files to PassingFiles folder 
        if (os.path.exists(srcPath)):
            shutil.copy(srcPath , FailingFilesFolder)
        else:
            withExtFileName = withoutExt + '.ibim'
            srcPath = os.path.join(ConvertedFilesFolder , withExtFileName)
            if(not os.path.exists(srcPath)):
                continue
            shutil.copy(srcPath , FailingFilesFolder)             