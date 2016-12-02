from django.http import HttpResponse
from django.shortcuts import render

import urllib2, json, sqlite3

def return_page(request):

    file_location = 'https://cmst2.web.cern.ch/cmst2/unified/all_errors.json'
    res  = urllib2.urlopen(file_location)
    data = json.load(res)
    res.close()

    errors_location = 'https://cmst2.web.cern.ch/cmst2/unified/explanations.json'
    res  = urllib2.urlopen(errors_location)
    errors_explained = json.load(res)
    res.close()

    conn = sqlite3.connect(':memory:')
    curs = conn.cursor()
    curs.execute('CREATE TABLE workflows (stepname varchar(255), errorcode int, sitename varchar(255), numbererrors int)')

    stepset = set()
    errorset = set()
    siteset = set()

    # Store everything into an SQL database for fast retrival

    for stepname, errorcodes in data.items():
        stepset.add(stepname)
        for errorcode, sitenames in errorcodes.items():
            errorset.add(errorcode)
            for sitename, numbererrors in sitenames.items():
                siteset.add(sitename)
                curs.execute('INSERT INTO workflows VALUES (?,?,?,?)',(stepname, errorcode, sitename, numbererrors))

    allsteps = list(stepset)
    allsteps.sort()
    allerrors = list(errorset)
    allerrors.sort()
    allsites = list(siteset)
    allsites.sort()

    # Get the dimensions passed by the user
    
    pievar = request.GET.get('pievar','errorcode')

    allmap = { # lists of elements to call for each possible row and column
        'errorcode' : allerrors,
        'stepname' : allsteps,
        'sitename' : allsites,
        }

    titlemap = {
        'errorcode' : 'code ',
        'stepname' : 'step ',
        'sitename' : 'site ',
        }

    pievarmap = { # for each pievar : ( row, column )
        'errorcode' : ('stepname', 'sitename','errorcode'),
        'sitename'  : ('stepname', 'errorcode','sitename'),
        'stepname'  : ('errorcode', 'sitename','stepname'),
        }

    # Based on the dimesions from the user, create a list of pies to show

    rowname, colname, varname = pievarmap[pievar]

    pieinfo = []
    pietitles = []
    passrow = []
    passcol = []

    sqlcall = 'SELECT {0}, numbererrors FROM workflows WHERE {1}=? AND {2}=?'.format(pievar,rowname,colname)

    colErrors = [0] * len(allmap[colname])
    rowErrors = [0] * len(allmap[rowname])

    for col in allmap[colname]:
        if colname == 'errorcode':
            passcol.append({'title' : str('\n --- \n'.join(errors_explained[col])).rstrip('\n'), 'name' : col})
        else:
            passcol.append({'title' : col, 'name' : col})

    rowCount = 0

    for row in allmap[rowname]:
        if rowname == 'stepname':
            passrow.append({'title' : row, 'name' : row.split('/')[1]})
        elif rowname == 'errorcode':
            passrow.append({'title' : str('\n --- \n'.join(errors_explained[row])).rstrip('\n'), 'name' : row})
        else:
            passrow.append({'title' : row, 'name' : row})

        pietitlerow = []

        colCount = 0

        for col in allmap[colname]:
            errorNum = 0
            toappend = []
            pietitle = ''
            if rowname != 'stepname':
                pietitle += titlemap[rowname] + ': ' + row + '\n'
            pietitle += titlemap[colname] + ': ' + col
            for piekey, errnum in curs.execute(sqlcall,(row,col)):
                if errnum != 0:
                    toappend.append(errnum)
                    if varname != 'stepname':
                        pietitle += '\n' + titlemap[varname] + str(piekey) + ': ' + str(errnum)
                    else:
                        pietitle += '\n' + titlemap[varname] + str(piekey).split('/')[1] + ': ' + str(errnum)
            pieinfo.append(toappend)
            sumErrors = sum(toappend)
            pietitle = 'Total Errors: ' + str(sumErrors) + '\n' + pietitle
            pietitlerow.append(pietitle)

            rowErrors[rowCount] += sumErrors
            colErrors[colCount] += sumErrors
            colCount += 1

        pietitles.append(pietitlerow)
        rowCount += 1

    for iRow in range(len(passrow)):
        passrow[iRow]['title'] = 'Total errors: ' + str(rowErrors[iRow]) + '\n' + passrow[iRow]['title']
    for iCol in range(len(passcol)):
        passcol[iCol]['title'] = 'Total errors: ' + str(colErrors[iCol]) + '\n' + passcol[iCol]['title']

    row_zip = zip(passrow, pietitles)

    return render(request,'4dinfo/piecharts.html',{
            'collist' : passcol,
            'pieinfo' : pieinfo,
            'rowzip' : row_zip,
            'pievar' : pievar,
            })

