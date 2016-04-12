#!/usr/bin/env python
#encoding=utf-8
# from _django_orm import *
from models.mone.models import EmailQueue, RA_USER_ACTION_TEAM_LEADER_CREATED, RA_USER_ACTION_TEAM_LEADER_RESUBMIT, \
	RA_USER_ACTION_TEAM_LEADER_CONFIRMED, ReleaseApplyState, RA_STATE_WAITTING_MANAGER_CONFIRMED, \
	RA_USER_ACTION_DEVELOPER_CREATED, RA_USER_ACTION_DEVELOPER_RESUBMIT, RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED, \
	RA_USER_ACTION_MANAGER_CONFIRMED, RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED, \
	RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED, RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED, \
	RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED, RA_STATE_WAITTING_TESTER_CONFIRMED, RA_USER_ACTION_TESTER_CONFIRMED, \
	RA_STATE_WAITTING_OPERATOR_CLAIMED, Organization, RA_USER_ACTION_TESTER_REJECT, RA_USER_ACTION_TEAM_LEADER_REJECTED, \
	RA_USER_ACTION_OPERATOR_REJECTED, RA_USER_ACTION_MANAGER_REJECTED, RA_STATE_WAITTING_DEVELOPER_MODIFIED, \
	RA_STATE_WAITTING_TEAM_LEADER_MODIFIED, RA_USER_ACTION_OPERATOR_CLAIMED, RA_STATE_WAITTING_OPERATOR_EXECUTED, \
	RA_USER_ACTION_OPERATOR_EXECUTED, RA_STATE_WAITTING_DEVELOPER_CLOSED, RA_STATE_WAITTING_TEAM_LEADER_CLOSED, \
	RA_USER_ACTION_DEVELOPER_CLOSED, RA_USER_ACTION_TEAM_LEADER_CLOSED, RA_STATE_CLOSED, Role, \
	RA_STATE_WAITTING_COMPLETE


def _send_email(email,ra,state):
	eq = EmailQueue()
	eq.email = email
	eq.title = ra.title or '' + state
	eq.content = "http://localhost/release_apply/"+str(ra.id)
	eq.save()

def get_all_operator():
	all_user_list = []
	roles = Role.objects.filter(name__contains="运维")
	for role in roles:
		user_list = role.user.all()
		all_user_list.extend(user_list)
	return list(set(all_user_list))

def state_transfer(user,action,ra,reject_reason = None):
	"""
	根据用户定位角色
	根据role + action 定位当前状态及要流转的状态,并异步发出通知
	开发or研发主管发起上线申请，经主管和经理审批再进行构建提测到发布
	"""
	if action == RA_USER_ACTION_TEAM_LEADER_CREATED or action == RA_USER_ACTION_TEAM_LEADER_RESUBMIT or action == RA_USER_ACTION_TEAM_LEADER_CONFIRMED:
		ret = user.role_set.all() & Role.objects.filter(name__contains=u"架构师").all()
		if len(ret) > 0:
			manager = user
		else:
			manager = user.organization.parent.leader if user.organization.parent else user
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = manager ,release_apply = ra, state = RA_STATE_WAITTING_MANAGER_CONFIRMED , action = action)
		_send_email(manager.email,ra,"需要您审批")
		return user.id

	if action == RA_USER_ACTION_DEVELOPER_CREATED or action == RA_USER_ACTION_DEVELOPER_RESUBMIT:
		team_leader = user.organization.leader
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = team_leader ,release_apply = ra, state = RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED , action = action)
		_send_email(team_leader.email,ra,"需要您审批")
		return user.id

	if action == RA_USER_ACTION_MANAGER_CONFIRMED:
		_state = RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED
		if ra.applier.is_team_leader():
			state = RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = ra.applier ,release_apply = ra, state = _state , action = action)
		_send_email(ra.applier.email,ra,"可以构建了")
		return user.id

	if action == RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED or action == RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED:
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = ra.tester ,release_apply = ra, state = RA_STATE_WAITTING_TESTER_CONFIRMED , action = action)
		#发测试全组
		for tester in ra.tester.organization.user_set.all():
			_send_email(tester.email,ra,"需要测试组测试")
		return user.id

	if action == RA_USER_ACTION_TESTER_CONFIRMED:
		ReleaseApplyState.objects.create(creator = user ,release_apply = ra, state = RA_STATE_WAITTING_OPERATOR_CLAIMED , action = action)
		#发运维全组
		for operator in get_all_operator():
			_send_email(operator.email,ra,"需要运维组发布")
		return user.id

	if action == RA_USER_ACTION_TESTER_REJECT or \
	   action == RA_USER_ACTION_TEAM_LEADER_REJECTED or \
	   action == RA_USER_ACTION_OPERATOR_REJECTED or \
	   action == RA_USER_ACTION_MANAGER_REJECTED:
		_state = RA_STATE_WAITTING_DEVELOPER_MODIFIED
		if ra.applier.organization.leader == ra.applier:
			state = RA_STATE_WAITTING_TEAM_LEADER_MODIFIED
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = ra.applier ,release_apply = ra, state = _state, reject_reason = reject_reason, action = action)
		_send_email(ra.applier.email,ra,user.username+"拨回了您的上线申请")
		return user.id

	if action == RA_USER_ACTION_OPERATOR_CLAIMED:
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = user ,release_apply = ra, state = RA_STATE_WAITTING_OPERATOR_EXECUTED , action = action)
		ra.operator = user
		ra.save()
		_send_email(ra.applier.email,ra,user.username+"认领了该上线申请")
		#发运维全组
		for operator in get_all_operator():
			_send_email(operator.email,ra,user.username+"认领了"+ra.title+"上线申请")
		_send_email(ra.applier.email,ra,user.username+"认领了您的"+ra.title+"上线申请")
		return user.id

	if action == RA_USER_ACTION_OPERATOR_EXECUTED:
		_state = RA_STATE_WAITTING_COMPLETE
		if ra.applier.is_team_leader():
			_state = RA_STATE_WAITTING_COMPLETE
		ReleaseApplyState.objects.create(creator = user, waitting_confirmer = ra.applier ,release_apply = ra, state = _state , action = action)
		_send_email("ecomdev@meizu.com",ra,"发布成功")
		_send_email(ra.applier.email,ra,ra.title+"发布完成，请关闭上线申请单")
		return user.id

	if action == RA_USER_ACTION_DEVELOPER_CLOSED or action == RA_USER_ACTION_TEAM_LEADER_CLOSED:
		ReleaseApplyState.objects.create(creator = user, release_apply = ra, state = RA_STATE_CLOSED , action = action)
		_send_email(ra.applier.email,ra,ra.title+"上线申请单关闭")
		_send_email(ra.operator.email,ra,"您执行的"+ra.title+"上线申请单已关闭")
		return user.id

	return user.id

if __name__ == "__main__":
	from _django_orm import *
	import datetime
	from release_apply_test_data import *
	team_leader = developer.organization.leader
	#主管action6个，开发action4个,经理action2个，测试action2个，运维action3个
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_CREATED,ra)
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_REJECTED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_RESUBMIT,ra)
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CONFIRMED,ra)
	print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_CONFIRMED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED,ra)
	print "tester id",state_transfer(tester,RA_USER_ACTION_TESTER_REJECT,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_RESUBMIT,ra)
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CONFIRMED,ra)
	print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_CONFIRMED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED,ra)
	print "tester id",state_transfer(tester,RA_USER_ACTION_TESTER_CONFIRMED,ra)
	print "operator id",state_transfer(operator,RA_USER_ACTION_OPERATOR_REJECTED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_RESUBMIT,ra)
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CONFIRMED,ra)
	print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_CONFIRMED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED,ra)
	print "tester id",state_transfer(tester,RA_USER_ACTION_TESTER_CONFIRMED,ra)
	print "operator id",state_transfer(operator,RA_USER_ACTION_OPERATOR_CLAIMED,ra)
	print "operator id",state_transfer(operator,RA_USER_ACTION_OPERATOR_EXECUTED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_DEVELOPER_CLOSED,ra)



	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CREATED,ra)
	print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_REJECTED,ra)
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_RESUBMIT,ra)
	#print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_CONFIRMED,ra)
	#print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED,ra)
	#print "tester id",state_transfer(tester,RA_USER_ACTION_TESTER_CONFIRMED,ra)
	#print "operator id",state_transfer(operator,RA_USER_ACTION_OPERATOR_CLAIMED,ra)
	#print "operator id",state_transfer(operator,RA_USER_ACTION_OPERATOR_EXECUTED,ra)
	#print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CLOSED,ra)

	print "applier id",applier.created_release_applys_by_pagination(1)
	print "applier id",applier.waitting_confirmed_release_applys_by_pagination(1)
	done,cnt = manager.operated_release_applys_by_pagination(1)
	print "manager id",done,cnt,done[0].state,done[0].action

