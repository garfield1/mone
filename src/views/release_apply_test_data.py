#!/usr/bin/env python
#encoding=utf-8
from _django_orm import *
import datetime
Application.objects.create(name="shopping cart")
sys_role = Role.objects.create(name="系统管理员")
team_leader_role = Role.objects.create(name="研发主管")
test_leader_role = Role.objects.create(name="测试主管")
tester_role = Role.objects.create(name="测试工程师")
developer_role  = Role.objects.create(name="研发工程师")
manager_role = Role.objects.create(name="研发经理")
operator_role = Role.objects.create(name="运维工程师")
operator_leader_role = Role.objects.create(name="运维主管")
producter_role = Role.objects.create(name="产品经理")

sys = User.objects.create(username="sys",desc="sys")
sys.role_set.add(sys_role)
#sys.role_set.add(manager_role)
#Role.objects.filter(name="研发经理")[0].user.all()[0].username

developer = User.objects.create(username="hf",desc="研发工程师",email="huangfuzepeng@meizu.com")
developer.role_set.add(developer_role)
applier = developer
producter = developer
producter.role_set.add(producter_role)

tester = User.objects.create(username="cg",desc="测试工程师",email="chengeng@meizu.com")
tester.role_set.add(tester_role)
team_leader = User.objects.create(username="ft",desc="研发主管",email="xufengtian@meizu.com")
team_leader.role_set.add(team_leader_role)
manager = User.objects.create(username="maolingzhi",desc="研发经理",email="maolingzhi@meizu.com")
manager.role_set.add(manager_role)
operator = User.objects.create(username="xh",desc="运维工程师",email="jiaxiaohui@meizu.com")
operator.role_set.add(operator_role)
ra = ReleaseApply(title="shopping cart",tester = tester ,applier = applier ,producter = producter, application = Application.objects.first(),planned_at=datetime.datetime.now())      
ra.save()
wt = WorksheetType.objects.create(name="1111")   
w = Worksheet.objects.create(title="ws",applier= developer,planned_at = datetime.datetime.now(),worksheet_type = wt)

dev_leader1 = User.objects.create(username="lw",desc="研发主管",email="xufengtian@meizu.com")
dev_leader2 = User.objects.create(username="xp",desc="研发主管",email="xufengtian@meizu.com")
dev_leader3 = User.objects.create(username="zc",desc="研发主管",email="xufengtian@meizu.com")
dev_leader4 = User.objects.create(username="zq",desc="研发主管",email="xufengtian@meizu.com")
dev_leader5 = User.objects.create(username="jt",desc="前端主管",email="xufengtian@meizu.com")
tester_leader = User.objects.create(username="qt",desc="测试主管",email="qutao@meizu.com")
operator_leader =User.objects.create(username="wb",desc="运维主管",email="wenbin@meizu.com")





org0 = Organization.objects.create(name = "系统开发组",leader = manager)
org1 = Organization.objects.create(name = "平台架构&基础运维",leader = dev_leader4)
operator_org =Organization.objects.create(name = "基础运维",leader = operator_leader)
operator_org.user_set.add(operator)
operator_org.user_set.add(operator_leader)
org3 = Organization.objects.create(name = "平台架构",leader = dev_leader4)
org1.children.add(operator_org)
org1.children.add(org3)
org4 = Organization.objects.create(name = "交易前台",leader = dev_leader3)
org5 = Organization.objects.create(name = "交易后台",leader = team_leader)
org5.user_set.add(team_leader)
org5.user_set.add(developer)
org6 = Organization.objects.create(name = "前端",leader = dev_leader5)
test_org = Organization.objects.create(name = "测试",leader = tester_leader)
test_org.user_set.add(tester)
#print tester.organization.name,"hhzhzhzhhzh"
test_org.user_set.add(tester_leader)
#for user in test_org.user_set.all():
#	print user.username,user.email

org8 = Organization.objects.create(name = "数据分析",leader = dev_leader1)
org0.children.add(org1)
org0.children.add(org4)
org0.children.add(org5)
org0.children.add(org6)
org0.children.add(test_org)
org0.children.add(org8)

print developer.organization.user_set.all()

#print User.objects.filter(username="ft")
#print Organization.objects.filter(name="基础运维")
