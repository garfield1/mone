#encoding=utf-8
from django.db.models.signals import post_save
from django.utils import timezone
from django.db import models
# Create your models here.


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
	applier = models.ForeignKey(User)
	operator = models.ForeignKey('User', null = True, blank = True, related_name = "operator")#运维人员
	content = models.TextField()
	state = models.CharField(max_length = 400,null = True,blank = True)
	worksheet_type = models.ForeignKey(WorksheetType)
	planned_at = models.DateTimeField(default=timezone.now)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

	# def __init__(self, *args, **kwargs):
	# 	super(Worksheet, self).__init__(*args, **kwargs)
    #
	# def save(self, *args, **kwargs):
	# 	if self.state == '待审核':
	# 		state_transfer(self.applier, WS_USER_ACTION_WS_CREATED, self)
	# 	elif self.state == '待认领':
	# 		state_transfer(self.applier, WS_USER_ACTION_TEAM_LEADER_CONFIRMED, self)
	# 	elif self.state == '待执行':
	# 		state_transfer(self.operator, WS_USER_ACTION_OPENATOR_CLAIMED, self)
	# 	elif self.state == '已完成':
	# 		state_transfer(self.operator, WS_USER_ACTION_OPERATOR_EXECUTED, self)
	# 	elif self.state == '已打回':
	# 		if self.user.organization.name == '基础运维':
	# 			state_transfer(self.user, WS_USER_ACTION_OPENATOR_REJECTED, self, reject_reason = self.reject_reason)
	# 		else:
	# 			state_transfer(self.user,WS_USER_ACTION_TEAM_LEADER_REJECTED, self, reject_reason = self.reject_reason)
	# 	elif self.state == '已关闭':
	# 		state_transfer(self.applier, WS_STATE_CLOSE, self)
	# 	super(Worksheet, self).save(*args, **kwargs)
	# 	return


class WorksheetState(models.Model):
	creator = models.ForeignKey(User,related_name='ws_creator') #sys or specific user
	waitting_confirmer = models.ForeignKey(User,related_name='ws_waitting_confirmer',null = True,blank=True)#creator must be sys
	worksheet = models.ForeignKey(Worksheet)
	state = models.CharField(max_length = 400,null = True,blank = True)
	reject_reason = models.CharField(max_length = 400,null = True,blank = True)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

  
def worksheet_state_post_save(sender, instance, signal, *args, **kwargs):
	wss = instance
	w = wss.worksheet
	w.state = wss.state
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
	applier = models.ForeignKey(User,related_name = "applier")
	tester = models.ForeignKey(User,related_name = "tester")
	producter = models.ForeignKey(User,related_name = "producter")
	release_type = models.CharField(max_length = 400,null = True,blank = True)
	risk_level = models.CharField(max_length = 400,null = True,blank = True)
	deploy_type = models.CharField(max_length = 400,null = True,blank = True)
	application = models.ForeignKey(Application)
	wiki_url = models.CharField(max_length = 400,null = True,blank = True)
	jira_url = models.CharField(max_length = 400,null = True,blank = True)
	planned_at = models.DateTimeField()
	memo  = models.CharField(max_length = 400,null = True,blank = True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
class ReleaseApplyState(models.Model):
	creator = models.ForeignKey(User,related_name='creator') #sys or specific user
	waitting_confirmer = models.ForeignKey(User,related_name='waitting_confirmer',null = True,blank=True)#creator must be sys
	release_apply = models.ForeignKey(ReleaseApply)
	state = models.CharField(max_length = 400,null = True,blank = True)
	#state_type = models.OneToOneField(ReleaseApplyStateType)
	created_at= models.DateTimeField(auto_now_add=True)
	updated_at= models.DateTimeField(auto_now=True)

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

