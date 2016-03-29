# coding=utf-8
from ConfigParser import ConfigParser
import json
import os
from django.db.models import Q
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.ext.login import login_required
import time
from models.mone.models import Worksheet, WorksheetType, WorksheetState, User, WS_USER_ACTION_TEAM_LEADER_CONFIRMED, \
	WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED, WS_STATE_WAITTING_OPERATOR_CLAIMED, WS_STATE_WAITTING_OPERATOR_EXECUTED, \
	WS_USER_ACTION_DEVELOPER_CREATED, WS_USER_ACTION_DEVELOPER_RESUBMIT, \
	WS_USER_ACTION_TEAM_LEADER_CREATED, Role, WS_STATE_HAVE_BACK
from views._worksheet import state_transfer
config = ConfigParser()
with open('mone.conf', 'r') as cfgfile:
	config.readfp(cfgfile)
	page_size = int(config.get('page', 'page_size'))
	upload_path = config.get('path', 'upload_path')
cfgfile.close()


worksheet = Blueprint('worksheet', __name__)


@worksheet.route('/access_control/')
@login_required
def access_control():
    return render_template("user/access_control.html")


def get_worksheets_by_page(page_num, filter_type='taskpad', **kwargs):
	start_page = page_size*(page_num-1)
	end_page = page_size*page_num
	if filter_type == 'taskpad':
		worksheets = Worksheet.objects.filter(**kwargs).exclude(state='已完成').order_by('-id')[start_page: end_page]
	else:
		worksheets = Worksheet.objects.filter(**kwargs).order_by('-id')[start_page: end_page]
	return worksheets

def get_worksheets_count(filter_type='taskpad', **kwargs):
	if filter_type=='taskpad':
		return Worksheet.objects.filter(**kwargs).exclude(state='已完成').count()
	else:
		return Worksheet.objects.filter(**kwargs).count()


@worksheet.route('/taskpad/', methods=['GET'])
@login_required
def taskpad():
	taskpad_type = request.args.get('taskpad_type')
	page_num = int(request.args.get('page_num') or 1)
	if page_num < 1:
		page_num = 1
	if taskpad_type == "own":
		user_id = session.get("user_data").get("user_id")
		kwargs = {"waitting_confirmer_id": user_id}
		worksheets = get_worksheets_by_page(page_num, filter_type='taskpad', **kwargs)
		next_worksheets_num = get_worksheets_by_page(page_num+1, filter_type='taskpad', **kwargs).count()
	else:
		worksheets = get_worksheets_by_page(page_num)
		next_worksheets_num = get_worksheets_by_page(page_num+1).count()
	worksheet_list = []
	previous_page = page_num -1 if page_num > 1 else 0
	next_page = page_num + 1 if next_worksheets_num > 0 else 0
	for data in worksheets:
		worksheet_list.append({'worksheet_id': data.id, 'title': data.title, 'content': data.content, 'worksheet_type': data.worksheet_type.name, 'created_at': data.created_at, 'planned_at': data.planned_at, 'apply_name': data.applier.username, 'status': data.state })

	return render_template("worksheet/taskpad.html", worksheet_list=worksheet_list, previous_page=previous_page, next_page=next_page)

def get_own_taskpad(user_id, page_num, is_operator):
	start_page = page_size*(page_num-1)
	end_page = page_size*page_num
	if is_operator:
		worksheets = Worksheet.objects.filter(Q(applier_id=user_id)|Q(waitting_confirmer_id=user_id)|Q(state=u'待运维认领')).order_by('-id')[start_page: end_page]
	else:
		worksheets = Worksheet.objects.filter(Q(applier_id=user_id)|Q(waitting_confirmer_id=user_id)).order_by('-id')[start_page: end_page]
	return worksheets

def get_own_worksheets_count(user_id, is_operator):
	if is_operator:
		return Worksheet.objects.filter(Q(applier_id=user_id)|Q(waitting_confirmer_id=user_id)|Q(state=u'待运维认领')).count()
	else:
		return Worksheet.objects.filter(Q(applier_id=user_id)|Q(waitting_confirmer_id=user_id)).count()


@worksheet.route('/get/taskpad/', methods=['POST'])
@login_required
def get_taskpad():
	taskpad_type = request.form.get('taskpad_type')
	page_num = int(request.form.get('page_num') or 1)
	if page_num < 1:
		page_num = 1
	kwargs = {}
	user_id = session.get("user_data").get("user_id")
	if taskpad_type == "own":
		is_operator = User.objects.filter(id=user_id)[0].is_operator()
		worksheets = get_own_taskpad(user_id, page_num, is_operator)
		total = get_own_worksheets_count(user_id, is_operator)
	else:
		worksheets = get_worksheets_by_page(page_num, filter_type='taskpad', **kwargs)
		total = get_worksheets_count(filter_type='taskpad', **kwargs)
	worksheet_list = []

	page_count = total/page_size + 1
	for data in worksheets:
		worksheet_list.append({'worksheet_id': data.id, 'title': data.title, 'content': data.content, 'worksheet_type': data.worksheet_type.name, 'created_at': str(data.created_at), 'planned_at': str(data.planned_at), 'apply_name': data.applier.username, 'status': data.state })

	result = {'status': 200, 'data': {'total': total, 'page_num': page_num, 'page_count': page_count, 'worksheet_list': worksheet_list}}
	return json.dumps(result)







status_dict = {"1": u"待主管确认",
			   "2": u"待运维认领",
			   "3": u"待运维执行",
			   "4": u"已完成",
			   "5": u"待开发修改",
			   "6": u"待主管修改",
			   "7": u"已关闭上线工单"}

myworksheet_status_dict = {"1": u"工单创建",
						   "2": u"主管确认",
						   "3": u"主管待确认",}


@worksheet.route('/search_worksheet/', methods=['POST'])
@login_required
def search_worksheet():
	title = request.form.get('title')
	apply_name = request.form.get('apply_name')
	operator_id = request.form.get('operator_id')
	worksheet_type_id = request.form.get('worksheet_type_id')
	start_time = request.form.get('start_time')
	end_time = request.form.get('end_time')
	status_id = request.form.get('status')
	status = status_dict.get(status_id)
	page_num = int(request.form.get('page_num') or 1)
	myworksheet_status_id = request.form.get('myworksheet_status')
	user_id = session['user_data'].get('user_id')
	user_data = User.objects.filter(id=user_id)[0]
	kwargs = {}
	if page_num < 1:
		page_num = 1
	if myworksheet_status_id:
		if myworksheet_status_id == "1":
			worksheets, total = user_data.created_worksheets_by_pagination(current_page=page_num, pagesize=page_size)
		elif myworksheet_status_id == "2":
			worksheets, total = user_data.waitting_confirmed_worksheets_by_pagination(current_page=page_num, pagesize=page_size)
		else:
			worksheets, total = user_data.operated_worksheets_by_pagination(current_page=page_num, pagesize=page_size)
		page_count = total/page_size + 1
		worksheet_list = []
		for data in worksheets:
			operator_name = data.operator.username if data.operator else ''
			apply_name = data.applier.username if data.applier else ''
			finish_time = data.update_at if data.worksheet_type.name == '已完成' else ''
			worksheet_list.append({'worksheet_id': data.id, 'title': data.title, 'worksheet_type': data.worksheet_type.name, 'status': data.state, 'apply_time': str(data.created_at), 'finish_time': str(finish_time), 'apply_name': apply_name, 'operator_name': operator_name})

	else:
		if title:
			kwargs['title__contains'] = title
		if apply_name:
			kwargs['applier__username__contains'] = apply_name
		if operator_id:
			kwargs['operator_id'] = operator_id
		if worksheet_type_id:
			kwargs['worksheet_type_id'] = worksheet_type_id
		if start_time:
			kwargs['created_at__gte'] = start_time
		if end_time:
			kwargs['created_at__lte'] = end_time
		if status:
			kwargs['state'] = status
		worksheet_list = []
		worksheets = get_worksheets_by_page(page_num, filter_type='search', **kwargs)
		total = get_worksheets_count(filter_type='search', **kwargs)
		page_count = total/page_size + 1
		for data in worksheets:
			operator_name = data.operator.username if data.operator else ''
			apply_name = data.applier.username if data.applier else ''
			finish_time = data.updated_at if data.state == '已完成' else ''
			worksheet_list.append({'worksheet_id': data.id, 'title': data.title, 'worksheet_type': data.worksheet_type.name, 'status': data.state, 'apply_time': str(data.created_at), 'finish_time': str(finish_time), 'apply_name': apply_name, 'operator_name': operator_name})
	result = {'status': 200, 'data': {'total': total, 'page_num': page_num, 'page_count': page_count, 'worksheet_list': worksheet_list}}
	return json.dumps(result)

def get_all_operator():
	all_user_list = []
	roles = Role.objects.filter(name__contains="运维")
	for role in roles:
		user_list = role.user.all()
		all_user_list.extend(user_list)
	return list(set(all_user_list))

@worksheet.route('/')
@login_required
def worksheet_list():
	operator_list = []
	operators = get_all_operator()
	for operator in operators:
		operator_list.append({'id': operator.id, 'name': operator.username})
	worksheettype_list = []
	worksheettypes = WorksheetType.objects.all()
	for worksheet in worksheettypes:
		worksheettype_list.append({'id': worksheet.id, 'name': worksheet.name})
	return render_template("worksheet/list.html", worksheettype_list=worksheettype_list, operator_list=operator_list)


@worksheet.route('/add/', methods=['GET'])
@login_required
def add_worksheet():
	worksheet_id = request.args.get('worksheet_id')
	if worksheet_id:
		try:
			worksheet_data = Worksheet.objects.filter(id=worksheet_id)[0]
		except:
			worksheet_data = None
		user_id = session["user_data"]["user_id"]
		if worksheet_data:
			if worksheet_data.applier_id == user_id:
				worksheettype_list = []
				worksheets = WorksheetType.objects.all()
				for worksheet in worksheets:
					worksheettype_list.append({'id': worksheet.id, "name": worksheet.name})
				return render_template("worksheet/add.html", worksheettype_list=worksheettype_list, worksheet_data=worksheet_data)
			else:
				return redirect(url_for('user.index'))
	else:
		worksheettype_list = []
		worksheets = WorksheetType.objects.all()
		for worksheet in worksheets:
			worksheettype_list.append({'id': worksheet.id, "name": worksheet.name})
		worksheet_data = {"title": "", "worksheet_type_id": "", "worksheet_type": {"id": ""},  "planned_at": "", "content": ""}
		return render_template("worksheet/add.html", worksheettype_list=worksheettype_list, worksheet_data=worksheet_data)


statusid_dict ={u"关闭": 0,
	            u"待开发修改": 1,
				u"待主管修改": 1,
				u"待主管确认": 2,
				u"待运维认领": 3,
				u"待运维执行": 4,
				u"已完成": 5,
				}

@worksheet.route('/details/<worksheet_id>')
@login_required
def worksheet_details(worksheet_id):
	user_id = session["user_data"]["user_id"]
	try:
		worksheet = Worksheet.objects.filter(id=worksheet_id)[0]
	except:
		worksheet = None
	if not worksheet:
		return redirect(url_for('user.index'))
	apply_name = worksheet.applier.username if worksheet.applier else ''
	operator_name = worksheet.operator.username if worksheet.operator else ''
	worksheet_data = {"worksheet_id": worksheet.id, "title": worksheet.title, "type_name": worksheet.worksheet_type.name, "planned_at": str(worksheet.planned_at)[:19], "state": worksheet.state, "state_id": statusid_dict.get(worksheet.state) or 0, "apply_name": apply_name, "operator_name": operator_name, "created_at": worksheet.created_at, "content": worksheet.content, "attached_file_path": worksheet.attached_file_path, "is_manager": worksheet.applier.is_manager()}
	try:
		worksheetstates = WorksheetState.objects.filter(worksheet_id=worksheet_id).order_by('-id')
	except:
		worksheetstates = None
	worksheetstate_list = []
	approver = ''
	for data in worksheetstates:
		name = data.creator.username if data.creator else None
		if data.state == WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED and not approver:
			approver = data.waitting_confirmer.username if data.waitting_confirmer else ''
		worksheetstate_list.append({"name": name, "created_at": data.created_at, "state": data.state, "content": data.reject_reason or ''})
	worksheet_data['approver'] = approver
	is_leader = False
	if worksheet.state == WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED:
		leader_id = worksheetstates[0].waitting_confirmer_id
		if leader_id == user_id:
			is_leader = True
	is_operator = False
	if worksheet.state == WS_STATE_WAITTING_OPERATOR_CLAIMED:
		user_data = User.objects.filter(id = user_id)[0]
		is_operator = user_data.is_operator()
	is_operator_execute = False
	if worksheet.state == WS_STATE_WAITTING_OPERATOR_EXECUTED:
		operator_id = worksheet.operator_id
		if operator_id == user_id:
			is_operator_execute = True
	is_revise = False
	if worksheet.state == WS_STATE_HAVE_BACK:
		applier_id = worksheet.applier_id
		if user_id == applier_id:
			is_revise = True
	return render_template("worksheet/details.html", worksheet_data=worksheet_data, worksheetstate_list=worksheetstate_list, is_leader=is_leader, is_operator=is_operator, is_operator_execute=is_operator_execute, is_revise=is_revise)

@worksheet.route('/update/worksheetstate/', methods=['GET', 'POST'])
@login_required
def update_worksheetstate():
	user_id = session["user_data"]["user_id"]
	action_type = request.form.get('action_type')
	reject_reason = request.form.get('reject_reason') or None
	worksheet_id = request.form.get('worksheet_id')
	result = {'status': 1001, 'message': '请求失败'}
	try:
		user_data = User.objects.filter(id=user_id)[0]
	except:
		user_data = None
	try:
		worksheet_data = Worksheet.objects.filter(id=worksheet_id)[0]
	except:
		worksheet_data = None
	ISOTIMEFORMAT='%Y-%m-%d %X'
	now_time = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
	if user_data and worksheet_data:
		if action_type == u"运维认领":
			worksheet_data.operator_id = user_id
			worksheet_data.save()
		if action_type == u"运维执行成功":
			worksheet_data.updated_at = now_time
			worksheet_data.save()
		if state_transfer(user_data, action_type, worksheet_data, reject_reason):
			result = {'status': 200, 'message': '请求成功'}
	return json.dumps(result)

@worksheet.route('/add/add_post/', methods=['GET', 'POST'])
@login_required
def add_post():
	title = request.form.get('title')
	worksheet_type_id = request.form.get('worksheet_type_id')
	finish_at = request.form.get('finish_at')
	content = request.form.get('content')
	user_id = session['user_data'].get('user_id')
	email = session['user_data'].get('email')
	worksheet_id = request.form.get('worksheet_id')
	file = request.files.get('file')
	file_location = None
	if file:
		filename = file.filename
		UPLOAD_FOLDER = upload_path + email.split('@')[0] + '/'
		if not os.path.exists(UPLOAD_FOLDER):
			os.mkdir(UPLOAD_FOLDER)
		file_location = os.path.join(UPLOAD_FOLDER, filename)
		file.save(file_location)
	if worksheet_id:
		try:
			worksheet_data = Worksheet.objects.filter(id=worksheet_id)[0]
		except:
			worksheet_data = None
		if not worksheet_data:
			result = {'status': 1001, 'message': '数据不存在'}
			return json.dumps(result)
		if worksheet_data.applier_id == user_id:
			user_data = User.objects.filter(id=user_id)[0]
			worksheet_data.title = title
			worksheet_data.worksheet_type_id = worksheet_type_id
			worksheet_data.finish_at = finish_at
			if file_location:
				worksheet_data.attached_file_path = file_location
			worksheet_data.content = content
			# worksheet_data.attached_file_path = file_location
			state_transfer(user_data, WS_USER_ACTION_DEVELOPER_RESUBMIT, worksheet_data)
			result = {'status': 200, 'message': '保存成功' , 'data': {'worksheet_id': worksheet_data.id}}
		else:
			result = {'status': 1001, 'message': '没有权限'}
		return json.dumps(result)

	try:
		apply_user = User.objects.filter(id=user_id)[0]
	except:
		apply_user = None
	try:
		if file_location:
			worksheet_data = Worksheet(title=title, applier_id=user_id, content=content, worksheet_type_id=worksheet_type_id, attached_file_path=file_location, planned_at=finish_at)
		else:
			worksheet_data = Worksheet(title=title, applier_id=user_id, content=content, worksheet_type_id=worksheet_type_id, planned_at=finish_at)
		worksheet_data.save()
		if apply_user.organization.leader_id == user_id:
			state_transfer(apply_user, WS_USER_ACTION_TEAM_LEADER_CREATED, worksheet_data)
		else:
			state_transfer(apply_user, WS_USER_ACTION_DEVELOPER_CREATED, worksheet_data)
		if worksheet_data:
			result = {'status': 200, 'message': '保存成功', 'data': {'worksheet_id': worksheet_data.id}}
		else:
			result = {'status': 1001, 'message': '保存失败'}
	except Exception,e:
		print e
		result = {'status': 1001, 'message': '数据库异常'}
	return json.dumps(result)

@worksheet.route('/add/get_template/', methods=['GET', 'POST'])
@login_required
def get_template():
	worksheet_type_id = request.form.get('worksheet_type_id')
	try:
		template = WorksheetType.objects.get(id=worksheet_type_id).template
		# result = {'status': 200, 'message': '数据不存在','worksheet_content': ws_template_dict.get(ws_template_map.get(worksheet_type_id))}
		result = {'status': 200, 'message': '请求成功','worksheet_content': template}
	except:
		result = {'status': 1001, 'message': '数据不存在'}
	return json.dumps(result)