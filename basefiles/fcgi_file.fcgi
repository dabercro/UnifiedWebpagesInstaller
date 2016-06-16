#!/usr/bin/python2.6 

import sys, os

sys.path.insert(0, 'PREFIXLOC/lib/python2.6/site-packages')
sys.path.insert(0, 'PREFIXLOC/lib64/python2.6/site-packages')
sys.path.insert(0, 'PREFIXLOC/flup-1.0.2-py2.6.egg')
sys.path.insert(0, 'USERHOME/www/PROJECTNAMEHERE') 

os.environ['DJANGO_SETTINGS_MODULE'] = 'PROJECTNAMEHERE.settings' 

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')
