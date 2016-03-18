#!/usr/bin/env python
#encoding=utf-8
from _django_orm import *
Application.objects.create(name="shopping cart")
role1 = Role.objects.create(name="系统管理员")
team_leader_role = Role.objects.create(name="研发主管")
role3 = Role.objects.create(name="测试主管")
developer_role  = Role.objects.create(name="研发工程师")
manager_role = Role.objects.create(name="研发经理")

user1 = User.objects.create(username="sys",desc="sys")
user2 = User.objects.create(username="hf",desc="研发工程师",email="huangfuzepeng@meizu.com")
print user2.id,"user2.id <="
user2.role_set.add(developer_role)


user3 = User.objects.create(username="lw",desc="研发主管",email="xufengtian@meizu.com")
user4 = User.objects.create(username="xp",desc="研发主管",email="xufengtian@meizu.com")
user5 = User.objects.create(username="zc",desc="研发主管",email="xufengtian@meizu.com")
user6 = User.objects.create(username="zq",desc="研发主管",email="xufengtian@meizu.com")
user7 = User.objects.create(username="qt",desc="研发主管",email="xufengtian@meizu.com")
user8 = User.objects.create(username="jt",desc="研发主管",email="xufengtian@meizu.com")
user9 = User.objects.create(username="ft",desc="研发主管",email="xufengtian@meizu.com")
user9.role_set.add(team_leader_role)
user10 = User.objects.create(username="maolingzhi",desc="研发经理",email="maolingzhi@meizu.com")
user10.role_set.add(manager_role)
user11 = User.objects.create(username="liwei",desc="研发主管",email="liwei2@meizu.com")

ra = ReleaseApply(title="shopping cart",tester = user1,applier = user2,producter = user1,application = Application.objects.first(),planned_at=datetime.datetime.now())      
ra.save()        
state_transfer(u2,RA_USER_ACTION_RA_CREATED,ra)




org0 = Organization.objects.create(name = "系统开发组",leader = user4)
org1 = Organization.objects.create(name = "平台架构&基础运维",leader = user5)
org2 =Organization.objects.create(name = "基础运维",leader = user4)
org3 = Organization.objects.create(name = "平台架构",leader = user4)
org1.children.add(org2)
org1.children.add(org3)
org4 = Organization.objects.create(name = "交易前台",leader = user10)
org5 = Organization.objects.create(name = "交易后台",leader = user9)
org6 = Organization.objects.create(name = "前端",leader = user8)
org7 = Organization.objects.create(name = "测试",leader = user7)
org8 = Organization.objects.create(name = "数据分析",leader = user6)
org0.children.add(org1)
org0.children.add(org4)
org0.children.add(org5)
org0.children.add(org6)
org0.children.add(org7)
org0.children.add(org8)

user2.organization = org5
user9.organization = org5
user2.save()
user9.save()


print User.objects.filter(username="ft")
