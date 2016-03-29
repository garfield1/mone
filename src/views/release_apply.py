#!/usr/bin/env python
#encoding=utf-8
from ConfigParser import ConfigParser
# import json
# import os
# from django.db.models import Q
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.ext.login import login_required
import time
# from models.mone.models import
# from views._release_apply import state_transfer
config = ConfigParser()
with open('mone.conf', 'r') as cfgfile:
	config.readfp(cfgfile)
	page_size = int(config.get('page', 'page_size'))
	upload_path = config.get('path', 'upload_path')
cfgfile.close()


release_apply = Blueprint('release_apply', __name__)

@release_apply.route('/taskpad/', methods=['GET'])
@login_required
def taskpad():
	return render_template("release_apply/taskpad.html")

@release_apply.route('/add/', methods=['GET'])
@login_required
def add():
	return render_template("release_apply/add.html")

@release_apply.route('/list/', methods=['GET'])
@login_required
def list():
	return render_template("release_apply/list.html")

@release_apply.route('/detail/', methods=['GET'])
@login_required
def detail():
	return render_template("release_apply/details.html")