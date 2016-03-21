#!/usr/bin/env python
#encoding=utf-8

#全局变量在models.py中
from models.mone.models import EmailQueue, WS_USER_ACTION_TEAM_LEADER_CREATED, WS_USER_ACTION_TEAM_LEADER_RESUBMIT, \
	WorksheetState, WS_STATE_WAITTING_OPERATOR_CLAIMED, WS_USER_ACTION_DEVELOPER_CREATED, \
	WS_USER_ACTION_DEVELOPER_RESUBMIT, WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED, WS_USER_ACTION_TEAM_LEADER_CONFIRMED, \
	WS_USER_ACTION_TEAM_LEADER_REJECTED, WS_USER_ACTION_OPERATOR_REJECTED, WS_STATE_WAITTING_DEVELOPER_MODIFIED, \
	WS_STATE_WAITTING_TEAM_LEADER_MODIFIED, WS_USER_ACTION_OPERATOR_CLAIMED, WS_STATE_WAITTING_OPERATOR_EXECUTED, \
	WS_USER_ACTION_OPERATOR_EXECUTED, WS_STATE_WAITTING_DEVELOPER_CLOSED, WS_STATE_WAITTING_TEAM_LEADER_CLOSED, \
	WS_USER_ACTION_TEAM_LEADER_CLOSED, WS_USER_ACTION_DEVELOPER_CLOSED, WS_STATE_CLOSED


def _send_email(email,w,state):
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
	#开发action3个 主管action5个 运维action3个
	if action == WS_USER_ACTION_TEAM_LEADER_CREATED or action == WS_USER_ACTION_TEAM_LEADER_RESUBMIT:
		#主管提交上线申请直拉到运维待认领 or 运维打回
		ws = WorksheetState.objects.create(creator = user, waitting_confirmer = w.operator ,worksheet = w, state = WS_STATE_WAITTING_OPERATOR_CLAIMED , action = action)
		#发运维全组
		for operator in w.operator.organization.user_set.all():
			_send_email(operator.email,w,w.title+"需要运维组认领")
		return user.id

	if action == WS_USER_ACTION_DEVELOPER_CREATED or action == WS_USER_ACTION_DEVELOPER_RESUBMIT:
		#开发,pd等基础岗位提交上线申请走主管审批流程
		WorksheetState.objects.create(creator = user, waitting_confirmer = user.organization.leader ,worksheet = w, state = WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED , action = action)
		_send_email(user.organization.leader.email,w,w.title+"需要您审批")
		return user.id

	if action == WS_USER_ACTION_TEAM_LEADER_CONFIRMED:
		WorksheetState.objects.create(creator = user , worksheet = w, state = WS_STATE_WAITTING_OPERATOR_CLAIMED , action = action)
		#发运维全组
		for operator in w.operator.organization.user_set.all():
			_send_email(operator.email,w,"需要运维组认领")
		return user.id

	if action == WS_USER_ACTION_TEAM_LEADER_REJECTED or action == WS_USER_ACTION_OPERATOR_REJECTED:
		state = WS_STATE_WAITTING_DEVELOPER_MODIFIED
		if w.applier.is_team_leader():
			state = WS_STATE_WAITTING_TEAM_LEADER_MODIFIED
		WorksheetState.objects.create(creator = user, waitting_confirmer = w.applier ,worksheet = w, state = state , reject_reason = reject_reason, action = action)
		_send_email(w.applier.email,w,user.username+"拨回了你的"+w.title+"工单")
		_send_email(user.email,w,"您拨回了"+w.applier.username+"的"+w.title+"工单")
		return user.id
			
	if action == WS_USER_ACTION_OPERATOR_CLAIMED:
		WorksheetState.objects.create(creator = user, waitting_confirmer = w.operator ,worksheet = w, state = WS_STATE_WAITTING_OPERATOR_EXECUTED , action = action)
		#发运维全组
		for operator in w.operator.organization.user_set.all():
			_send_email(w.operator.email,w,"被运维组"+user.username+"认领")
		#发工单发起人
		_send_email(w.applier.email,w,"被运维组"+user.username+"认领")
		return user.id

	if action == WS_USER_ACTION_OPERATOR_EXECUTED:
		_state = WS_STATE_WAITTING_DEVELOPER_CLOSED
		if w.applier.is_team_leader():
			_state = WS_STATE_WAITTING_TEAM_LEADER_CLOSED
		WorksheetState.objects.create(creator = user, waitting_confirmer = w.applier, worksheet = w, state = _state , action = action)
		_send_email(w.applier,w,"您的"+w.title+"工单需要您关闭")
		_send_email("ecomdev@meizu.com",w,"发布成功")
		return user.id

	if action == WS_USER_ACTION_TEAM_LEADER_CLOSED or action == WS_USER_ACTION_DEVELOPER_CLOSED:
		WorksheetState.objects.create(creator = user, worksheet = w, state = WS_STATE_CLOSED , action = action)
		_send_email(user.email,w,"工单: {0}, 已关闭成功".format(w.title))
		_send_email(w.operator.email,w,"工单: {0}, 已关闭成功".format(w.title))
		return user.id

	return user.id

if __name__ == "__main__":
	from release_apply_test_data import *
	#开发action3个 主管action5个 运维action3个
	print "developer id",state_transfer(developer,WS_USER_ACTION_DEVELOPER_CREATED,w)
	print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_REJECTED,w)
	print "developer id",state_transfer(developer,WS_USER_ACTION_DEVELOPER_RESUBMIT,w)
	print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_CONFIRMED,w)
	print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_CLAIMED,w)
	print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_EXECUTED,w)
	print "developer id",state_transfer(developer,WS_USER_ACTION_DEVELOPER_CLOSED,w)
	exit(0)
	#print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_CREATED,w)
	#print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_REJECTED,w,reject_reason = "reason")
	#print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_RESUBMIT,w,reject_reason = "reason")
	#print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_CLAIMED,w)
	#print "operator id",state_transfer(operator,WS_USER_ACTION_OPERATOR_EXECUTED,w)
	#print "team_leader id",state_transfer(team_leader,WS_USER_ACTION_TEAM_LEADER_CLOSED,w)

	print "applier id",applier.created_worksheets_by_pagination(1)
	todo,cnt  = team_leader.waitting_confirmed_worksheets_by_pagination(1)
	print "team_leader",todo,cnt
	if cnt > 0:
		print todo[0].state
	done,cnt = team_leader.operated_worksheets_by_pagination(1)
	print "team_leader",done,cnt
	if cnt > 0:
		print done[0].state,done[0].action
