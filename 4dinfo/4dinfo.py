from django.http import HttpResponse
from django.shortcuts import render

import urllib2, json, sqlite3

def return_page(request):

    file_location = 'https://cmst2.web.cern.ch/cmst2/unified/all_errors.json'
    res  = urllib2.urlopen(file_location)
    data = json.load(res)
    res.close()

    conn = sqlite3.connect(':memory:')
    curs = conn.cursor()
    curs.execute('CREATE TABLE workflows (stepName varchar(255), requestName varchar(255), errorCode int, siteName varchar(255), numberErrors int)')

    allsteps = set()
    allerrors = set()
    allsites = set()

    for stepname in data.keys():
        allsteps.add(stepname)
        requestname = ''
        if len(stepname.split('/')) > 1:
            requestname = stepname.split('/')[1]
        for errorcode in data[stepname].keys():
            allerrors.add(errorcode)
            for sitename in data[stepname][errorcode].keys():
                allsites.add(sitename)
                numbererrors = data[stepname][errorcode][sitename]
                curs.execute('INSERT INTO workflows VALUES (?,?,?,?,?)',(stepname, requestname, errorcode, sitename, numbererrors))

    pieinfo = []
    for step in allsteps:
        for site in allsites:
            errorNum = 0
            toappend = []
            for row in curs.execute('SELECT numberErrors FROM workflows WHERE stepName=? AND siteName=?',(step,site)):
                toappend.append(row[0])
            pieinfo.append(toappend)

    return render(request,'4dinfo/piecharts.html',{
            'step_list' : allsteps,
            'site_list' : allsites,
            'pieinfo' : pieinfo,
            })
