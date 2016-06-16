from django.http import HttpResponse
from django.shortcuts import render

import urllib2, json, sqlite3

def return_page(request):

    file_location = 'https://cmst2.web.cern.ch/cmst2/unified/all_errors.json'
    res  = urllib2.urlopen(file_location)
    data = json.load(res)
    res.close()

    conn = sqlite3.connect(':memory:')

    return render(request,'4dinfo/piecharts.html',{})
