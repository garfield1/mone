#!/usr/bin/env python
#encoding=utf-8
#action代表瞬时的动作
from django.core.paginator import Paginator
from _django_orm import *

WS_USER_ACTION_WS_CREATED = u"工单创建"
WS_USER_ACTION_WS_RESUBMIT = u"工单重提交"
WS_USER_ACTION_TEAM_LEADER_CONFIRMED = u"主管确认"
WS_USER_ACTION_TEAM_LEADER_REJECTED = u"主管打回"
WS_USER_ACTION_OPENATOR_REJECTED = u"运维打回"
WS_USER_ACTION_OPENATOR_CLAIMED = u"运维认领"
WS_USER_ACTION_OPERATOR_EXECUTED = u"运维执行成功"
WS_USER_ACTION_WS_CLOSED = u"关闭工单"# 已关闭
#state代表一种持续的中间状态
WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED = u"主管待确认"   #待审核
WS_STATE_DEVELOPER_WAITTING_MODIFIED= u"开发待修改" #已打回
WS_STATE_TEAM_LEADER_WAITTING_MODIFIED = u"主管待修改" #已打回
WS_STATE_OPERATOR_WAITTING_CLAIMED = u"运维待认领" #待认领
WS_STATE_OPERATOR_WAITTING_EXECUTED = u"运维待执行"#待执行
WS_STATE_OPERATOR_FINISHED = u"运维执行完成关闭"#已完成
WS_STATE_TEAM_LEADER_CLOSED = u"主管关闭工单"
WS_STATE_DEVELOPER_CLOSED = u"开发关闭工单"

scores ={
	WS_USER_ACTION_WS_CREATED:1,
	WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED:20,
	WS_USER_ACTION_TEAM_LEADER_REJECTED:21,
	WS_STATE_DEVELOPER_WAITTING_MODIFIED:2,
	WS_USER_ACTION_WS_RESUBMIT:3,
	WS_USER_ACTION_TEAM_LEADER_CONFIRMED:23,
	WS_STATE_OPERATOR_WAITTING_CLAIMED:1000,
	WS_STATE_TEAM_LEADER_WAITTING_MODIFIED:200,
	WS_USER_ACTION_OPENATOR_REJECTED:2001,
	WS_USER_ACTION_OPENATOR_CLAIMED:2003,
	WS_STATE_OPERATOR_WAITTING_EXECUTED:4000,
	WS_USER_ACTION_OPERATOR_EXECUTED:5001,
	WS_STATE_OPERATOR_FINISHED:6000,
	WS_USER_ACTION_WS_CLOSED:5,
	WS_STATE_TEAM_LEADER_CLOSED:300,
	WS_STATE_DEVELOPER_CLOSED:4
	}


def send_email(email,w,state):
	eq = EmailQueue()
	eq.email = email
	eq.title = w.title + state
	eq.content = "http://localhost/worksheet/"+str(w.id)
	eq.save()

def state_transfer(user,action,w,reject_reason=None):
	"""
	根据用户定位角色
	根据role + action 定位当前状态及要流转的状态,并异步发出通知
	开发or研发主管发起上线申请，经主管和经理审批再进行构建提测到发布
	"""
	sys = User.objects.get(username="sys")
	operator = Role.objects.filter(Q(name=u"运维工程师")|Q(name=u"运维主管"))[0].user.all()[0]
	user_roles = user.role_set.all()
	leader_roles = Role.objects.filter(Q(name__endswith=u'主管')|Q(name__endswith=u'研发经理'))
	#存储action瞬时状态
	ws = WorksheetState(creator = user, worksheet = w, state = action)
	ws.save()
	#基础角色需要其直属主管确认
	if action == WS_USER_ACTION_WS_CREATED or action == WS_USER_ACTION_WS_RESUBMIT:
		if len(leader_roles & user_roles) > 0:
			#主管提交上线申请直拉到运维待认领 or 运维打回
			ws = WorksheetState(creator = sys, waitting_confirmer = operator ,worksheet = w, state = WS_STATE_OPERATOR_WAITTING_CLAIMED)
			ws.save()
			#发运维全组
			for operator in operator.organization.user_set.all():
				send_email(operator.email,w,w.title+"需要运维组认领")
			return user.id
		else:
			#开发,pd等基础岗位提交上线申请走主管审批流程
			ws = WorksheetState(creator = sys, waitting_confirmer = user.organization.leader ,worksheet = w, state = WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED)
			ws.save()
			send_email(user.organization.leader.email,w,w.title+"需要您审批")
			return user.id

	if action == WS_USER_ACTION_TEAM_LEADER_CONFIRMED:
		ws = WorksheetState(creator = sys, waitting_confirmer = operator ,worksheet = w, state = WS_STATE_OPERATOR_WAITTING_CLAIMED)
		ws.save()
		#发运维全组
		for operator in operator.organization.user_set.all():
			send_email(operator.email,w,"需要运维组认领")
		return user.id

	if action == WS_USER_ACTION_TEAM_LEADER_REJECTED:
		ws = WorksheetState(creator = sys, waitting_confirmer = user ,worksheet = w, state = WS_STATE_DEVELOPER_WAITTING_MODIFIED , reject_reason = reject_reason)
		ws.save()
		send_email(w.applier.email,w,"您的主管拨回了你的"+w.title+"工单")
		send_email(user.email,w,"您拨回了"+w.applier.username+"的"+w.title+"工单")
		
			
	if action == WS_USER_ACTION_OPENATOR_CLAIMED:
		ws = WorksheetState(creator = sys, waitting_confirmer = operator ,worksheet = w, state = WS_STATE_OPERATOR_WAITTING_EXECUTED)
		ws.save()
		#发运维全组
		for operator in operator.organization.user_set.all():
			send_email(operator.email,w,"被运维组"+user.username+"认领")
		#发工单发起人
		send_email(w.applier.email,w,"被运维组"+user.username+"认领")
		return user.id

	if action == WS_USER_ACTION_OPENATOR_REJECTED:
		ws = WorksheetState(creator = sys, waitting_confirmer = user ,worksheet = w, state = WS_STATE_DEVELOPER_WAITTING_MODIFIED , reject_reason = reject_reason)
		ws.save()
		send_email(w.applier.email,w,"运维拨回了你的"+w.title+"工单")
		send_email(user.email,w,"您拨回了"+w.applier.username+"的"+w.title+"工单")
		
	if action == WS_USER_ACTION_OPERATOR_EXECUTED:
		ws = WorksheetState(creator = sys, waitting_confirmer = w.applier, worksheet = w, state = WS_STATE_OPERATOR_FINISHED)
		ws.save()
		send_email("ecomdev@meizu.com",w,"发布成功")
		return user.id

	if action == WS_USER_ACTION_WS_CLOSED:
		if len(leader_roles & user_roles) > 0:
			ws = WorksheetState(creator = sys, worksheet = w, state = WS_STATE_TEAM_LEADER_CLOSED)
			ws.save()
		else:
			ws = WorksheetState(creator = sys, worksheet = w, state = WS_STATE_DEVELOPER_CLOSED)
			ws.save()
		send_email(user.email,w,"工单: {0}, 已关闭成功".format(w.title))
		return user.id

	return user.id

def get_worksheets_by_state(user_id,state,current_page,pagesize = 1):
	ret = []
	if state == WS_USER_ACTION_WS_CREATED:
		ret = Worksheet.objects.filter(applier_id = user_id).order_by("-created_at")
	
	if state == WS_USER_ACTION_TEAM_LEADER_CONFIRMED:
		wss = WorksheetState.objects.filter(Q(creator_id = user_id) & Q(state = state))#.order_by("created_at")
		worksheets = set([ws.worksheet for ws in wss])
		#查找工单是否最新的状态是否比WS_USER_ACTION_TEAM_LEADER_CONFIRMED的分值要低，如果低说明有拨回,则排除此条内容
		ret = []
		for worksheet in worksheets:
			ws = WorksheetState.objects.filter(worksheet_id = worksheet.id).order_by("-created_at").first()
			if scores[ws.state] > scores[state]:
				ret.append(worksheet)
	
	if state == WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED:
		wss = WorksheetState.objects.filter(Q(waitting_confirmer_id = user_id) & Q(state = state))#.order_by("created_at")
		worksheets = set([ws.worksheet for ws in wss])
		#查找工单是否最新的状态是否比WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED的分值要低，如果低说明有拨回,则排除此条内容
		ret = []
		for worksheet in worksheets:
			ws = WorksheetState.objects.filter(worksheet_id = worksheet.id).order_by("-created_at").first()
			if scores[ws.state] >= scores[state]:
				ret.append(worksheet)
	p = Paginator(ret,pagesize)
	return p.page(current_page).object_list, len(ret)


if __name__ == "__main__":
	from release_apply_test_data import *
	#工单创建 待审核
	print "developer id",state_transfer(developer,WS_USER_ACTION_WS_CREATED,w)
	team_leader = developer.organization.leader
	#主管打回  已打回
	print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_REJECTED,w,reject_reason = "reason")
	#工单重提交 待审核
	print "developer id",state_transfer(developer,WS_USER_ACTION_WS_RESUBMIT,w)
	#主管确认 待认领
	print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_CONFIRMED,w)
	#运维打回 已打回
	print "operator id",state_transfer(operator,WS_USER_ACTION_OPENATOR_REJECTED,w,reject_reason = "reason")
	#运维认领 待执行
	print "operator id",state_transfer(operator,WS_USER_ACTION_OPENATOR_CLAIMED,w)
	#运维执行成功 已完成
	print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_EXECUTED,w)
	#开发关闭
	print "developer id",state_transfer(developer,WS_USER_ACTION_WS_CLOSED,w)
	print get_worksheets_by_state(2,WS_USER_ACTION_WS_CREATED,1)
	print get_worksheets_by_state(team_leader.id,WS_STATE_TEAM_LEADER_WAITTING_CONFIRMED,1)
