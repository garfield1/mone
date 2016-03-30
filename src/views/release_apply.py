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
from models.mone.models import Application, ReleaseApply, User, Role

config = ConfigParser()
with open('mone.conf', 'r') as cfgfile:
	config.readfp(cfgfile)
	page_size = int(config.get('page', 'page_size'))
	upload_path = config.get('path', 'upload_path')
cfgfile.close()


release_apply = Blueprint('release_apply', __name__)

@release_apply.route('/add/application/', methods=['GET'])
@login_required
def add_application():
	return render_template("release_apply/add_application.html")

@release_apply.route('/taskpad/', methods=['GET'])
@login_required
def taskpad():
	return render_template("release_apply/taskpad.html")

@release_apply.route('/add/release_apply/', methods=['GET'])
@login_required
def add_release_apply():
	producter_list = []
	tester_list = []
	producter_datas = Role.objects.filter(name__contains="产品经理")[0].user.all()
	tester_datas = Role.objects.filter(name__contains="测试工程师")[0].user.all()
	for producter_data in producter_datas:
		print producter_data.id
		producter_list.append({'user_id': producter_data.id, 'username': producter_data.username})
	for tester_data in tester_datas:
		tester_list.append({'user_id': tester_data.id, 'username': tester_data.username})
	return render_template("release_apply/add.html", producter_list=producter_list, tester_list=tester_list)

@release_apply.route('/get/application_list/')
@login_required
def get_application_list():
	user_id = session.get('user_data').get('user_id')
	try:
		user_data = User.objects.filter(id=user_id)[0]
	except Exception,e:
		user_data = None
	application_list = []
	result = {'status': 1001, 'message': '用户不存在', 'data': {'application_list': []}}
	if user_data:
		applications = user_data.application_set.all()
		for application in applications:
			application_list.append({'id': application.id, 'name': application.name, 'git_url': application.git_url})
		result = {'status': 200, 'message': '请求成功', 'data': {'application_list': application_list}}
	return json.dumps(result)


@release_apply.route('/list/', methods=['GET'])
@login_required
def list():
	return render_template("release_apply/list.html")

@release_apply.route('/detail/', methods=['GET'])
@login_required
def detail():
	return render_template("release_apply/details.html")

@release_apply.route('/update/application/', methods=['POST'])
@login_required
def update_application():
	name = request.form.get('name')
	git_url = request.form.get('git_url')
	user_id = session.get('user_data').get('user_id')
	application_id = request.form.get('application_id')
	result = {'status': 1001, 'message': '参数缺失'}
	if name and git_url:
		if application_id:
			try:
				Application.objects.get(id=application_id).update(name=name, git_url=git_url)
				result = {'status': 200, 'message': '保存成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
		else:
			try:
				application_data = Application(name=name, git_url=git_url, apply_user_id=user_id)
				application_data.save()
				result = {'status': 200, 'message': '保存成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
	return json.dumps(result)

@release_apply.route('/update/release_apply/', methods=['POST'])
def update_release_apply():
	title = request.form.get('title')
	tester_id = request.form.get('tester_id')
	producter_id = request.form.get('producter_id')
	release_type = request.form.get('release_type')
	risk_level = request.form.get('risk_level')
	application_id = request.form.get('application_id')
	deploy = request.form.get('deploy')
	planned_at = request.form.get('planned_at')
	wiki_url = request.form.get('wiki_url')
	jira_url = request.form.get('jira_url')
	is_self_test = request.form.get('is_self_test')
	release_apply_id = request.form.get('release_apply_id')
	result = {'status': 1001, 'message': '参数缺失'}
	if title and application_id and is_self_test:
		if release_apply_id:
			try:
				ReleaseApply.objects.get(id=release_apply_id).update(tester_id=tester_id, producter_id=producter_id, release_type=release_type,
																 	risk_level=risk_level, application_id=application_id, deploy=deploy,
																 	planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
																 	is_self_test=is_self_test)
				result = {'status': 200, 'message': '更新成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
		else:
			try:
				releaseapply_data = ReleaseApply(tester_id=tester_id, producter_id=producter_id, release_type=release_type,
									risk_level=risk_level, application_id=application_id, deploy=deploy,
									planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
									is_self_test=is_self_test)
				releaseapply_data.save()
				result = {'status': 200, 'message': '保存成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
	return json.dumps(result)













