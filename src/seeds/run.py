#!/usr/bin/env python
#encoding=utf-8
import os.path,sys,shutil,os
reload(sys)
os.chdir(os.path.dirname(__file__))
sys.setdefaultencoding('utf8')
path=os.path.join(os.getcwd(),"zz")
print path
sys.path.append(path)
#from django.core.management import setup_environ
#import settings
#setup_environ(settings)
import os
os.environ['DJANGO_SETTING_MODULE']='zz.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zz.settings")

from gd.models import *
from django.db.models import Q
p=Dinner(count=1,purpose="zz")
p.save()
print len(Dinner.objects.all())
