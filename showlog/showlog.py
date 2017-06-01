from django.http import HttpResponse
from django.shortcuts import render
import httplib
import os
import json

def search_logs(q, size):
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
    conn.request("POST", '/logs/_search?size=%i' % size, json.dumps(goodquery))
    response = conn.getresponse()
    data = response.read()
    o = json.loads(data)
    return o['hits']['hits']
    
def give_logs(request):
    query = request.GET.get('search', '')
    module = request.GET.get('module', '')
    limit = int(request.GET.get('limit', 50))
    size = int(request.GET.get('size', 1000))
    keep_duplicates = bool(request.GET.get('all', False))

    checked = ' checked' if keep_duplicates else ''

    formtext = ('<form>Submit query: <input type="text" name="search"> '
                'Module: <input type="text" name="module" value="%s"> '
                'Logs Limit: <input type="text" name="limit" value="%i"> '
                'Elastic Search Size: <input type="text" name="size" value="%i"> '
                'Keep Duplicates: <input type="checkbox" name="all"%s> '
                '<input type="submit"></form>' % (module, limit, size, checked))

    if query == '':
        # Get form page
        return HttpResponse(formtext)

    else:
        o = search_logs(query, size)
        if len(o) == 0:
            return HttpResponse('No logs were found!<br>' + formtext)

        texts = set()
        logs = list()

        for i in o:
            if len(texts) > limit:
                break
            if i['_source']['text'] in texts and not keep_duplicates:
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
                       'limit' : limit,
                       'size' : size,
                       'checked' : checked
                      }
                     )
