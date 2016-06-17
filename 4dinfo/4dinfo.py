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
                if row[0] != 0:
                    toappend.append(row[0])
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

