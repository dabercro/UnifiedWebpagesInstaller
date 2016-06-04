from django.http import HttpResponse
from django.shortcuts import render
import httplib
import os
import json

def search_logs(q):
    # I'm not completely sure what this does. Ask Jean-Roch.
    conn = httplib.HTTPConnection('cms-elastic-fe.cern.ch:9200')
    goodquery = {
        "query": {
            "bool": {
                "must": [
                    {
                        "wildcard": {
                            "meta": "*%s*" % q
                            }
                        },
                    ]
                }
            },
        "sort": [
            {
                "timestamp": "desc"
                }
            ],
        "_source": [
            "text",
            "subject",
            "date",
            "meta"
            ]
        }
    conn.request("POST", '/logs/_search?size=1000', json.dumps(goodquery))
    response = conn.getresponse()
    data = response.read()
    o = json.loads(data)
    return o['hits']['hits']
    
def give_logs(request):
    input = request.GET.get('search','')
    if input == '':
        # Get form page
        return HttpResponse('enter a value at the end of the url with ?search=SomeValue<br>Example: <a href=http://dabercro.web.cern.ch/dabercro/unified/showlog/?search=SUS-RunIISummer15wmLHEGS-00038>http://dabercro.web.cern.ch/dabercro/unified/showlog/?search=SUS-RunIISummer15wmLHEGS-00038</a>')

    else:
        o = search_logs(input)
        if len(o) == 0:
            return HttpResponse('No logs were found!')

        texts = set()
        logs = list()

        for i in o:
            if len(texts)>50:
                break
            if i['_source']['text'] in texts:
                continue

            logs.append(
                {
                    'subject' : i['_source']['subject'],
                    'date'    : i['_source']['date'],
                    'text'    : i['_source']['text'].split('\n')
                }
            )

            texts.add( i['_source']['text'] )

        return render(request,'showlog/table.html',
                      { 'logs' : logs, 'meta' : o[0]['_source']['meta'].split('\n') })
