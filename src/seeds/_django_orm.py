#!/usr/bin/env python
#encoding=utf-8
import sys
sys.path.append('..')
import os
os.environ['DJANGO_SETTING_MODULE']='models.zz.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "models.zz.settings")
from models.mone.models import *