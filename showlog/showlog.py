from django.http import HttpResponse
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
        metaData = ''
        if len(o) > 0:
            metaData = o[0]['_source']['meta'].replace('\n','<br>')

        res = '<!DOCTYPE HTML> <html lang=en> <head> <style type="text/css"> th{text-align:center;font-size:100%;border: 3px solid #ddc;padding:.4em} td{text-align:left;font-size:100%;border: 3px solid #ddc;padding:.2em} table{border: 1px border-collapse:collapse #ddc;width:100%} .foo {  float: left;  width: 40px;  height: 20px;  margin: 10px;} .injector {background: #cccccc} .transferor {background: #ff0000} .stagor{background: #0000ff} .assignor {background: #00ff00} .checkor {background: #ff6600} .closor{background: #9966ff} .cleanor {background: #00ffff} .rejector {background: #000000} .completor {background: #ffff00} </style> </head><body>'

        res += '<table border="3" style="border-collapse: collapse;">'
        texts=set()

        for i in o:
            if len(texts)>50:
                break
            if i['_source']['text'] in texts:
                continue

            res += '<tr><th width=60px><div class="foo '+i['_source']['subject']+'"></div></th><th>' 
            res += i['_source']['subject'] + '</th><th>' + i['_source']['date'] + '</th></tr><tr><td colspan="3"><br>'
            res += i['_source']['text'].replace('\n','<br>') + '<br></td></tr>'

            texts.add( i['_source']['text'] )

        res += '</table><br> <h3> Meta Data: </h3>' + metaData + '</body></html>'

        return HttpResponse(res)
