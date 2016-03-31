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
	user_id = session.get('user_data').get('user_id')
	try:
		user_data = User.objects.filter(id=user_id)[0]
	except Exception,e:
		user_data = None
	application_list = []
	application_dict = {}
	if user_data:
		applications = user_data.application_set.all()
		for application in applications:
			application_list.append({'id': application.id, 'name': application.name})
			application_dict[application.id] = application.git_url
	producter_list = []
	tester_list = []
	producter_datas = Role.objects.filter(name__contains="产品经理")[0].user.all()
	tester_datas = Role.objects.filter(name__contains="测试工程师")[0].user.all()
	for producter_data in producter_datas:
		producter_list.append({'user_id': producter_data.id, 'username': producter_data.username})
	for tester_data in tester_datas:
		tester_list.append({'user_id': tester_data.id, 'username': tester_data.username})
	return render_template("release_apply/add.html", producter_list=producter_list, tester_list=tester_list, application_list=application_list, application_dict=application_dict)

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
	release_apply_id = request.args.get('release_apply_id')
	try:
		releaseapply_data = ReleaseApply.objects.filter(id=release_apply_id)[0]
	except Exception,e:
		releaseapply_data = None
	releaseapplystate_list = []
	if releaseapply_data:
		releaseapplystates = releaseapply_data.ReleaseApplyState.all()
		for releaseapplystate in releaseapplystates:
			releaseapplystate_list.append({'name': releaseapplystate.creator.username, 'created_at': releaseapplystate.created_at, 'state': releaseapplystate.state})
	return render_template("release_apply/details.html", releaseapply_data=releaseapply_data, releaseapplystate_list=releaseapplystate_list)

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
@login_required
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
	update_model = request.form.get('update_model')
	attention = request.form.get('attention')
	memo = request.form.get('memo')
	result = {'status': 1001, 'message': '参数缺失'}
	user_id = session.get('user_data').get('user_id')
	if title and application_id and is_self_test:
		if release_apply_id:
			try:
				ReleaseApply.objects.get(id=release_apply_id).update(tester_id=tester_id, producter_id=producter_id, release_type=release_type,
																 	risk_level=risk_level, application_id=application_id, deploy=deploy,
																 	planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
																 	is_self_test=is_self_test, update_model=update_model, attention=attention, memo=memo)
				result = {'status': 200, 'message': '更新成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
		else:
			try:
				releaseapply_data = ReleaseApply(tester_id=tester_id, applier_id=user_id, producter_id=producter_id, release_type=release_type,
									risk_level=risk_level, application_id=application_id, deploy=deploy,
									planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
									is_self_test=is_self_test, update_model=update_model, attention=attention, memo=memo)
				releaseapply_data.save()
				result = {'status': 200, 'message': '保存成功'}
			except Exception,e:
				result = {'status': 1001, 'message': '数据库异常'}
	return json.dumps(result)

def get_release_apply_by_page(page_num, **kwargs):
	start_page = page_size*(page_num-1)
	end_page = page_size*page_num
	releaseapplys = ReleaseApply.objects.filter(**kwargs).order_by('-id')[start_page: end_page]
	return releaseapplys

def get_release_apply_count(**kwargs):
	return ReleaseApply.objects.filter(**kwargs).count()

@release_apply.route('/search_release_apply/', methods=['POST'])
@login_required
def search_release_apply():
	title = request.form.get('title')
	application_id = request.form.get('application_id')
	state = request.form.get('state')
	applier = request.form.get('applier')
	tester = request.form.get('tester')
	operator = request.form.get('operator')
	producter = request.form.get('producter')
	start_planned_time = request.form.get('start_planned_time')
	end_planned_time = request.form.get('end_planned_time')
	page_num = int(request.form.get('page_num') or 1)
	start_formal_at = request.form.get('start_formal_at')
	end_formal_at = request.form.get('end_formal_at')
	kwargs = {}
	if title:
		kwargs['title__contains'] = title
	if applier:
		kwargs['applier__username__contains'] = applier
	if tester:
		kwargs['tester__username__contains'] = tester
	if operator:
		kwargs['operator__username__contains'] = operator
	if producter:
		kwargs['producter__username__contains'] = producter
	if application_id:
		kwargs['application_id'] = application_id
	if state:
		kwargs['state'] = state
	if start_planned_time:
		kwargs['planned_at__gte'] = start_planned_time
	if end_planned_time:
		kwargs['planned_at__lte'] = start_planned_time
	if start_formal_at:
		kwargs['formal_at__gte'] = start_formal_at
	if end_formal_at:
		kwargs['formal_at__lte'] = end_formal_at
	release_applys = get_release_apply_by_page(page_num, **kwargs)
	total = get_release_apply_count(**kwargs)
	page_count = total/page_size + 1
	release_apply_list = []
	for release_apply in release_applys:
		operator_name = release_apply.operator.username if release_apply.operator else ''
		applier_name = release_apply.applier.username if release_apply.applier else ''
		tester_name = release_apply.tester.username if release_apply.tester else ''
		producter_name = release_apply.producter.username if release_apply.producter else ''
		application_name = release_apply.application.name if release_apply.application else ''
		release_apply_list.append({'title': release_apply.title, 'application_name': application_name,
								   'state': release_apply.state, 'applier_name': applier_name,
								   'tester_name': tester_name, 'operator_name': operator_name,
								   'producter_name': producter_name,'apply_time': str(release_apply.created_at)[:19],
								   'planned_time': str(release_apply.planned_at)[:19], 'formal_time': str(release_apply.formal_at)[:19]})
	result = {'status': 200, 'data': {'total': total, 'page_num': page_num, 'page_count': page_count, 'release_apply_list': release_apply_list}}
	return json.dumps(result)













