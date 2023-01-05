import os,psutil

#This function prints the available memory of the system in MB's
def print_available_memory():
    memory = psutil.virtual_memory()
    memory_in_mb = memory.free >>20
    print "\n\n****Free memory in MB's is : %d****\n\n" %memory_in_mb

#This function returns the total number of processes running on an instance
def size_list():
    
    list = []
    for process in psutil.process_iter():
        list.append(process)
        
    list_size = len(list)
    return list_size

#Terminates the process
def kill_by_process_name(name):

    cmd = "taskkill /IM " + name + ' /T /F'
    status = os.system(cmd)

    if(status == 0):
        print "Successfully terminated process:%s" %name
    else:
        print "Error terminating process:%s" %name
        
if __name__ == '__main__':

    #Prints available memory of the system in MB's
    print_available_memory()
    
    print "\n****The number of processes initially running: %d****\n"  %size_list()

    
    processes_to_kill = ["notepad.exe", "notepad++.exe" , "chrome.exe" , "PYTHON~1.EXE" , "iTunesHelper.exe" ,"OUTLOOK.EXE" ,"Pythonwin.exe", "lynchtmlconv.exe" ,"lync.exe" , "Taskmgr.exe" , "mstsc.exe" , "spoolsv.exe" , "mDNSResponder.exe" , "PanGPS.exe" , "OneDrive.exe" ,"iPodService.exe", "jusched.exe" ,"SCNotification.exe" , "devenv.exe" , "EXCEL.EXE"]
    
    #Iterator over the list of processes to be killed
    for process_name in processes_to_kill:

        #Iterates through the list of processes and kills the unnecessary ones
        for process in psutil.process_iter():
            
            if process.name() == process_name: 
                kill_by_process_name(process_name)

    print "\n****The number of processes after killing the unnecessary processes: %d****\n"  %size_list()

    print_available_memory()