import sys
import datetime
import os
import fnmatch
import re
import xlsxwriter


sys.path.append(r'C:\bsw\bim0200Win64TypeScript\src\DgnDbTestingScripts\CommonTasks')

if(len(sys.argv)==3):
    print 'inside report generation script, report is placed at OutPutPath\Winx64'
    stream=str(sys.argv[1])
    pth=str(sys.argv[2])
    now=datetime.datetime.now()
    datee=str(now.month)+':'+str(now.day)+':'+str(now.year)

    passCount=0
    failCount=0
    disableCount=0

    workbook = xlsxwriter.Workbook(pth+'/Winx64/'+stream+'TypeScriptTests.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('C1', 'UNIT TESTS EXECUTION-Win64TypeScript')
    worksheet.write('A3', 'Stream')
    worksheet.write('B3', str(stream))
    worksheet.write('A4','Date')
    worksheet.write('B4', datee)
    worksheet.write('A7', 'TEST NAME')
    worksheet.write('E7', 'STATUS')
    index=9
    
    myfile=open(pth+'/Winx64/TypeScriptTestsLog.txt','rb')
    passc=0
    failc=0
    disablec=0
    if os.stat(pth+'/Winx64/TypeScriptTestsLog.txt').st_size==0:
        print "Log is empty"
        worksheet.write('A'+str(index), 0)
        worksheet.write('E'+str(index), 0)
    else:
        for line in myfile:
            if '[     PASS ]' in line:
                if ' : ' in line:
                    temp = line.split(" ")
                    worksheet.write('A'+str(index), temp[10])
                    worksheet.write('E'+str(index), temp[8])
                    index = index +1
                    if temp[8] == 'Passed':
                        passc = passc + 1
                    elif temp[8] == 'Disabled':
                        disablec = disablec + 1
    worksheet.write('M2','Total')
    worksheet.write('N2',passc+disablec)
    worksheet.write('M3','Passed')
    worksheet.write('N3',passc)
    worksheet.write('M4','Disable')
    worksheet.write('N4',disablec)
    workbook.close()
    
else:
    print "Please enter valid arguments which are stream name and src path"
