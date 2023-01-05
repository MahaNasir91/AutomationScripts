#-------------------------------------------------------------------------------------------
#                                     Maha Nasir                               04/2018
#-------------------------------------------------------------------------------------------
import os, sys , argparse , shutil
import xml.etree.ElementTree as ET
import ntpath
from Run import runCommand,createDirectory 

#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    03/2018
#-------------------------------------------------------------------------------------------
#Walks through the dataset directory and copies the file from the directory to the given output location 
def locate_and_copy(DatasetDir, OutputDir):
    for (dirpath, dirnames, filenames) in os.walk(DatasetDir):
        for filename in filenames:
            if filename.endswith('.bim'):
                    file_path = os.path.join(dirpath , filename)
                    if os.path.isfile(file_path):
                        if not os.path.exists(os.path.join(OutputDir , filename)):
                            shutil.copy(file_path , OutputDir)
                            print 'Copied Dgn: ' +  filename

def removeFiles(DirectoryPath):
    filelist = [ f for f in os.listdir(DirectoryPath) if f.endswith(".bim") ]
    for f in filelist:
        fileName = os.path.join(DirectoryPath, f)
        os.remove(fileName)
        print 'Removed file:' + fileName
    
#Entry Point
parser = argparse.ArgumentParser()

parser.add_argument("--scriptsRoot", help="Path to the dgndbtesting repository", required=True)
parser.add_argument("--inputDir", help="Path to the directory containing the conversion dataset", required=True)
parser.add_argument("--outRoot", help="Folder path, where you want the output", required=True)
parser.add_argument("--converterExe", help="Path to exe of DgnV8Converter", required=True)
parser.add_argument("--conversionCsv", help="Path of the csv to be used for conversion", required=True)

args = parser.parse_args()

ScriptsDir = args.scriptsRoot
InputDir = args.inputDir
OutputDir = args.outRoot
ConverterExe = args.converterExe
ConversionDatasetCsvPath = args.conversionCsv

ConversionScriptsDir = os.path.join(ScriptsDir, 'DgnV8Conversion')
BulkConversionScript = os.path.join(ConversionScriptsDir , 'BulkDgnV8Conversion.py')
CustomizeXmlFile = os.path.join(ConversionScriptsDir, 'ConversionOfDiverseDataset.xml')
ImportConfigPath = os.path.join(ConversionScriptsDir , 'ImportConfigForQuickConversion.xml')

#Stripping the trailing slash in the output directory path, if there is any
if ntpath.basename(OutputDir) == "":
    OutputDir = OutputDir[:-1]
    
#Making a copy of the CustomXml file in the output directory
CustomFilePath = os.path.join(OutputDir,'ConversionOfDiverseDataset.xml')
if(os.path.exists(CustomFilePath)):
    os.remove(CustomFilePath)

shutil.copy(CustomizeXmlFile,OutputDir)
              
#Reading the Custom xml file
CopiedXmlPath = os.path.join(OutputDir,'ConversionOfDiverseDataset.xml')
print 'Copied path:' + CopiedXmlPath

tree = ET.parse(CopiedXmlPath)                              
root = tree.getroot()

#Replacing the path of the Csv with the appropriate path
customize = root.find('Customize')
data_set = customize.find('DataSetFilters')
csv_path = data_set.find('path').text
print '\nDataset Csv path1 is:' + csv_path

path = data_set.find('path').text = ConversionDatasetCsvPath
print '\nDataset Csv path is set to:' + path

#Adjusting the Import Config file path accordingly
import_config_file = customize.find("ImportConfigFile")
icf_path = import_config_file.find("path")
if icf_path.get("values") != "1":
    icf_path.set("values" , "1")

icf_path = import_config_file.find("path").text = ImportConfigPath
print '\nImport Config file path is set to:' + icf_path

tree.write(CopiedXmlPath)

#Conversion
cmd = BulkConversionScript + " --input=\""+InputDir+"\" --output=\""+OutputDir+"\" --converter=\""+ConverterExe+"\" --custom=\""+CopiedXmlPath+"\""
runCommand(cmd)

#Creating folder to place the failing files after reconversion
FolderForRecheckingFailingFiles = os.path.join(OutputDir, 'ReconfirmingFailingFiles')
createDirectory(FolderForRecheckingFailingFiles)
    
#Re-run conversion for confirming the crashes
CrossCheckingScript = os.path.join(ScriptsRoot , 'DgnV8Conversion' , 'CrosscheckFailingDgns.py')
ConversionCsv = os.path.join(OutputDir , 'Output_report.csv')
cmd = CrossCheckingScript + ' --csvPath=' + ConversionCsv + ' --datasetDir=' + InputDir + ' --workspaceRoot=' + FolderForRecheckingFailingFiles + ' --scriptsRoot=' + ScriptsRoot + ' --converterExe=' + ConverterExe
runCommand(cmd)

os.remove(CopiedXmlPath)
  
#Checks if the remote path already has files. If yes, copy them to previous folder
remotePathLatest = r"\\isbprdfs02\DgnDb\ConversionOutput\Bim0200\latest"
remotePathPrev = r"\\isbprdfs02\DgnDb\ConversionOutput\Bim0200\previous"

#Removes all the files from prev folder
removeFiles(remotePathPrev)

#Move files in the latest folder to the previous folder  
locate_and_copy(remotePathLatest,remotePathPrev)

#Removes all the files from latest folder
removeFiles(remotePathLatest)

#Copy the converted Dgns to a remote shared path
locate_and_copy(OutputDir,remotePathLatest)
