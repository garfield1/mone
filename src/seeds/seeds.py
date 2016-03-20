#!/usr/bin/env python
#encoding=utf-8
from _django_orm import *

u = User(username="11")
u.save()

r1 = Role(name="运维工程师")
r1.save()

r2 = Role(name="研发主管")
r2.save()

r2.user.add(u)
#逆向
print u.role_set.all()[0].name
#正向
print Role.objects.filter(name="研发主管")[0].user.all()
org = Organization(name="系统研发组")
org.save()

org2 = Organization(name="平台架构和基础运维")
#org2.save()
#org2.save()
org.children.add(org2)
org.save()
u.organization = org
u.save()
print u.organization.name

print org.user_set.all()[0].organization.name
lt = LogType(name="ReleaseApp")
lt.save()


log = Log(message="aaaa",ip="192.168.1.1",user = u)
log.log_type = lt
log.save()
log = Log(message="aaaa",ip="192.168.1.1",user = u)
log.save()
print u.log_set.all()

wt = WorksheetType(name="白名单添加")
wt.save()
w = Worksheet(title="购物车项目",worksheet_type = wt,applier = u)
w.save()
print "="*10
print w.applier.username
print w.applier.worksheet_set.all()

rt = ResourceType(name="slb")
rt.save()

rt = ResourceType(name="主机")
rt.save()
print "-"*10
rt2 = ResourceType(name="主机")
rt2.save()

r1 = Resource(lan_ip="192.168.2.1",resource_type = rt)
r1.save()
#!注意 这里rt2不能是rt,否则会触发unique的问题，初断为django机制问题
r2 = Resource(lan_ip="192.168.2.2",resource_type = rt2)
r2.save()
print "="*10
print r1.resource_type.name
app = Application(name="shopping cart")
app.save()
app = Application(name="shopping cart2")
app.save()
app.resources.add(r1)
app.resources.add(r2)
app.save()
for res in  app.resources.all():
	print res.lan_ip

r1 = Resource.objects.get(id=1)
print r1.application_set.all()[0].name

rast = ReleaseApplyStateType(name="工单创建")
rast.save()

rast2 = ReleaseApplyStateType(name="主管待审核")
rast2.save()

rast3 = ReleaseApplyStateType(name="主管主管审核通过")
rast3.save()

ret = ReleaseApplyStateType.objects.filter(name="主管待审核")
if len(ret) == 1:
	print "OK"
RA_STATE_CLOSED = u"已关闭上线申请单"
RA_STATE_WAITTING_MANAGER_CONFIRMED = u"待经理确认"
RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED = u"待开发构建确认"
RA_STATE_WAITTING_DEVELOPER_MODIFIED= u"待开发修改"
RA_STATE_WAITTING_DEVELOPER_CLOSED = u"待开发关闭"
RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED = "待主管确认"
RA_STATE_WAITTING_TEAM_LEADER_MODIFIED = u"待主管修改"
RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED = "待主管构建确认"
RA_STATE_WAITTING_TEAM_LEADER_CLOSED = u"待主管关闭"
RA_STATE_WAITTING_TESTER_CONFIRMED = "待测试确认"
RA_STATE_WAITTING_OPERATOR_CLAIMED = u"待运维认领"
RA_STATE_WAITTING_OPERATOR_EXECUTED = u"待运维执行"

import datetime
ra = ReleaseApply(title="mop上线",applier = u ,tester = u,release_type=u"常规发布",producter = u,application = app,planned_at=datetime.datetime.now())
ra.save()

ras = ReleaseApplyState(creator = u,release_apply = ra,state = RA_STATE_WAITTING_OPERATOR_EXECUTED)
ras.save()

ras = ReleaseApplyState(creator = u,release_apply = ra,state = RA_STATE_WAITTING_TESTER_CONFIRMED)
ras.save()

ras = ReleaseApplyState(creator = u,release_apply = ra,state = RA_STATE_WAITTING_OPERATOR_CLAIMED)
ras.save()
#help(ra)

print len(ReleaseApplyState.objects.all())  == 3
for ra in ReleaseApply.objects.all():
	for rsas in ra.releaseapplystate_set.all():
		print ra.title,rsas.state


abs = ApplicationBuildState(name="in queue")
abs.save()
abs = ApplicationBuildState(name="building")
abs.save()
abs = ApplicationBuildState(name="finished")
abs.save()
ab = ApplicationBuild(builder = u , release_apply = ra,application = app,state = "zz")
ab.save()

for ab in ApplicationBuild.objects.all():
	print ab.state

adts = AutoDeployTaskState(name="in queue")
adts.save()
adt = AutoDeployTask(user = u, application = app,release_apply = ra,state = adts)
adt.save()

#help(adt)
adtrs = AutoDeployTaskResourceState(name ="in queue")
adtrs.save()
for res in app.resources.all():
	adtr = AutoDeployTaskResource(task = adt, resource =res ,state = adtrs)
	adtr.save()


