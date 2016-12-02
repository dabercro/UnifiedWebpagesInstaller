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
    query = request.GET.get('search', '')
    module = request.GET.get('module', '')
    limit = int(request.GET.get('limit', 50))

    formtext = ('<form>Submit query: <input type="text" name="search"> '
                'Module: <input type="text" name="module" value="%s"> '
                'Logs Limit: <input type="text" name="limit" value = "%i"> '
                '<input type="submit" value="Submit"></form>' % (module, limit))

    if query == '':
        # Get form page
        return HttpResponse(formtext)

    else:
        o = search_logs(query)
        if len(o) == 0:
            return HttpResponse('No logs were found!<br>' + formtext)

        texts = set()
        logs = list()

        for i in o:
            if len(texts) > limit:
                break
            if i['_source']['text'] in texts:
                continue

            if not module or  i['_source']['subject'] == module:
                logs.append(
                    {
                        'subject' : i['_source']['subject'],
                        'date'    : i['_source']['date'],
                        'text'    : i['_source']['text'].split('\n')
                    }
                )

                texts.add( i['_source']['text'] )

        return render(request, 'showlog/table.html',
                      {'logs' : logs,
                       'meta' : o[0]['_source']['meta'].split('\n'),
                       'search' : query,
                       'module' : module,
                       'limit' : limit
                      }
                     )
