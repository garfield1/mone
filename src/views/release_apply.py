#!/usr/bin/env python
#encoding=utf-8
from ConfigParser import ConfigParser
# import json
# import os
# from django.db.models import Q
import json
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.ext.login import login_required
import time
# from models.mone.models import
# from views._release_apply import state_transfer
from models.mone.models import Application

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

@release_apply.route('/add/application/', methods=['POST'])
@login_required
def add_application():
	name = request.form.get('name')
	git_url = request.form.get('git_url')
	result = {'status': 1001, 'message': '参数缺失'}
	if name and git_url:
		try:
			application_data = Application(name=name, git_url=git_url)
			application_data.save()
			result = {'status': 200, 'message': '保存成功'}
		except Exception,e:
			result = {'status': 1001, 'message': '数据库异常'}
	return json.dumps(result)





