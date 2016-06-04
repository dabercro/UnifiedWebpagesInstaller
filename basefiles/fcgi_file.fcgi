#!/usr/bin/python2.6 

import sys, os

sys.path.insert(0, 'DJANGOPREFIX')
sys.path.insert(0, 'FLUPLOCATION/flup-1.0.2-py2.6.egg')
sys.path.insert(0, 'USERHOME/www/PROJECTNAMEHERE') 

os.environ['DJANGO_SETTINGS_MODULE'] = 'PROJECTNAMEHERE.settings' 

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')
