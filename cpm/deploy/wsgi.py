import os
import sys
from django.core.handlers.wsgi import WSGIHandler

sys.stdout = sys.stderr

from site import addsitedir
addsitedir('/home/webpowerlabs/.envs/cpm/lib/python2.7/site-packages')

from os.path import abspath, dirname, join
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'cpm.settings'
application = WSGIHandler()
