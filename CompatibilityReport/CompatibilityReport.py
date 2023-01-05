import os
import sys
import csv
import xlsxwriter

# for unicode issue
reload(sys)
sys.setdefaultencoding('Cp1252')


def getFormats(wb):
    headingFormat = wb.add_format({'color': 'blue', 'bold': 1, 'size': 16, 'align': 'center', 'text_wrap': 1})
    verticalFormat = wb.add_format({'color': 'blue', 'bold': 1, 'size': 16, 'align': 'center', 'text_wrap': 1})
    verticalFormat.set_rotation(90)
    heading2 = wb.add_format({'color': 'brown', 'bold': 1, 'size': 12, 'text_wrap': 1})
    headingFormat.set_align('vcenter')
    linkFormat = wb.add_format({'color': 'blue', 'underline': True})
    percentFormat = wb.add_format({'num_format' : '0%', 'color': 'brown', 'bold': 1, 'size': 12, 'text_wrap': 1})
    numFormat = wb.add_format({'num_format': '#,##0.#0'})
    return {'heading1': headingFormat, 'heading2': heading2, 'link': linkFormat, 'percent': percentFormat, 'num': numFormat, 'vertical': verticalFormat}

def create_chart(wb, title, type, cats, vals, xAxisTitle, chartName, labels):
    chart = wb.add_chart({'type': type ,
                          'name': chartName})
    chart.add_series({'name' : 'None',
                      'categories' : '=(' + cats + ')',
                      'values': '=(' + vals + ')',
                      'data_labels': {'value': labels}})
    chart.set_legend({'none': True})
    chart.set_title({'name': title})
    chart.set_x_axis({'name' : xAxisTitle,
                      'major_gridlines': {'visible': False}})
    chart.set_size({'width': 500, 'height': 275})
    return chart

def generatePieChart(wb, cats, vals, chartTitle, chartName):
    chart = wb.add_chart({'type': 'pie' ,
                          'name': chartName})
    chart.add_series({'name' : 'None',
                      'categories' : '=('+ cats + ')',
                      'values': '=(' + vals + ')',
                      'points': [
                                {'fill': {'color': 'green'}},
                                {'fill': {'color': 'orange'}},
                                ],
                      'data_labels': {'value': 1, 'position': 'center', 'font': {'color': 'white', 'bold': True}}})
    chart.set_title({'name': chartTitle ,
                    'name_font': {'color': 'blue'}})
    chart.set_size({'width': 372, 'height': 400})
    return chart
    
def populateSheet(wb, ConvertedThrough, TestedIn, statusCounts):
    sheetName = ConvertedThrough + TestedIn
    ws = wb.add_worksheet(sheetName)
    formats = getFormats(wb)
    ws.set_column(0,0,10)
    ws.set_column(1,4,30)
    
    ws.write('B1', "Converted Through", formats['heading1'])
    ws.write('C1', ConvertedThrough, formats['heading1'])
    ws.write('D1', "Tested In", formats['heading1'])
    ws.write('E1', TestedIn, formats['heading1'])
    ws.write('D3', "Total Files", formats['heading2'])
    ws.write('E3', statusCounts['Total'], formats['heading2'])
    ws.write('D4', "Passed", formats['heading2'])
    ws.write('E4', statusCounts['SUCCESS'], formats['heading2'])
    ws.write('D5', "Failed", formats['heading2'])
    ws.write('E5', statusCounts['Total'] - statusCounts['SUCCESS'], formats['heading2'])
    ws.write('D6', "%age Pass", formats['heading2'])
    ws.write('E6', float(statusCounts['SUCCESS']) / float(statusCounts['Total']), formats['percent'])
    wb.define_name(sheetName + 'percent', '=' + sheetName + '!E6')
    chart = generatePieChart(wb, sheetName + '!D4:D5', sheetName + '!E4:E5', sheetName + " - Summary", sheetName + "1")
    ws.insert_chart('B3', chart)

    ws.merge_range('D23:E23', "Failure Analysis", formats['heading1'])
    ws.write('D24', "Failure Type", formats['heading2'])
    ws.write('E24', "Count", formats['heading2'])
    rowNo = 25
    i = 0
    cats = sheetName + '!D' + str(rowNo)
    vals = sheetName + '!E' + str(rowNo)
    for status in statusCounts:
        if status == "Total" or status == "SUCCESS":
            continue
        else:
            ws.write(rowNo + i, 3, status)
            ws.write(rowNo + i, 4, statusCounts[status])
            i = i + 1

    cats = cats + ':D' + str(rowNo + i)
    vals = vals + ':E' + str(rowNo + i)
    chart = create_chart(wb, "Failure Analysis", 'bar', cats, vals, '', 'FailureAnalysis', 'None')
    ws.insert_chart('A24', chart)

def populateSummary(wb, ws, branches):
    formats = getFormats(wb)
    ws.merge_range('D1:G1', "Compatability Matrix with %age Passing Summary", formats['heading1'])
    ws.merge_range('D2:G2', dateToday, formats['heading1'])
    leftborderFormat = wb.add_format({'left': 2})
    bottomborderFormat = wb.add_format({'bottom' : 2})
    topborderFormat = wb.add_format({'top' : 2})
    rightborderFormat = wb.add_format({'right': 2})
    rowNo = 4
    colNo = 3
    offset = len(branches)
    ws.merge_range(rowNo - 2, colNo + 1, rowNo - 2, colNo + offset, "", bottomborderFormat)
    ws.write(rowNo - 1, colNo + offset + 1, "", leftborderFormat)
    ws.write(rowNo , colNo + offset + 1, "", leftborderFormat)
    ws.write(rowNo - 1, colNo, "", rightborderFormat)

    ws.merge_range(rowNo - 1, colNo + 1, rowNo - 1 , colNo + offset, "Tested In", formats['heading1'])
    headFormat = wb.add_format({'top': 2, 'left': 2, 'right': 2, 'color': 'blue', 'bold': 1, 'size': 16, 'align': 'center', 'text_wrap': 1})
    leftHead = wb.add_format({'color': 'brown', 'bold': 1, 'size': 12, 'text_wrap': 1, 'right': 2})
    TopHead = wb.add_format({'color': 'brown', 'bold': 1, 'size': 12, 'text_wrap': 1, 'bottom': 2})
    linkFormat = wb.add_format({'color': 'blue', 'underline': True})
    ws.write(rowNo, colNo, "Converted Through", headFormat)
    ws.set_column(colNo, colNo, 50)
    ws.set_row(rowNo, 40)
    i = 1
    lastRow = 0
    for ConvertedThrough in branches:
        ws.write(rowNo + i, colNo - 1, "", rightborderFormat)
        ws.write(rowNo + i, colNo, str(ConvertedThrough), leftHead)
        j = 1
        for TestedIn in branches:
            ws.write(rowNo, colNo + j, str(TestedIn), TopHead)
            if ConvertedThrough == TestedIn:
                ws.write(rowNo + i, colNo + j, "N/A")
            else:
                sheetName = ConvertedThrough + TestedIn
                found = False
                for worksheet in wb.worksheets():
                    if worksheet.get_name() == sheetName:
                        found = True
                if found == True:
                    ws.write(rowNo + i, colNo + j, '=' + sheetName + '!E6', formats['percent'])
                else:
                    ws.write(rowNo + i, colNo + j, "N/A")
            j = j + 1
            lastRow = j
        ws.write(rowNo + i, colNo + j, "", leftborderFormat)
        i = i + 1
        ws.set_column(colNo, colNo - 1 + j, 20)
    for k in range(lastRow):
        ws.write(rowNo + i, colNo + k, "", topborderFormat)
    ws.write(rowNo + i + 2, colNo, "Please visit the individual sheets for more details")

def fillDetails(wb, compCSV):
    formats = getFormats(wb)
    ws = wb.add_worksheet('Details')
    csvfile = open(compCSV, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    rowNo = 1
    rowNo = 1
    ws.set_column(0, 3, 20)
    ws.write(0, 0, "File Name", formats['heading2'])
    ws.write(0, 1, "Converted Through", formats['heading2'])
    ws.write(0, 2, "Tested In", formats['heading2'])
    ws.write(0, 3, "Status", formats['heading2'])
    next(reader) # To skip header
    for row in reader:
        ws.write(rowNo, 0, row[0])
        ws.write(rowNo, 1, row[1])
        ws.write(rowNo, 2, row[2])
        ws.write(rowNo, 3, row[3])
        rowNo = rowNo + 1
        
def parseCSV(compCSV, dict, colNo):
    csvfile = open(compCSV, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    next(reader) # To skip header
    for row in reader:
        toAdd = row[colNo].strip()
        if not dict.has_key(toAdd):
            dict.setdefault(toAdd)
        toAdd = row[colNo + 1].strip()
        if not dict.has_key(toAdd):
            dict.setdefault(toAdd)
    return dict

def getCounts(compCSV, ConvertedThrough, TestedIn):
    csvfile = open(compCSV, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    next(reader) # To skip header
    statusCounts = {"Total": 0, "SUCCESS" : 0, "ERROR_FileOpeningFailed":0, "ERROR_BadElement":0, "ERROR_ModelInsertFailed":0, "ERROR_ModelFillFailed":0, "ERROR_BadModel":0}
    totalCount = 0
    for row in reader:
        if row[1].strip() == ConvertedThrough:
            if row[2].strip() == TestedIn:
                for status in statusCounts:
                    if row[3].strip() == status:
                        statusCounts[status] = statusCounts[status] + 1
                        statusCounts["Total"] = statusCounts["Total"] + 1
    return statusCounts

def mergeCSVs(path):
    oneCSV = os.path.join(path, 'AllEntries.CSV')
    f = open(oneCSV, 'wb')
    writer = csv.writer(f)
    writer.writerow(('FileName', 'ConvertedThrough', 'TestedIn', 'FileOpeningStatus'))
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.csv'):
                f1 = open(os.path.join(path, file), 'r')
                reader = csv.reader(f1)
                next(reader)
                for row in reader:
                    writer.writerow((row[0], row[1].replace('-', '_'), row[2].replace('-', '_'), row[3]))
    return oneCSV
    
def generateReport(compCSV, outputFilePath):
    wb = xlsxwriter.Workbook(outputFilePath)
    wsSumm = wb.add_worksheet('Summary')

    print '*** Generating Sheet for each run ***'
    branches = {}
    branches = parseCSV(compCSV, branches, 1)
    
    for ConvertedThrough in branches:
        for TestedIn in branches:
            if ConvertedThrough != TestedIn:
                statusCounts = getCounts(compCSV, ConvertedThrough, TestedIn)
                if statusCounts["Total"] > 0:
                    populateSheet(wb, ConvertedThrough, TestedIn, statusCounts)

    populateSummary(wb, wsSumm, branches)
    fillDetails(wb, compCSV)
    wb.close()
    print '*** Done. See the report at: ' + outputFilePath + ' ***'

if len(sys.argv) < 4:
    print '*** ERROR ***'
    print "Correct usage CompatabilityReport.py D:\InputCSVs currentDate D:\CompatibilitySummary.xlsx"
else:
    oneCSV = mergeCSVs(sys.argv[1])
    dateToday = sys.argv[2]
    generateReport(oneCSV, sys.argv[3])