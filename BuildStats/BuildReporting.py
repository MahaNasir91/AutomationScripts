#--------------------------------------------------------------------------------------
#
#     $Source: CommonTasks/BuildReporting.py $
#
#  $Copyright: (c) 2018 Bentley Systems, Incorporated. All rights reserved. $
#
#--------------------------------------------------------------------------------------
import requests, base64, os, sys, argparse, re
from datetime import datetime
from requests_ntlm import HttpNtlmAuth
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go
import datetime,time
import dateutil.parser
from calendar import timegm
import sqlite3
import numpy as np
#from palettable.colorbrewer.qualitative import Pastel1_7
plt.style.use('ggplot')

class TFSbuild:

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Sets the credentials 
    #------------------------------------------------------------------------------------------- 
    def SetCredentials(self,username,password):
        self.username=username
        self.password=password

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018      
    # Gets the build data against the credentials
    #-------------------------------------------------------------------------------------------
    def buildresult(self,number): 
        if hasattr(self,"username") and hasattr(self,"password"):
            uploadapi ="http://tfs.bentley.com:8080/tfs/ProductLine/Platform%20Technology/_apis/build/builds/"+number+"?api-version=3.0"
            tfs=requests.get(uploadapi,auth=HttpNtlmAuth(self.username,self.password))
            return tfs.json()
        else:
            print "Set credentials"

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Gets all the build definitions   
    #-------------------------------------------------------------------------------------------       
    def GetDefinitionIds(self):
        uploadapi ="http://tfs.bentley.com:8080/tfs/ProductLine/Platform%20Technology/_apis/build/definitions?api-version=3.0"
        tfs=requests.get(uploadapi,auth=HttpNtlmAuth(self.username,self.password))
        dic=tfs.json()
        return dic

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Returns the build info against the provided build definition id  
    #-------------------------------------------------------------------------------------------       
    def GetBuildInfo(self , bd_id):
        api ="http://tfs.bentley.com:8080/tfs/ProductLine/Platform%20Technology/_apis/build/builds?definitions="+str(bd_id) +"&api-version=3.0"
        print 'Running API:' + api
        tfs=requests.get(api,auth=HttpNtlmAuth(self.username,self.password))
        dict=tfs.json()
        return dict

    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     08/2018
    # Returns the results againts the provided url 
    #-------------------------------------------------------------------------------------------       
    def RunUrl(self, url):
        print 'Running URL:' + url
        tfs=requests.get(url,auth=HttpNtlmAuth(self.username,self.password))
        dict=tfs.json()
        return dict
    
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maryam Shahid                     07/2018
    # Plots a graph for the reasons for the build failures
    #-------------------------------------------------------------------------------------------
    def PlotGraphForFailedTasks(self,failedtask,path):
        saver, count = np.unique(np.array(failedtask), return_counts=True)
        temp=np.argsort(count)
        count=count[temp]
        saver=saver[temp]
        counts=((count/float(sum(count)))*100)
        counts=counts.round(0)
        
        bar=plt.barh(np.arange(len(saver)),count,align='center' ,color='#6E8B3D',height=0.5)
        plt.yticks(np.arange(len(saver)+1), saver,color='g')
        #plt.xticks(np.arange(0, max(count)+2, step=1),color='g')
        plt.xlabel('Frequency',color='g')
        plt.title('Reasons for Failed Builds',color='g')

        i=0
        for rect in bar:
            plt.text( count[i]/2.0,rect.get_y()+rect.get_height()/2.0-0.25, '%s' % str(int(counts[i]))+'%', ha='center', va='bottom',color='black') 
            i+=1    

        plt.savefig(path+"\\ReasonForBuildFailures.png",bbox_inches='tight')
        plt.close()
        
    #------------------------------------------------------------------------------------------------------------
    # bsimethod                                     Maryam Shahid                                     07/2018 
    # Plots a graph between the persons responsible for the buildfailures against the frequency of build failures
    #------------------------------------------------------------------------------------------------------------
    def FailedByGraph(self,Name,path):
        Name, count1 = np.unique(np.array(Name), return_counts=True)
        temp1=np.argsort(count1)
        count1=count1[temp1]
        Name=Name[temp1]
        counts1=((count1/float(sum(count1)))*100)
        counts1=counts1.round(0)
        
        bar=plt.barh(np.arange(len(Name)) ,count1,color='#6E8B3D',align='center',height=0.5 )
        plt.yticks(np.arange(len(Name)+1), Name,color='g')
        #plt.xticks(np.arange(0, max(count1)+2, step=1),color='g')
        plt.xlabel('Frequency',color='g')
        plt.title('Failed By',color='g')

        i=0
        for rect in bar:
            plt.text(count1[i]/2.0 ,rect.get_y()+rect.get_height()/2.0-0.25, '%s' % str(int(counts1[i]))+'%', ha='center', va='bottom',color='black')
            i+=1
            
        plt.savefig(path+"\\BuildFailedBy.png",bbox_inches='tight')
        plt.close()


    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Creates database
    #-------------------------------------------------------------------------------------------
    def CreateDatabase(self):

        #Checking if the tables already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BuildDefinitions'")
        result = cursor.fetchall()
        if not result:
            cursor.execute('''CREATE TABLE BuildDefinitions
            (BuildId   INTEGER PRIMARY KEY,
            Name        TEXT NOT NULL,
            Count INTEGER);''')
            print "Table BuildDefinitions created successfully";
        else:
            print 'Table BuildDefinitions already exists.'

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BuildInfo'")
        result = cursor.fetchall()

        if not result:
            cursor.execute('''CREATE TABLE BuildInfo
            (BuildID INTEGER PRIMARY KEY,
            BuildDefID INTEGER,
            BuildNumber TEXT,
            Status  TEXT,
            Result TEXT,
            QueueTime TEXT,
            StartTime TEXT,
            FinishTime TEXT,
            SelfHref VARCHAR,
            WebHref VARCHAR,
            TimelineHref VARCHAR,
            PlanId TEXT,
            Url VARCHAR,
            DefinitionName TEXT,
            DefinitionUrl VARCHAR,
            DefinitionPath VARCHAR,
            DefinitionType TEXT,
            DefinitionRevision INTEGER,
            DefinitionProjectId TEXT,
            DefinitionProjectName TEXT,
            DefinitionProjectUrl VARCHAR,
            DefinitionProjectState TEXT,
            DefinitionProjectRevision INTEGER,
            DefinitionProjectVisibility TEXT,
            ProjectId TEXT,
            ProjectName TEXT,
            ProjectUrl VARCHAR,
            ProjectState TEXT,
            ProjectRevision INTEGER,
            ProjectVisibility TEXT,
            Uri VARCHAR,
            SourceBranch VARCHAR,
            SourceVersion TEXT,
            QueueId INTEGER,
            QueueName TEXT,
            QueuePoolId INTEGER,
            QueuePoolName TEXT,
            Priority TEXT,
            Reason TEXT, 
            RequestedForId TEXT,
            RequestedForDisplayName TEXT,
            RequestedForUniqueName VARCHAR,
            RequestedForUrl VARCHAR,
            RequestedForImageUrl VARCHAR,
            RequestedById TEXT,
            RequestedByDisplayName TEXT,
            RequestedByUniqueName VARCHAR,
            RequestedByUrl VARCHAR,
            RequestedByImageUrl VARCHAR,
            LastChangeDate TEXT,
            LastChangeById TEXT,
            LastChangeByDisplayName TEXT,
            LastChangeByUniqueName TEXT,
            LastChangeByUrl VARCHAR,
            LastChangeByImageUrl VARCHAR,
            OrchestrationPlanId TEXT,
            LogsId INTEGER,
            LogsType TEXT,
            LogsUrl VARCHAR,
            RepoId TEXT,
            RepoType TEXT,
            RepoClean INTEGER,
            RepoSubModule BOOLEAN,
            KeepForever BOOLEAN,
            RetainedByRelease BOOLEAN,
            FOREIGN KEY (BuildDefID) REFERENCES BuildDefinitions(BuildId));''')
            print "Table BuildInfo created successfully";
        else:
            print 'Table BuildInfo already exists.'

    
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Inserts BuildDefinitionId,Name and BuildCount in BuildDefinition table, updates when required.
    #-------------------------------------------------------------------------------------------
    def InsertRecords_BuildDefinition(self):
        dic = self.GetDefinitionIds()

        for x in dic['value']:

            BuildDefinition_Id = x['id']
            BuildDefinition_Name = x['name']
         
            #Inserting records in BuildDefinitions table
            cursor.execute("SELECT * FROM BuildDefinitions WHERE BuildId=?", (BuildDefinition_Id,))
            data = cursor.fetchall()

            #If a new BuildDefinition is added to the list 
            if len(data) == 0:
                dict = self.GetBuildInfo(BuildDefinition_Id)
                BuildCount = dict['count']

                cursor.execute("INSERT INTO BuildDefinitions(BuildId,Name,Count) VALUES(?,?,?)", (BuildDefinition_Id, BuildDefinition_Name, BuildCount))
                print BuildDefinition_Id, ": ",BuildDefinition_Name, " : ",BuildCount

           #If the record against an already inserted BuildDefinitionId needs to be updated
            elif len(data) != 0:
                dict = self.GetBuildInfo(BuildDefinition_Id)
                NewBuildCount = dict['count']
                                     
                #Iterating through the db to check if the Build count against each build definition needs to be updated or not
                for row in data:
                    OldBuildCount = row[2]
                    BuildId = row[0]
            
                    if NewBuildCount != OldBuildCount:
                        cursor.execute("UPDATE BuildDefinitions SET Count=? WHERE BuildId=?", (NewBuildCount,BuildId))
                        db.commit()
                        print 'Updated buildCount for ' + row[1] + ' from ' + str(OldBuildCount) + ' to ' + str(NewBuildCount)

         
    #-------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    #-------------------------------------------------------------------------------------------
    def InsertRecords_BuildInfo(self):
        dic = self.GetDefinitionIds()
        
        for x in dic['value']:

            BuildDefinitionId = x['id']
            BuildCount = dic['count']

            dict = self.GetBuildInfo(BuildDefinitionId)
           
            for item in dict['value']:

                #Getting th field values from the API
                SelfHref = item['_links']['self']['href']
                WebHref = item['_links']['web']['href']
                TimelineHref = item['_links']['timeline']['href']
                PlanId = item['plans'][0]['planId']
                BuildId = item['id']
                BuildNumber = item['buildNumber']
                Status = item['status']
                if (Status == 'inProgress' or Status == 'notStarted' or Status == 'cancelling'):
                    continue
                Result = item['result']
                QueueTime = item['queueTime']
                StartTime = item['startTime']
                FinishTime = item['finishTime']
                Url = item['url']
                DefinitionName = item['definition']['name']
                DefinitionUrl = item['definition']['url']
                DefinitionPath = item['definition']['path']
                DefinitionType = item['definition']['type']
                DefinitionRevision = item['definition']['revision']
                DefinitionProjectId = item['definition']['project']['id']
                DefinitionProjectName = item['definition']['project']['name']
                DefinitionProjectUrl = item['definition']['project']['url']
                DefinitionProjectState = item['definition']['project']['state']
                DefinitionProjectRevision = item['definition']['project']['revision']
                DefinitionProjectVisibility = item['definition']['project']['visibility']
                ProjectId = item['project']['id']
                ProjectName = item['project']['name']
                ProjectUrl = item['project']['url']
                ProjectState = item['project']['state']
                ProjectRevision = item['project']['revision']
                ProjectVisibility = item['project']['visibility']
                Uri = item['uri']
                SourceBranch = item['sourceBranch']
                SourceVersion = item['sourceVersion']
                QueueId = item['queue']['id']
                QueueName = item['queue']['name']
                QueuePoolId = item['queue']['pool']['id']
                QueuePoolName = item['queue']['pool']['name']
                Priority = item['priority']
                Reason = item['reason']
                RequestedForId = item['requestedFor']['id']
                RequestedForDisplayName = item['requestedFor']['displayName']
                RequestedForUniqueName = item['requestedFor']['uniqueName']
                RequestedForUrl = item['requestedFor']['url']
                RequestedForImageUrl = item['requestedFor']['imageUrl']
                RequestedById = item['requestedBy']['id']
                RequestedByDisplayName = item['requestedBy']['displayName']
                RequestedByUniqueName = item['requestedBy']['uniqueName']
                RequestedByUrl = item['requestedBy']['url']
                RequestedByImageUrl = item['requestedBy']['imageUrl']
                LastChangeDate = item['lastChangedDate']
                LastChangeById = item['lastChangedBy']['id']
                LastChangeByDisplayName = item['lastChangedBy']['displayName']
                LastChangeByUniqueName = item['lastChangedBy']['uniqueName']
                LastChangeByUrl = item['lastChangedBy']['url']
                LastChangeByImageUrl = item['lastChangedBy']['imageUrl']
                OrchestrationPlanId = item['orchestrationPlan']['planId']
                LogsId = item['logs']['id']
                LogsType = item['logs']['type']
                LogsUrl = item['logs']['url']
                RepoId = item['repository']['id']
                RepoType = item['repository']['type']
                RepoClean = item['repository']['clean']
                RepoSubModule = item['repository']['checkoutSubmodules']
                KeepForever = item['keepForever']
                RetainedByRelease = item['retainedByRelease']
                           
                #Inserting records in BuildInfo table
                cursor.execute("SELECT * FROM BuildInfo WHERE BuildID=?", (BuildId,))
                data = cursor.fetchall()

                #Adds an entry in the db if a new BuildNumber is added
                if len(data) == 0:
                    cursor.execute("""INSERT INTO BuildInfo(BuildID,BuildDefID,BuildNumber,Status,Result,QueueTime,StartTime,FinishTime,SelfHref,WebHref,TimelineHref,PlanId,Url,
                                        DefinitionName,DefinitionUrl,DefinitionPath,DefinitionType,DefinitionRevision,DefinitionProjectId,DefinitionProjectName,DefinitionProjectUrl,
                                        DefinitionProjectState,DefinitionProjectRevision,DefinitionProjectVisibility,ProjectId,ProjectName,ProjectUrl,ProjectState,ProjectRevision,
                                        ProjectVisibility,Uri,SourceBranch,SourceVersion,QueueId,QueueName,QueuePoolId,QueuePoolName,Priority,Reason,RequestedForId,RequestedForDisplayName,
                                        RequestedForUniqueName,RequestedForUrl,RequestedForImageUrl,RequestedById,RequestedByDisplayName,RequestedByUniqueName,RequestedByUrl,RequestedByImageUrl,
                                        LastChangeDate,LastChangeById,LastChangeByDisplayName,LastChangeByUniqueName,LastChangeByUrl,LastChangeByImageUrl,OrchestrationPlanId,
                                        LogsId,LogsType,LogsUrl,RepoId,RepoType,RepoClean,RepoSubModule,KeepForever,RetainedByRelease) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                                        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (BuildId,BuildDefinitionId,BuildNumber,Status,Result,QueueTime,StartTime,FinishTime,SelfHref,WebHref,TimelineHref,PlanId,Url,\
                                                                                                                                                                                      DefinitionName,DefinitionUrl,DefinitionPath,DefinitionType,DefinitionRevision,DefinitionProjectId,DefinitionProjectName,DefinitionProjectUrl,\
                                                                                                                                                                                      DefinitionProjectState,DefinitionProjectRevision,DefinitionProjectVisibility,ProjectId,ProjectName,ProjectUrl,ProjectState,ProjectRevision,\
                                                                                                                                                                                      ProjectVisibility,Uri,SourceBranch,SourceVersion,\
                                                                                                                                                                                      QueueId,QueueName,QueuePoolId,QueuePoolName,Priority,Reason,RequestedForId,RequestedForDisplayName,RequestedForUniqueName,\
                                                                                                                                                                                      RequestedForUrl,RequestedForImageUrl,RequestedById,RequestedByDisplayName,RequestedByUniqueName,RequestedByUrl,RequestedByImageUrl,\
                                                                                                                                                                                      LastChangeDate,LastChangeById,LastChangeByDisplayName,LastChangeByUniqueName,LastChangeByUrl,LastChangeByImageUrl,OrchestrationPlanId,\
                                                                                                                                                                                      LogsId,LogsType,LogsUrl,RepoId,RepoType,RepoClean,RepoSubModule,KeepForever,RetainedByRelease))


                    print BuildId, ": ",Status, " : ",Result
                    db.commit()
                    

    #------------------------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Get the builds stats against a particular build def. and plots a graph for it
    #------------------------------------------------------------------------------------------------------------
    def PlotGraphForBuildStats(self, BuildDefName):
        
        cursor.execute("SELECT COUNT(*) FROM BuildInfo WHERE Result='failed' AND DefinitionName=?", (BuildDefName,))
        FailedBuildsCount = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM BuildInfo WHERE Result='partiallySucceeded' AND DefinitionName=?", (BuildDefName,))
        PartialSuccededBuildCount = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM BuildInfo WHERE Result='canceled' AND DefinitionName=?", (BuildDefName,))
        CanceledBuildCount = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM BuildInfo WHERE Result='succeeded' AND DefinitionName=?", (BuildDefName,))
        SuccededBuildCount = cursor.fetchone()[0]

        labels = ['Succeeded', 'Partially succeeded' , 'Failed' , 'Cancelled']
        values = [SuccededBuildCount,PartialSuccededBuildCount,FailedBuildsCount,CanceledBuildCount]

        y_pos = np.arange(len(labels))

        # Create horizontal bars
        bar = plt.barh(y_pos, values)
 
        # Naming on the y-axis
        plt.yticks(y_pos, labels)

        #Labelling the graph
        plt.xlabel('Frequency',color='g')
        plt.ylabel('Build Stats',color='g')
        plt.title(BuildDefName + ' Builds Stats',color='g')

        #Putting labels for bar graph
        for index,val in enumerate(values):
            #plt.text(v + 2, i + .25, str(v), color='green', ha='center', fontweight='bold')
            plt.annotate(str(val), xy=(val, index), ha='left' , va = 'center')
        
        #Saving graphs
        plt.savefig(WorkspaceRoot+"\\BuildStats.png",bbox_inches='tight')
        plt.close()

    #------------------------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Converts the given seconds into days,hours,minutes,seconds
    #------------------------------------------------------------------------------------------------------------
    def secs_to_DHMS(self, taskName , secs):

        if secs < 60:
            TotalTime = datetime.datetime.fromtimestamp(secs).strftime('%S')
            print 'The total time taken by the task "' + taskName + '" to complete in %S is : ' + TotalTime
            return TotalTime
        
        elif secs in range(60 , 3600):
            TotalTime = datetime.datetime.fromtimestamp(secs).strftime('%M:%S')
            print 'The total time taken by the task "' + taskName + '" to complete in %M:%S is : ' + TotalTime
            return TotalTime

        elif secs in range(3600 , 86400):
            TotalTime = datetime.datetime.fromtimestamp(secs).strftime('%H:%M:%S')
            print 'The total time taken by the task "' + taskName + '" to complete in %H:%M:%S is : ' + TotalTime
            return TotalTime
        
        elif secs > 86400:
            TotalTime = time.strftime("%d:%H:%M:%S", time.gmtime(secs))
            print 'The total time taken by the task "' + taskName + '" to complete in %D:%H:%M:%S is : ' + TotalTime
            return TotalTime

    #------------------------------------------------------------------------------------------------------------------------------------------------------
    # bsimethod                                                       Maha Nasir                                                          08/2018
    # Plots a graph for the max. time consuming tasks
    #------------------------------------------------------------------------------------------------------------------------------------------------------          
    def PlotGraphForMaxTimeConsumingTask(self,dict):
        plt.barh(range(len(dict)), [v[1] for k,v in dict.iteritems()], align='center')
        plt.yticks(range(len(dict)), dict.keys())
        plt.xlabel('Max time consuming task(in sec)', fontsize=12)
        plt.ylabel('Build Number', fontsize=12)
        plt.show()
        
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # bsimethod                                                       Maha Nasir                                                          07/2018
    # Get a list of all the tasks for the first 25 passing builds against the given BuildDefinitionName and returns the max time consuming task for each build
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    def FindMaxTimeConsumingTask(self, BuildDefName):
        
        dic = {}
        SortedList = []
        MaxTimeTakingTaskList = {}
        MaxTimeConsTask = ''
        rows = cursor.execute("SELECT BuildNumber,TimelineHref FROM BuildInfo WHERE Result='succeeded' AND DefinitionName=? ORDER BY BuildId DESC LIMIT 25 ", (BuildDefName,))
            
        for row in rows:

            #Clearing the lists and dictionaries for each record
            MaxTimeConsTask = None
            SortedList[:] = []
            dic.clear()
            
            BuildNumber = row[0]
            TimelineHref = row[1]
          
            dict = self.RunUrl(TimelineHref)
             
            for record in dict['records']:
                
                if record['type'] == 'Job':
                    continue

                #Gets the task name, start and finish time for each respective build 
                TaskName = record['name']
                TaskStart = record['startTime']
                TaskFinish = record['finishTime']

                TaskStartDateTime = TaskStart.split('.')[0]
                TaskFinishDateTime = TaskFinish.split('.')[0]

                if ('Z' in TaskStartDateTime):
                    TaskStartDateTime = TaskStart.split('Z')[0]
                if ('Z' in TaskFinishDateTime):
                    TaskFinishDateTime = TaskFinish.split('Z')[0]
 
                TaskStartTime_sec = round(float(TaskStart.split(':')[2].split('Z')[0]) , 2)
                TaskFinishTime_sec = round(float(TaskFinish.split(':')[2].split('Z')[0]) , 2)
                
                TaskStartDateTime = str(TaskStartDateTime[:16]) + ':' + str(TaskStartTime_sec)
                TaskFinishDateTime = str(TaskFinishDateTime[:16]) + ':' + str(TaskFinishTime_sec)

                StartDate = datetime.datetime.strptime(TaskStartDateTime , '%Y-%m-%dT%H:%M:%S.%f')
                FinishDate = datetime.datetime.strptime(TaskFinishDateTime , '%Y-%m-%dT%H:%M:%S.%f')

                if str(str(StartDate).split(' ')[1]).find('.') == -1:
                    StartDate = str(StartDate) + '.000000'

                if str(str(FinishDate).split(' ')[1]).find('.') == -1:
                    FinishDate = str(FinishDate) + '.000000'

                #Finding the time taken by each task
                fmt = '%Y-%m-%d %H:%M:%S.%f'
                
                d1 = datetime.datetime.strptime(str(StartDate), fmt)
                d2 = datetime.datetime.strptime(str(FinishDate), fmt)

                TaskTime = (d2-d1).total_seconds()  
                print 'Task:' + TaskName + ' took ' + str(TaskTime) + ' seconds to complete.' 

                dic[TaskName] = TaskTime

            #Finding the task taking the maximum time to complete
            SortedList = sorted(dic.items(), key =lambda x : x[1] , reverse=True)
            MaxTimeConsTask = max(SortedList , key=lambda x: x[1])

            MaxTimeTakingTaskList[BuildNumber] = MaxTimeConsTask
            
            print '\n*************************'
            print '\nThe task consuming the maximum time is: ' + MaxTimeConsTask[0] + '. It took ' + str(MaxTimeConsTask[1]) + ' secs to complete.'
            print '\n*************************\n'

        return MaxTimeTakingTaskList
   
    #------------------------------------------------------------------------------------------------------------
    # bsimethod                                     Maha Nasir                     07/2018
    # Get the builds histoy and plots graphs for the failed builds
    #------------------------------------------------------------------------------------------------------------
    def GetResultsAndPlotGraphs(self,name,path):
        
        #---------------------------------------fetch  id of given definition name--------------------------------------
        if hasattr(self,"username") and hasattr(self,"password"): 
            uploadapi ="http://tfs.bentley.com:8080/tfs/ProductLine/Platform%20Technology/_apis/build/definitions?name="+name+"&api-version=3.0"
            tfs=requests.get(uploadapi,auth=HttpNtlmAuth(self.username,self.password))
            
            if (not tfs.ok):
                print 'Invalid username or password or definition name.'
                exit(1)
                
            dic=tfs.json()
            buildid= dic['value'][0]['id']
            print buildid
            
            #----------------------------------fetch the builds of given definition------------------------------
            
            uploadapi ="http://tfs.bentley.com:8080/tfs/ProductLine/Platform%20Technology/_apis/build/builds?definitions="+str(buildid)+"&api-version=3.0"
            tfs=requests.get(uploadapi,auth=HttpNtlmAuth("Maha.Nasir@bentley.com","MSmd#345678e"))
            dic=tfs.json()
            val=dic['value']
            
           #------------------------get results of builds and failed tasks of builds--------------------

            #Fails if the provided build definition doesn't matches with any of the definitions        
            if not val:
                print "The provided build definition didnt match with any of the definitions. Please provide a valid build definition. Exiting"
                exit(1)
                
            results=[]
            failedtask=[]
            failedby=[]
            
            for bn in val:
                dic=self.buildresult(str(bn['id']))
                if (dic['status'] !='inProgress'):
                    results.append(str( dic['result'])) # result array

                url= dic['_links']['timeline']['href']
                tfs=requests.get(url,auth=HttpNtlmAuth(self.username,self.password))
                logs=tfs.json()

                for x in logs['records']:
                    
                    if "issues" in x:
                        for issuemsg in x['issues']: 
                            isusseStr=issuemsg['message']
                            m=re.search('exceeded the maximum execution time ',isusseStr)
                            if m:
                                failedtask.append('Exceed time')
                                failedby.append(str(dic['requestedFor']['displayName']))
                                print "Failed task  : Exceededs excecution time" , ". Build Number : ",bn['id'], " Name : ",dic['requestedFor']['displayName']
                                
                    if x['result']=='failed' and "issues" in x : 
                        print "Failed task : " ,x['name'], " Build Number : ",bn['id'], " Name : ",dic['requestedFor']['displayName']
                        failedtask.append(str(x['name']))
                        failedby.append(str(dic['requestedFor']['displayName']))

            #--------------------------------Print succeeded and failed task---------------------------------------
                        
            unique_elements, counts_elements = np.unique(np.array(results), return_counts=True)
            for x in range(len(unique_elements)):
                print unique_elements[x] , ": ",counts_elements[x]

            #---------------------------------print counts of failed task--------------------------------------- 

            unique_elements, counts_elements = np.unique(np.array(failedtask), return_counts=True)
            for x in range(len(unique_elements)):
                print unique_elements[x] , ": ",counts_elements[x]

            print "Number of Builds of   given definition: ", len(val),  "First Build ID  ",val[0]['id'] , "  Last Build ID", val[-1]['id']
            print
            if failedtask:
                self.PlotGraphForFailedTasks(failedtask,path)
            if failedby:
                self.FailedByGraph(failedby,path)
         
#-------------------------------------------------------------------------------------------
# bsimethod                                     Maha Nasir    06/2018
#-------------------------------------------------------------------------------------------
#Entry point of script
parser = argparse.ArgumentParser()

parser.add_argument("--userName", help="UserName for logging", required=True)
parser.add_argument("--password", help="Password for logging", required=True)
parser.add_argument("--buildDefinition", help="Specify the build definition against which you want to check the history")
parser.add_argument("--workspaceRoot", help="Specify the folder where you want the build history graphs", required=True)
parser.add_argument("--fromDate", help="Data retrieval from the db 'from' this date, for making graphs. The date should be in YYYY-MM-DD format")
parser.add_argument("--tillDate", help="Data retrieval from the db 'till' this date, for making graphs. The date should be in YYYY-MM-DD format")

args = parser.parse_args()
    
UserName = args.userName
Password = args.password
BuildDef = args.buildDefinition
WorkspaceRoot = args.workspaceRoot
FromDate = args.fromDate
TillDate = args.tillDate

#Verify if the workspace is a valid path
if (not os.path.exists(WorkspaceRoot)):
    print 'Please provide a valid directory path.'
    exit(1)

#Checking if the provided dates matches the required format
if FromDate:
    datetime.strptime(FromDate, "%Y-%m-%d").strftime('%Y-%m-%d')
if TillDate:
    datetime.strptime(TillDate, "%Y-%m-%d").strftime('%Y-%m-%d')

obj = TFSbuild()
obj.SetCredentials(UserName, Password)

dbPath = os.path.join(WorkspaceRoot, 'BuildHistory.db')
db = sqlite3.connect(dbPath)

cursor = db.cursor()

#Creating a database and populating it      
obj.CreateDatabase()
obj.InsertRecords_BuildDefinition()
obj.InsertRecords_BuildInfo()
db.close()

#Plots a graph for the build stats i.e passing and failing builds against the given build definition
obj.PlotGraphForBuildStats(BuildDef)

#Plots a graph for the maximum time consuming task in each build number against a given build definition
MaxTimeTakingTaskList = obj.FindMaxTimeConsumingTask(BuildDef)
if not any(MaxTimeTakingTaskList):
    print 'No succeeding builds in the dataset to plot a graph. Therfore exiting'
    exit()
    
obj.PlotGraphForMaxTimeConsumingTask(MaxTimeTakingTaskList)
#obj.GetResultsAndPlotGraphs(BuildDef,WorkspaceRoot)