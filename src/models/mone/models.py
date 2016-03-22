#encoding=utf-8
from django.db.models.signals import post_save
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
# Create your models here.

#action代表瞬时的动作
#开发action3个 主管action5个 运维action3个
WS_USER_ACTION_DEVELOPER_CREATED = u"开发工单创建"
WS_USER_ACTION_DEVELOPER_RESUBMIT = u"开发工单重提交"
WS_USER_ACTION_DEVELOPER_CLOSED = u"开发关闭工单"
WS_USER_ACTION_TEAM_LEADER_CREATED = u"主管工单创建"
WS_USER_ACTION_TEAM_LEADER_RESUBMIT = u"主管工单创建"
WS_USER_ACTION_TEAM_LEADER_CONFIRMED = u"主管确认"
WS_USER_ACTION_TEAM_LEADER_REJECTED = u"主管打回"
WS_USER_ACTION_TEAM_LEADER_CLOSED = u"主管关闭"
WS_USER_ACTION_OPERATOR_REJECTED = u"运维打回"
WS_USER_ACTION_OPERATOR_CLAIMED = u"运维认领"
WS_USER_ACTION_OPERATOR_EXECUTED = u"运维执行成功"
#state代表一种持续的中间状态
#主管状态3个 开发状态2个 运维状态2个 关闭状态1个
WS_STATE_CLOSED = u"已关闭上线工单"
WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED = u"待主管确认"   #待审核
WS_STATE_WAITTING_DEVELOPER_MODIFIED= u"待开发修改" #已打回
WS_STATE_WAITTING_TEAM_LEADER_MODIFIED = u"待主管修改" #已打回
WS_STATE_WAITTING_OPERATOR_CLAIMED = u"待运维认领" #待认领
WS_STATE_WAITTING_OPERATOR_EXECUTED = u"待运维执行"#待执行
WS_STATE_WAITTING_TEAM_LEADER_CLOSED = u"待主管关闭工单"
WS_STATE_WAITTING_DEVELOPER_CLOSED = u"待开发关闭工单"

WS_STATE_SCORES ={
	WS_STATE_CLOSED:9000000000000L,
	WS_STATE_WAITTING_TEAM_LEADER_CONFIRMED:200L,
	WS_STATE_WAITTING_DEVELOPER_MODIFIED:10L,
	WS_STATE_WAITTING_TEAM_LEADER_MODIFIED:200L,
	WS_STATE_WAITTING_OPERATOR_CLAIMED:5000000L,
	WS_STATE_WAITTING_OPERATOR_EXECUTED:50000000L,
	WS_STATE_WAITTING_TEAM_LEADER_CLOSED:200000000L,
	WS_STATE_WAITTING_DEVELOPER_CLOSED:100000000L,
}




#action代表瞬时的动作
#主管action6个，开发action4个,经理action2个，测试action2个，运维action3个

RA_USER_ACTION_TEAM_LEADER_CREATED = u"主管创建"
RA_USER_ACTION_TEAM_LEADER_RESUBMIT = u"主管重提交"
RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED = u"主管构建确认"
RA_USER_ACTION_TEAM_LEADER_REJECTED = u"主管打回"
RA_USER_ACTION_TEAM_LEADER_CLOSED = u"主管关闭上线申请单"

RA_USER_ACTION_DEVELOPER_CREATED = u"开发创建"
RA_USER_ACTION_TEAM_LEADER_CONFIRMED = u"主管确认"
RA_USER_ACTION_MANAGER_CONFIRMED = u"经理确认"
RA_USER_ACTION_MANAGER_REJECTED = u"经理打回"
RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED = u"开发构建确认"
RA_USER_ACTION_TESTER_CONFIRMED = u"测试通过确认"
RA_USER_ACTION_TESTER_REJECT = u"测试拨回"
RA_USER_ACTION_OPERATOR_REJECTED = u"运维打回"
RA_USER_ACTION_OPERATOR_CLAIMED = u"运维认领"
RA_USER_ACTION_OPERATOR_EXECUTED = u"运维执行发布成功"
RA_USER_ACTION_DEVELOPER_CLOSED = u"开发关闭上线申请单"
RA_USER_ACTION_DEVELOPER_RESUBMIT = u"开发重提交"
#state表示一种持续的状态,共12种
RA_STATE_CLOSED = u"已关闭上线申请单"
RA_STATE_WAITTING_MANAGER_CONFIRMED = u"待经理确认"
RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED = u"待开发构建确认"
RA_STATE_WAITTING_DEVELOPER_MODIFIED= u"待开发修改"
RA_STATE_WAITTING_DEVELOPER_CLOSED = u"待开发关闭"
RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED = u"待主管确认"
RA_STATE_WAITTING_TEAM_LEADER_MODIFIED = u"待主管修改" 
RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED = u"待主管构建确认"
RA_STATE_WAITTING_TEAM_LEADER_CLOSED = u"待主管关闭"
RA_STATE_WAITTING_TESTER_CONFIRMED = u"待测试确认"
RA_STATE_WAITTING_OPERATOR_CLAIMED = u"待运维认领" 
RA_STATE_WAITTING_OPERATOR_EXECUTED = u"待运维执行"

RA_STATE_SCORES = {
	RA_STATE_CLOSED:9000000000000L,
	RA_STATE_WAITTING_MANAGER_CONFIRMED:3000L,
	RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED:10000L,
	RA_STATE_WAITTING_DEVELOPER_MODIFIED:10L,
	RA_STATE_WAITTING_DEVELOPER_CLOSED:100000000L,
	RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED:200L,
	RA_STATE_WAITTING_TEAM_LEADER_MODIFIED:200L,
	RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED:20000L,
	RA_STATE_WAITTING_TEAM_LEADER_CLOSED:200000000L,
	RA_STATE_WAITTING_TESTER_CONFIRMED:400000L,
	RA_STATE_WAITTING_OPERATOR_CLAIMED:5000000L,
	RA_STATE_WAITTING_OPERATOR_EXECUTED:50000000L,
}


class Organization(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	parent = models.ForeignKey('self', default = -1, null = True, blank = True, related_name = 'children')
	leader = models.ForeignKey('User', null = True, blank = True, related_name = "leader")#机构负责人
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class User(models.Model):
	username = models.CharField(max_length = 400,null = True,blank = True)
	meizu_id = models.IntegerField(null = True,blank = True)
	email = models.CharField(max_length = 400,null = True,blank = True)
	password = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	organization = models.ForeignKey(Organization,null=True, blank=True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

	def is_team_leader(self):
		print self.email
		if self.organization.leader == self:
			return True
		return False

	def is_manager(self):
		ret = self.role_set.all() & Role.objects.filter(name_endswith=u"经理").all()
		if len(ret) > 0:
			return True
		return False

	def is_operator(self):
		ret = self.role_set.all() & Role.objects.filter(name_startswith=u"运维").all()
		if len(ret) > 0:
			return True
		return False

	def created_release_applys_by_pagination(self , current_page , pagesize = 1):
		"""
		我的上线申请
		"""
		ret = self.release_apply_set.all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))

	#TODO
	def waitting_confirmed_release_applys_by_pagination(self, current_page , pagesize = 1):
		"""
		我的待操作上线申请,有问题
		"""
		ret = ReleaseApply.objects.filter(waitting_confirmer_id = self.id).all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))
			
	def operated_release_applys_by_pagination(self , current_page , pagesize = 1):
		"""
		我的已操作上线申请
		"""
		ret = ReleaseApplyState.objects.filter(creator = self).order_by("-created_at").all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))

	def created_worksheets_by_pagination(self, current_page , pagesize = 1):
		"""
		我创建的工单
		"""
		ret = self.worksheet_set.all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))

	def waitting_confirmed_worksheets_by_pagination(self , current_page , pagesize = 1):
		"""
		我的待操作工单
		"""
		if self.is_operator():
			ret = Worksheet.objects.filter(state =  u'待运维认领').all()
		else:
			ret = Worksheet.objects.filter(waitting_confirmer_id = self.id).all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))

	def operated_worksheets_by_pagination(self , current_page , pagesize = 1):
		"""
		我的已操作工单
		"""
		ret = WorksheetState.objects.filter(creator = self).order_by("-created_at").all()
		p = Paginator(ret , pagesize)
		return (p.page(current_page).object_list, len(ret))

class Role(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	user = models.ManyToManyField(User)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)
	
class LogType(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class Log(models.Model):
	user = models.ForeignKey(User)
	message = models.CharField(max_length = 400,null = True,blank = True)
	ip = models.CharField(max_length = 400,null = True,blank = True)
	log_type = models.ForeignKey(LogType,null=True, blank=True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)
	
class WorksheetType(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class Worksheet(models.Model):
	title = models.CharField(max_length = 400,null = True,blank = True)
	applier = models.ForeignKey(User,related_name="worksheet_set")
	#operator = models.ForeignKey('User', null = True, blank = True, related_name = "operator")#运维人员
	operator = models.ForeignKey(User,null=True,blank=True,related_name = "w_operator")
	content = models.TextField()
	waitting_confirmer = models.ForeignKey(User,related_name='ws_waitting_confirmer',null = True,blank=True)
	state = models.CharField(max_length = 400,null = True,blank = True)
	state_value = models.BigIntegerField(null = True,blank = True)
	worksheet_type = models.ForeignKey(WorksheetType)
	planned_at = models.DateTimeField(default=timezone.now)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class WorksheetState(models.Model):
	creator = models.ForeignKey(User,related_name='ws_creator') #sys or specific user
	waitting_confirmer = models.ForeignKey(User,related_name='wss_waitting_confirmer',null = True,blank=True)#creator must be sys
	worksheet = models.ForeignKey(Worksheet)
	state = models.CharField(max_length = 400,null = True,blank = True)
	action = models.CharField(max_length = 400,null = True,blank = True)
	reject_reason = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)
  
def worksheet_state_post_save(sender, instance, signal, *args, **kwargs):
	wss = instance
	w = wss.worksheet
	w.state = wss.state
	w.state_value = WS_STATE_SCORES[w.state]
	w.waitting_confirmer_id = wss.waitting_confirmer_id
	w.save()

post_save.connect(worksheet_state_post_save, sender = WorksheetState)

class ResourceType(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class Resource(models.Model):
	wan_ip = models.CharField(max_length = 400,null = True,blank = True)
	lan_ip = models.CharField(max_length = 400,null = True,blank = True)
	resource_type = models.ForeignKey(ResourceType)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class Application(models.Model):
	name = models.CharField(max_length = 255,null = True,blank = True,unique=True)
	repo = models.CharField(max_length = 400,null = True,blank = True)
	resources = models.ManyToManyField(Resource)#线上 测试
	wiki_url = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class EmailQueue(models.Model):
	email = models.CharField(max_length = 400,null = True,blank = True)
	title = models.CharField(max_length = 400,null = True,blank = True)
	content = models.TextField()
	is_sended = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class ReleaseApplyStateType(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class ReleaseApply(models.Model):
	title = models.CharField(max_length = 400,null = True,blank = True)
	applier = models.ForeignKey(User,related_name = "release_apply_set")
	tester = models.ForeignKey(User,related_name = "tester")
	operator = models.ForeignKey(User, null = True, blank = True, related_name = "operator")#运维人员
	producter = models.ForeignKey(User,related_name = "producter")
	release_type = models.CharField(max_length = 400,null = True,blank = True)
	risk_level = models.CharField(max_length = 400,null = True,blank = True)
	deploy_type = models.CharField(max_length = 400,null = True,blank = True)
	application = models.ForeignKey(Application)
	wiki_url = models.CharField(max_length = 400,null = True,blank = True)
	jira_url = models.CharField(max_length = 400,null = True,blank = True)
	planned_at = models.DateTimeField()
	memo  = models.CharField(max_length = 400,null = True,blank = True)
	waitting_confirmer_id = models.IntegerField(null = True , blank = True)
	state = models.CharField(max_length = 400,null = True,blank = True)
	state_value = models.BigIntegerField(null = True,blank = True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
class ReleaseApplyState(models.Model):
	creator = models.ForeignKey(User,related_name='creator') #sys or specific user
	waitting_confirmer = models.ForeignKey(User,related_name='waitting_confirmer',null = True,blank=True)#creator must be sys
	release_apply = models.ForeignKey(ReleaseApply)
	state = models.CharField(max_length = 400,null = True,blank = True)
	action = models.CharField(max_length = 400,null = True,blank = True)
	reject_reason = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

def release_apply_state_post_save(sender, instance, signal, *args, **kwargs):
	ras = instance
	ra = ras.release_apply
	ra.state = ras.state
	ra.state_value = RA_STATE_SCORES[ras.state]
	ra.waitting_confirmer_id = ras.waitting_confirmer_id
	ra.save()

post_save.connect(release_apply_state_post_save, sender = ReleaseApplyState)

class ApplicationBuildState(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class ApplicationBuild(models.Model):
	builder = models.ForeignKey(User)
	release_apply = models.ForeignKey(ReleaseApply)
	application = models.ForeignKey(Application)
	message = models.TextField()
	state = models.CharField(max_length = 400,null = True,blank = True)
	#application_build_state = models.ForeignKey(ApplicationBuildState)
	package_url = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class AutoDeployTaskState(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class AutoDeployTask(models.Model):
	user = models.ForeignKey(User)
	application = models.ForeignKey(Application)
	release_apply = models.ForeignKey(ReleaseApply)
	resources = models.ManyToManyField(Resource,through="AutoDeployTaskResource")
	state = models.ForeignKey(AutoDeployTaskState)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class AutoDeployTaskResourceState(models.Model):
	name = models.CharField(max_length = 400,null = True,blank = True)
	desc = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

class AutoDeployTaskResource(models.Model):
	task = models.ForeignKey(AutoDeployTask)
	resource = models.ForeignKey(Resource)
	message = models.TextField()
	state = models.ForeignKey(AutoDeployTaskResourceState)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

