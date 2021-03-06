#!/usr/bin/env python
#encoding=utf-8
from ConfigParser import ConfigParser
import hashlib
import json
from flask import Blueprint, render_template, get_flashed_messages, request, flash, redirect, url_for, session, \
    send_file
from flask.ext.login import UserMixin, LoginManager, logout_user, login_required, login_user
import ldap
from models.mone.models import User, Role, Organization
import sys
from utils.decorators import check_access

reload(sys)
sys.setdefaultencoding('utf8')

user = Blueprint('user', __name__)
login_manager = LoginManager()
login_manager.login_view = "user.login"
login_manager.login_message = u"你好，请先登录。"
config = ConfigParser()
with open('mone.conf', 'r') as cfgfile:
    config.readfp(cfgfile)
    login_type = config.get('user_configure', 'login_type')
cfgfile.close()


class UserNotFoundError(Exception):
    pass

def check_user(email=None, user_id=None):
    if user_id:
        user_datas = User.objects.filter(id=user_id)
    else:
        user_datas = User.objects.filter(email=email)
    if user_datas:
        return user_datas[0]
    else:
        return False

class set_user(UserMixin):
    '''Simple User class'''

    def __init__(self, id):
        if not check_user(id):
            raise UserNotFoundError()
        self.id = id

    @classmethod
    def get(self_class, id):
        '''Return admin_module instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None

@user.record_once
def on_load(state):
	state.app.config['SECRET_KEY'] = 'SET T0 4NY SECRET KEY L1KE RAND0M H4SH'
	login_manager.init_app(state.app)

@login_manager.user_loader
def load_user(id):
    #考虑记住密码，需要回调时记录session
    user_data = check_user(id)
    is_session = session.get('user_data')
    if not is_session:
        session['user_data'] = {"email": user_data.email, "username": user_data.username, "user_id": user_data.id}
        roles_data = user_data.role_set.all()
        own_roles_list = []
        for role_data in roles_data:
            own_roles_list.append(role_data.id)
        session['own_roles_list'] = own_roles_list
        session['is_operator'] = user_data.is_operator()
        session['is_manager'] = user_data.is_manager()
    return set_user.get(id)

@user.route('/login/')
def login():
    message = ', '.join([ str(m) for m in get_flashed_messages() ])
    return render_template('user/login.html', message=message)

def update_user(email, **kwargs):
    user_data = User.objects.filter(email=email).update(**kwargs)
    return user_data

def get_pwd(passward):
    '''
    登陆密码加密
    :param passward:
    :return:
    '''
    m = hashlib.md5()
    key_str = '#@$#Dtg46SF$SD-78'
    new_key_str = passward + key_str
    m.update(new_key_str)
    pwd = m.hexdigest()
    return pwd

def ldap_check_user(user, pw):
    '''
    验证登陆
    :param user:
    :param pw:
    :return:
    '''
    con = ldap.initialize('ldap://172.16.1.110:389')
    try:
        login_data = con.simple_bind_s(user, pw)
        if login_data:
            if login_data[2]:
                return True
        else:
            return False
    except Exception, e:
        return False

@user.route('/login/check/', methods=['POST'])
def login_check():
    '''
    登陆
    :return:
    '''
    email = request.form.get('email')
    email = email + '@meizu.com'
    password = request.form.get('password')
    _remember_me = request.form.get('_remember_me')
    if login_type == 'ldap':
        # if email == 'maolingzhi@meizu.com':
        #     user = set_user.get(email)
        #     login_user(user)
        #     user_data = check_user(email)
        #     session['user_data'] = {"email": user_data.email, "username": user_data.username, "user_id": user_data.id}
        #     roles_data = user_data.role_set.all()
        #     own_roles_list = []
        #     for role_data in roles_data:
        #         own_roles_list.append(role_data.id)
        #     session['own_roles_list'] = own_roles_list
        #     session['is_operator'] = user_data.is_operator()
        #     session['is_manager'] = user_data.is_manager()
        #     return redirect(url_for('user.index'))
        if not ldap_check_user(email, password):
            flash('用户名或密码错误')
            return redirect(url_for('user.login'))
        user_data = check_user(email)
        if not user_data.password:
            password = get_pwd(password)
            update_user(email=email, password=password)
        user = set_user.get(email)
        if _remember_me == 'on':
            login_user(user, remember=True)
        else:
            login_user(user)
        session['user_data'] = {"email": user_data.email, "username": user_data.username, "user_id": user_data.id}
        roles_data = user_data.role_set.all()
        own_roles_list = []
        for role_data in roles_data:
            own_roles_list.append(role_data.id)
        session['own_roles_list'] = own_roles_list
        session['is_operator'] = user_data.is_operator()
        session['is_manager'] = user_data.is_manager()
        return redirect(url_for('user.index'))
    return redirect(url_for('user.login'))

@user.route('/logout/')
def logout():
    '''
    登出
    :return:
    '''
    session.pop('user_data', None)
    logout_user()
    return redirect(url_for('user.login'))

@user.route('/')
@login_required
def index():
    return redirect(url_for('worksheet.taskpad'))

@user.route('/access_control/')
@login_required
@check_access([{"role_id": 1, "role_name": "系统管理员"}])
def access_control():
    user_datas = User.objects.all()
    role_datas = Role.objects.all()
    organization_datas = Organization.objects.all()
    role_list = []
    for data in role_datas:
        role_list.append({'id': data.id, 'name': data.name})
    organization_list = []
    for data in organization_datas:
        organization_list.append({'id': data.id, 'name': data.name})
    user_list = []
    for data in user_datas:
        user_id = data.id
        own_role_dict = {}
        own_role_datas = data.role_set.all()
        for own_role_data in own_role_datas:
            own_role_dict[own_role_data.id] = True
        if data.organization:
            organization = data.organization.name
            organization_id = data.organization_id
        else:
            organization = ''
            organization_id = ''

        # parent = data.parent.username if data.parent else ''
        if Role.objects.filter(id=user_id):
            role = Role.objects.filter(id=user_id)[0].name
            role_id = Role.objects.filter(id=user_id)[0].id
        else:
            role = ''
            role_id = ''
        user_list.append({'id': user_id, 'username': data.username, 'organization': organization, 'organization_id': organization_id,  'role': role, 'role_id': role_id, 'own_role_dict': own_role_dict})

    return render_template("user/access_control.html", user_list=user_list, role_list=role_list, organization_list=organization_list)

@user.route('/change_information/', methods=['POST'])
@login_required
def change_information():
    user_id = request.form.get('user_id')
    try:
        role_list = json.loads(request.form.get('role_list'))
    except:
        return json.dumps({'status': 1001, 'message': 'failure'})
    organization_id = request.form.get('organization_id')
    try:
        user_data = check_user(user_id=user_id)
        user_data.organization_id = organization_id
        user_data.save()
    except:
        user_data = None
    if user_data:
        user_data.role_set.clear()
        for role_id in role_list:
            role_data = Role.objects.filter(id=role_id)[0]
            user_data.role_set.add(role_data)
        own_user_id = session.get('user_data').get('user_id')
        own_user_data = check_user(user_id=own_user_id)
        own_roles_data = own_user_data.role_set.all()
        own_roles_list = []
        for role_data in own_roles_data:
            own_roles_list.append(role_data.id)
        session['own_roles_list'] = own_roles_list
        session.pop('user_data', None)
        return json.dumps({'status': 200, 'message': 'success'})
    else:
        return json.dumps({'status': 1001, 'message': 'failure'})

@user.route('/organization_control/')
@login_required
@check_access([{"role_id": 1, "role_name": "系统管理员"}])
def organization_control():
    organization_list = []
    organizations = Organization.objects.all()
    for organization in organizations:
        leader_id = ''
        leader_name = ''
        leader = organization.leader
        if leader:
            leader_id = leader.id
            leader_name = leader.username
        organization_list.append({'id': organization.id, 'name': organization.name, 'leader_id': leader_id, 'leader_name': leader_name})
    user_list = []
    users = User.objects.all()
    for user in users:
        user_list.append({'id': user.id, 'name': user.username})
    return render_template("user/organization_control.html", user_list=user_list, organization_list=organization_list)

@user.route('/update/org_leader/', methods=['POST'])
@login_required
@check_access([{"role_id": 1, "role_name": "系统管理员"}])
def update_org_leader():
    user_id = request.form.get('user_id')
    org_id = request.form.get('org_id')
    try:
        org_data = Organization.objects.filter(id=org_id).update(leader=user_id)
    except:
        org_data = None
    if org_data:
        result = {'status': 200, 'message': '请求成功'}
    else:
        result = {'status': 1001, 'message': '请求失败'}
    return json.dumps(result)

@user.route('/download/<path:path>')
@login_required
def download_file(path):
    try:
        file = send_file(path)
    except:
        file = json.dumps({'status': 1001, 'message': '文件不存在'})
    return file


