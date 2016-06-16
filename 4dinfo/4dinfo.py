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

    # Store everything into an SQL database for fast retrival

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

    # Based on the dimesions from the user, create a list of pies to show

    pieinfo = []
    pietitles = []
    passstep = []
    for step in allsteps:
        passstep.append({'name' : step, 'parent' : step.split('/')[1]})
        pietitlerow = []
        for site in allsites:
            errorNum = 0
            toappend = []
            pietitle = 'site: ' + site
            for row in curs.execute('SELECT numberErrors, errorcode FROM workflows WHERE stepName=? AND siteName=?',(step,site)):
                toappend.append(row[0])
                if row[0] != 0:
                    pietitle += '\ncode ' + str(row[1]) + ': ' + str(row[0])
            pieinfo.append(toappend)
            pietitlerow.append(pietitle.rstrip('\n'))

        pietitles.append(pietitlerow)

    steps_titles = zip(passstep, pietitles)

    return render(request,'4dinfo/piecharts.html',{
            'site_list' : allsites,
            'pieinfo' : pieinfo,
            'steps_titles' : steps_titles,
            })

