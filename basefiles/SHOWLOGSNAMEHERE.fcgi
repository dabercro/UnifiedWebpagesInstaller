#!/usr/bin/python2.6 

import sys, os

# These might be buggy. Let me know if these paths should be changed.
sys.path.insert(0, os.environ.get('HOME') + '/.local')
sys.path.insert(0, '/afs/cern.ch/user/d/dabercro/public/FlupForDjango/flup-1.0.2-py2.6.egg')
sys.path.insert(0, os.environ.get('HOME') + '/www/SHOWLOGSNAMEHERE') 

os.environ['DJANGO_SETTINGS_MODULE'] = 'SHOWLOGSNAMEHERE.settings' 

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')
