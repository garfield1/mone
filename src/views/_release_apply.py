#!/usr/bin/env python
#encoding=utf-8
RA_USER_ACTION_RA_CREATED = "上线申请单创建"
RA_USER_ACTION_TEAM_LEADER_CONFIRMED = "主管确认"
RA_USER_ACTION_MANAGER_CONFIRMED = "经理确认"
RA_USER_ACTION_BUILD_CONFIRMED = "构建确认"
RA_USER_ACTION_TEST_SUCCESS_CONFIRMED = "测试通过确认"
RA_USER_ACTION_RELEASE_SUCCESS_CONFIRMED = "发布成功确认"

RA_STATE_TEAM_LEADER_WAITTING_CONFIRMED = "主管待确认"
RA_STATE_MANAGER_WAITTING_CONFIRMED = "经理待确认"
RA_STATE_BUILD_WAITTING_CONFIRMED = "构建待确认"
RA_STATE_TEST_WAITTING_CONFIRMED = "测试待确认"
RA_STATE_RELEASE_WAITTING_CONFIRMED = "发布待确认"

def find_manager(team_leader):
	manager_role = Role.objects.filter(name="研发经理")[0]
	while (team_leader.organization.parent <> None):
		if len(team_leader.organization.parent.leader.role_set.all() & manager_role) > 0:
			return team_leader.organization.parent.leader
		else:
			return find_manager(team_leader.organization.parent.leader)
	else:
		return None 

def send_email(email,ra,state):
	eq = EmailQueue()
	eq.email = email
	eq.title = ra.title + state
	eq.content = "http://localhost/release_apply/"+str(ra.id)
	eq.save()
	

def state_transfer(user,action,ra):
	"""
	根据用户定位角色
	根据role + action 定位当前状态及要流转的状态,并异步发出通知
	开发or研发主管发起上线申请，经主管和经理审批再进行构建提测到发布
	"""
	sys = User.objects.get(username="sys")
	manager = Role.objects.filter(name="研发经理")[0].user.all()[0]
	operator = Role.objects.filter(name="运维工程师")[0].user.all()[0]
	user_roles = user.role_set.all()
	rsa = ReleaseApplyState(creator = user, release_apply = ra, state = action)
	rsa.save()
	if action == RA_USER_ACTION_RA_CREATED:
		team_leader_role = Role.objects.get(name="研发主管")
		developer_role = Role.objects.get(name="研发工程师")
		if team_leader_role in user_roles:
			#主管提交上线申请走经理审批流程
			rsa = ReleaseApplyState(creator = sys, waitting_confirmer = manager ,release_apply = ra, state = RA_STATE_MANAGER_WAITTING_CONFIRMED)
			rsa.save()
			send_email(manager.email,ra,"需要您审批")
			return user.id
		elif developer_role in user_roles:
			#开发提交上线申请走主管审批流程
			rsa = ReleaseApplyState(creator = sys, waitting_confirmer = user.organization.leader ,release_apply = ra, state = RA_STATE_TEAM_LEADER_WAITTING_CONFIRMED)
			rsa.save()
			send_email(user.organization.leader.email,ra,"需要您审批")
			return user.id
		else:
			print "非合适角色，只有开发和主管可以提交上线申请"

	if action == RA_USER_ACTION_TEAM_LEADER_CONFIRMED:
		rsa = ReleaseApplyState(creator = sys, waitting_confirmer = manager ,release_apply = ra, state = RA_STATE_MANAGER_WAITTING_CONFIRMED)
		rsa.save()
		send_email(manager.email,ra,"需要您审批")
		return user.id

	if action == RA_USER_ACTION_MANAGER_CONFIRMED:
		rsa = ReleaseApplyState(creator = sys, waitting_confirmer = ra.applier ,release_apply = ra, state = RA_STATE_BUILD_WAITTING_CONFIRMED)
		rsa.save()
		send_email(user.email,ra,"可以构建了")
		return user.id
	
	if action == RA_USER_ACTION_BUILD_CONFIRMED:
		rsa = ReleaseApplyState(creator = sys, waitting_confirmer = ra.tester ,release_apply = ra, state = RA_STATE_TEST_WAITTING_CONFIRMED)
		rsa.save()
		#发测试全组
		for tester in ra.tester.organization.user_set.all():
			send_email(tester.email,ra,"需要测试组测试")
		return user.id

	if action == RA_USER_ACTION_TEST_SUCCESS_CONFIRMED:
		rsa = ReleaseApplyState(creator = sys, waitting_confirmer = operator ,release_apply = ra, state = RA_STATE_RELEASE_WAITTING_CONFIRMED)
		rsa.save()
		#发运维全组
		for operator in operator.organization.user_set.all():
			send_email(operator.email,ra,"需要运维组发布")
		return user.id

	if action == RA_USER_ACTION_RELEASE_SUCCESS_CONFIRMED:
		send_email("ecomdev@meizu.com",ra,"发布成功")
		return user.id

	return user.id
	

if __name__ == "__main__":
	from _django_orm import *
	import datetime
	from release_apply_test_data import *
	print "developer id",state_transfer(developer,RA_USER_ACTION_RA_CREATED,ra)
	team_leader = developer.organization.leader
	print "team_leader id",state_transfer(team_leader,RA_USER_ACTION_TEAM_LEADER_CONFIRMED,ra)
	#print team_leader.organization.name,"tl org"
	#获取直线经理
	print "manager id",state_transfer(manager,RA_USER_ACTION_MANAGER_CONFIRMED,ra)
	print "developer id",state_transfer(developer,RA_USER_ACTION_BUILD_CONFIRMED,ra)
	print "tester id",state_transfer(tester,RA_USER_ACTION_TEST_SUCCESS_CONFIRMED,ra)
	print "operator id",state_transfer(operator,RA_USER_ACTION_RELEASE_SUCCESS_CONFIRMED,ra)
