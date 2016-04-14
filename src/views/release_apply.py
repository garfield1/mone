#!/usr/bin/env python
# encoding=utf-8
from ConfigParser import ConfigParser
import json
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
from flask.ext.login import login_required
import time
from views._release_apply import state_transfer
from models.mone.models import Application, ReleaseApply, User, Role, RA_USER_ACTION_TEAM_LEADER_CREATED, \
    RA_USER_ACTION_DEVELOPER_CREATED, ReleaseApplyState, RA_USER_ACTION_OPERATOR_CLAIMED, \
    RA_USER_ACTION_OPERATOR_EXECUTED, RA_STATE_CLOSED, RA_STATE_WAITTING_DEVELOPER_MODIFIED, \
    RA_STATE_WAITTING_TEAM_LEADER_MODIFIED, RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED, \
    RA_STATE_WAITTING_MANAGER_CONFIRMED, \
    RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED, RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED, \
    RA_STATE_WAITTING_TESTER_CONFIRMED, RA_STATE_WAITTING_OPERATOR_CLAIMED, RA_STATE_WAITTING_OPERATOR_EXECUTED, \
    RA_STATE_WAITTING_COMPLETE, RA_USER_ACTION_MANAGER_CONFIRMED, RA_USER_ACTION_MANAGER_REJECTED, \
    RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED, RA_STATE_WAITTING_DEVELOPER_CLOSED, RA_USER_ACTION_TEAM_LEADER_REJECTED, \
    RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED, RA_USER_ACTION_TEAM_LEADER_CONFIRMED, \
    RA_STATE_WAITTING_TEAM_LEADER_CLOSED, RA_USER_ACTION_TESTER_CONFIRMED, RA_USER_ACTION_TESTER_REJECT, \
    RA_USER_ACTION_OPERATOR_REJECTED, RA_USER_ACTION_TEAM_LEADER_RESUBMIT, RA_USER_ACTION_DEVELOPER_RESUBMIT, \
    ApplicationBuild, ReleaseapplyBuild, BulidQueue

config = ConfigParser()
with open('mone.conf', 'r') as cfgfile:
    config.readfp(cfgfile)
    page_size = int(config.get('page', 'page_size'))
    upload_path = config.get('path', 'upload_path')
cfgfile.close()

release_apply = Blueprint('release_apply', __name__)


@release_apply.route('/add/application/', methods=['GET'])
@login_required
def add_application():
    application_id = request.args.get('application_id')
    try:
        application_data = Application.objects.filter(id=application_id)[0]
    except Exception, e:
        application_data = {'name': '', 'git_url': '', 'file_url': ''}
    return render_template("release_apply/add_application.html", application_data=application_data)

@release_apply.route('/application/list/')
def application_list():
    application_datas = Application.objects.all()
    application_list = []
    for application_data in application_datas:
        application_list.append({'application_id': application_data.id, 'name': application_data.name, 'git_url': application_data.git_url, 'file_path': application_data.file_path or '', 'created_at': application_data.created_at or ''})
    return render_template("release_apply/app_list.html", application_list=application_list)

@release_apply.route('/taskpad/', methods=['GET'])
@login_required
def taskpad():
    return render_template("release_apply/taskpad.html")


@release_apply.route('/add/release_apply/', methods=['GET'])
@login_required
def add_release_apply():
    # user_id = session.get('user_data').get('user_id')
    release_apply_id = request.args.get('release_apply_id')
    # try:
    #     user_data = User.objects.filter(id=user_id)[0]
    # except Exception, e:
    #     user_data = None
    application_list = []
    application_dict = {}
    # if user_data:
    #     applications = user_data.application_set.all()
    #     for application in applications:
    #         application_list.append({'id': application.id, 'name': application.name})
    #         application_dict[application.id] = application.git_url
    applications = Application.objects.all()
    for application in applications:
            application_list.append({'id': application.id, 'name': application.name})
            application_dict[application.id] = application.git_url
    producter_list = []
    tester_list = []
    producter_datas = Role.objects.filter(name__contains="产品经理")[0].user.all()
    tester_datas = Role.objects.filter(name__contains="测试工程师")[0].user.all()
    for producter_data in producter_datas:
        producter_list.append({'user_id': producter_data.id, 'username': producter_data.username})
    for tester_data in tester_datas:
        tester_list.append({'user_id': tester_data.id, 'username': tester_data.username})
    if release_apply_id:
        try:
            releaseapply_data = ReleaseApply.objects.filter(id=release_apply_id)[0]
        except Exception, e:
            return redirect(url_for('user.index'))
    else:
        releaseapply_data = {'update_model': '', 'attention': '', 'update_content': '',
                             'memo': '', 'producter_id': '', 'producter': {'username': ''},
                             'release_type': '', 'risk_level': '', 'tester_id': '',
                             'tester': {'username': ''}, 'application_id': '', 'application': {'name': ''},
                             'deploy': '', 'wiki_url': ''}
    return render_template("release_apply/add.html", releaseapply_data=releaseapply_data, producter_list=producter_list,
                           tester_list=tester_list, application_list=application_list,
                           application_dict=json.dumps(application_dict))


@release_apply.route('/get/application_list/')
@login_required
def get_application_list():
    user_id = session.get('user_data').get('user_id')
    try:
        user_data = User.objects.filter(id=user_id)[0]
    except Exception, e:
        user_data = None
    application_list = []
    result = {'status': 1001, 'message': '用户不存在', 'data': {'application_list': []}}
    if user_data:
        applications = user_data.application_set.all()
        for application in applications:
            application_list.append({'id': application.id, 'name': application.name, 'git_url': application.git_url})
        result = {'status': 200, 'message': '请求成功', 'data': {'application_list': application_list}}
    return json.dumps(result)


@release_apply.route('/list/', methods=['GET'])
@login_required
def list():
    producter_list = []
    tester_list = []
    operator_list = []
    producter_datas = Role.objects.filter(name__contains="产品经理")[0].user.all()
    tester_datas = Role.objects.filter(name__contains="测试工程师")[0].user.all()
    operator_datas = Role.objects.filter(name__contains="运维")[0].user.all()
    for producter_data in producter_datas:
        producter_list.append({'user_id': producter_data.id, 'username': producter_data.username})
    for tester_data in tester_datas:
        tester_list.append({'user_id': tester_data.id, 'username': tester_data.username})
    for operator_data in operator_datas:
        operator_list.append({'user_id': operator_data.id, 'username': operator_data.username})
    return render_template("release_apply/list.html", producter_list=producter_list, tester_list=tester_list, operator_list=operator_list)


state_to_step = {
    RA_STATE_CLOSED: -1,
    RA_STATE_WAITTING_DEVELOPER_MODIFIED: 0,
    RA_STATE_WAITTING_TEAM_LEADER_MODIFIED: 0,
    RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED: 1,
    RA_STATE_WAITTING_MANAGER_CONFIRMED: 2,
    RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED: 4,
    RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED: 4,
    RA_STATE_WAITTING_TESTER_CONFIRMED: 3,
    RA_STATE_WAITTING_OPERATOR_CLAIMED: 5,
    RA_STATE_WAITTING_OPERATOR_EXECUTED: 6,
    RA_STATE_WAITTING_COMPLETE: 7
}

step_to_message = {
    -1: '工单已关闭',
    0: '工单已打回',
    1: '主管待审批',
    2: '经理待审批',
    3: '待测试',
    4: '待构建',
    5: '运维发布中',
    6: '运维发布中',
    7: '已完成'
}

@release_apply.route('/details/<release_apply_id>')
@login_required
def detail(release_apply_id):
    '''
    state_to_step = {
    已关闭上线申请单: -1,
    待开发修改: 0,
    待主管修改: 0,
    待主管确认: 1,
    待经理确认: 2,
    待开发构建确认: 3,
    待主管构建确认: 3,
    待测试确认: 4,
    待运维认领: 5,
    待运维执行: 6,
    已完成: 7
    }
    当step为－2时: 状态未知
    :param release_apply_id:
    :return:
    '''
    try:
        releaseapply_data = ReleaseApply.objects.filter(id=release_apply_id)[0]
    except Exception, e:
        releaseapply_data = None
    if not releaseapply_data:
        return redirect(url_for('user.index'))
    releaseapplystate_list = []
    releaseapplystates = ReleaseApplyState.objects.filter(release_apply_id=releaseapply_data.id)
    for releaseapplystate in releaseapplystates:
        releaseapplystate_list.append(
            {'name': releaseapplystate.creator.username, 'created_at': releaseapplystate.created_at,
             'state': releaseapplystate.state})
    step = state_to_step.get(releaseapply_data.state) if releaseapply_data.state else -2
    last_action = ''
    next_action = ''
    if releaseapply_data.state == RA_STATE_CLOSED:
        last_action = ''
        next_action = ''
    elif releaseapply_data.state == RA_STATE_WAITTING_MANAGER_CONFIRMED:
        last_action = RA_USER_ACTION_MANAGER_REJECTED
        next_action = RA_USER_ACTION_MANAGER_CONFIRMED
    elif releaseapply_data.state == RA_STATE_WAITTING_DEVELOPER_BUILD_CONFIRMED:
        last_action = ''
        next_action = RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED
    elif releaseapply_data.state == RA_STATE_WAITTING_DEVELOPER_MODIFIED:
        last_action = ''
        next_action = RA_USER_ACTION_DEVELOPER_CREATED
    elif releaseapply_data.state == RA_STATE_WAITTING_DEVELOPER_CLOSED:
        last_action = ''
        next_action = RA_USER_ACTION_DEVELOPER_CREATED
    elif releaseapply_data.state == RA_STATE_WAITTING_TEAM_LEADER_CONFIRMED:
        last_action = RA_USER_ACTION_TEAM_LEADER_REJECTED
        next_action = RA_USER_ACTION_TEAM_LEADER_CONFIRMED
    elif releaseapply_data.state == RA_STATE_WAITTING_TEAM_LEADER_MODIFIED:
        last_action = ''
        next_action = RA_USER_ACTION_TEAM_LEADER_CREATED
    elif releaseapply_data.state == RA_STATE_WAITTING_TEAM_LEADER_BUILD_CONFIRMED:
        last_action = ''
        next_action = RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED
    elif releaseapply_data.state == RA_STATE_WAITTING_TESTER_CONFIRMED:
        last_action = RA_USER_ACTION_TESTER_REJECT
        next_action = RA_USER_ACTION_TESTER_CONFIRMED
    elif releaseapply_data.state == RA_STATE_WAITTING_OPERATOR_CLAIMED:
        last_action = RA_USER_ACTION_OPERATOR_REJECTED
        next_action = RA_USER_ACTION_OPERATOR_CLAIMED
    elif releaseapply_data.state == RA_STATE_WAITTING_OPERATOR_EXECUTED:
        last_action = ''
        next_action = RA_USER_ACTION_OPERATOR_EXECUTED
    elif releaseapply_data.state == RA_STATE_WAITTING_COMPLETE:
        last_action = ''
        next_action = ''
    release_apply_message = step_to_message.get(step)
    try:
        releaseapplybuild_datas = ReleaseapplyBuild.objects.filter(release_apply_id=release_apply_id)
    except Exception, e:
        releaseapplybuild_datas = None
    releaseapplybuild_list = []
    if releaseapplybuild_datas:
        for releaseapplybuild_data in releaseapplybuild_datas:
            releaseapplybuild_list.append(
                {'releaseapplybuild_id': releaseapplybuild_data.id, 'message': releaseapplybuild_data.message,
                 'created_at': str(releaseapplybuild_data.created_at)[:19]})
    is_build = BulidQueue.objects.filter(release_apply_id=release_apply_id).order_by('-id')[0].is_build if BulidQueue.objects.filter(release_apply_id=release_apply_id) else False
    return render_template("release_apply/details.html", releaseapply_data=releaseapply_data,
                           releaseapplystate_list=releaseapplystate_list, step=step,
                           release_apply_message=release_apply_message, last_action=last_action,
                           next_action=next_action, releaseapplybuild_list=releaseapplybuild_list, is_build=is_build)

@release_apply.route('/update/application/', methods=['POST'])
@login_required
def update_application():
    name = request.form.get('name')
    git_url = request.form.get('git_url')
    user_id = session.get('user_data').get('user_id')
    file_path = request.form.get('file_path')
    test_mvn = request.form.get('test_mvn')
    pre_release_mvn = request.form.get('pre_release_mvn')
    formal_mvn = request.form.get('formal_mvn')
    application_id = request.form.get('application_id')
    result = {'status': 1001, 'message': '参数缺失'}
    if name and git_url:
        if application_id:
            try:
                Application.objects.filter(id=application_id).update(name=name, git_url=git_url, file_path=file_path, test_mvn=test_mvn, pre_release_mvn=pre_release_mvn, formal_mvn=formal_mvn)
                result = {'status': 200, 'message': '保存成功'}
            except Exception, e:
                print e
                result = {'status': 1001, 'message': '数据库异常'}
        else:
            result = {'status': 1002, 'message': '应用名称重复'}
            try:
                check_application_data = Application.objects.filter(name=name)[0]
            except Exception, e:
                check_application_data = None
            if not check_application_data:
                try:
                    application_data = Application(name=name, git_url=git_url, apply_user_id=user_id, file_path=file_path, test_mvn=test_mvn, pre_release_mvn=pre_release_mvn, formal_mvn=formal_mvn)
                    application_data.save()
                    result = {'status': 200, 'message': '保存成功'}
                except Exception, e:
                    result = {'status': 1001, 'message': '数据库异常'}
    return json.dumps(result)


@release_apply.route('/update/release_apply/', methods=['POST'])
@login_required
def update_release_apply():
    title = request.form.get('title')
    tester_id = request.form.get('tester_id')
    producter_id = request.form.get('producter_id')
    release_type = request.form.get('release_type')
    risk_level = request.form.get('risk_level')
    application_id = request.form.get('application_id')
    deploy = request.form.get('deploy')
    planned_at = request.form.get('planned_at')
    wiki_url = request.form.get('wiki_url')
    jira_url = request.form.get('jira_url')
    is_self_test = request.form.get('is_self_test')
    release_apply_id = request.form.get('release_apply_id')
    update_model = request.form.get('update_model')
    update_content = request.form.get('update_content')
    attention = request.form.get('attention')
    memo = request.form.get('memo')
    version = request.form.get('version')
    result = {'status': 1001, 'message': '参数缺失'}
    user_id = session.get('user_data').get('user_id')
    try:
        user_data = User.objects.filter(id=user_id)[0]
    except Exception, e:
        result = {'status': 1001, 'message': '数据库异常'}
        return json.dumps(result)
    is_manager = user_data.is_manager()
    if title and application_id and is_self_test:
        if release_apply_id:
            try:
                releaseapply_datas = ReleaseApply.objects.filter(id=release_apply_id)
                releaseapply_datas.update(title=title, tester=tester_id, producter=producter_id,
                                          release_type=release_type,
                                          risk_level=risk_level, application=application_id, deploy=deploy,
                                          planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
                                          is_self_test=is_self_test, update_model=update_model, attention=attention,
                                          update_content=update_content, memo=memo, version=version)

                releaseapply_data = releaseapply_datas[0]
                if is_manager:
                    state_transfer(user_data, RA_USER_ACTION_TEAM_LEADER_RESUBMIT, releaseapply_data)
                else:
                    state_transfer(user_data, RA_USER_ACTION_DEVELOPER_RESUBMIT, releaseapply_data)
                result = {'status': 200, 'message': '更新成功', 'data': {'release_apply_id': releaseapply_data.id}}
            except Exception, e:
                result = {'status': 1001, 'message': '数据库异常'}
        else:
            try:
                releaseapply_data = ReleaseApply(title=title, tester_id=tester_id, applier_id=user_id,
                                                 producter_id=producter_id, release_type=release_type,
                                                 risk_level=risk_level, application_id=application_id, deploy=deploy,
                                                 planned_at=planned_at, wiki_url=wiki_url, jira_url=jira_url,
                                                 is_self_test=is_self_test, update_model=update_model,
                                                 attention=attention, update_content=update_content, memo=memo, version=version)
                releaseapply_data.save()
                if is_manager:
                    state_transfer(user_data, RA_USER_ACTION_TEAM_LEADER_CREATED, releaseapply_data)
                else:
                    state_transfer(user_data, RA_USER_ACTION_DEVELOPER_CREATED, releaseapply_data)
                result = {'status': 200, 'message': '保存成功', 'data': {'release_apply_id': releaseapply_data.id}}
            except IndexError as ex:
                result = {'status': 1001, 'message': '数据库异常'}
    return json.dumps(result)


def get_release_apply_by_page(page_num, filter_type='taskpad', **kwargs):
    start_page = page_size * (page_num - 1)
    end_page = page_size * page_num
    if filter_type == 'taskpad':
        releaseapplys = ReleaseApply.objects.filter(**kwargs).exclude(state='已完成').order_by('-id')[start_page: end_page]
    else:
        releaseapplys = ReleaseApply.objects.filter(**kwargs).order_by('-id')[start_page: end_page]
    return releaseapplys


def get_release_apply_count(filter_type='taskpad', **kwargs):
    if filter_type == 'taskpad':
        return ReleaseApply.objects.filter(**kwargs).count()
    else:
        return ReleaseApply.objects.filter(**kwargs).count()

def get_own_release_apply_by_type(user_id, page_num, release_apply_type):
    start_page = page_size*(page_num-1)
    end_page = page_size*page_num
    if release_apply_type == 'tester':
        releaseapplys = ReleaseApply.objects.filter(tester_id=user_id).order_by('-id')[start_page: end_page]
        total = ReleaseApply.objects.filter(tester_id=user_id).count()
    elif release_apply_type == 'producter':
        releaseapplys = ReleaseApply.objects.filter(producter_id=user_id).order_by('-id')[start_page: end_page]
        total = ReleaseApply.objects.filter(producter_id=user_id).count()
    elif release_apply_type == 'operator':
        releaseapplys = ReleaseApply.objects.filter(operator_id=user_id).order_by('-id')[start_page: end_page]
        total = ReleaseApply.objects.filter(operator_id=user_id).count()
    else:
        releaseapplys = None
        total = 0
    return releaseapplys, total


@release_apply.route('/search_release_apply/', methods=['POST'])
@login_required
def search_release_apply():
    title = request.form.get('title')
    application_id = request.form.get('application_id')
    state = request.form.get('state')
    applier = request.form.get('applier')
    tester = request.form.get('tester')
    operator = request.form.get('operator')
    producter = request.form.get('producter')
    start_planned_time = request.form.get('start_planned_time')
    end_planned_time = request.form.get('end_planned_time')
    page_num = int(request.form.get('page_num') or 1)
    start_formal_at = request.form.get('start_formal_at')
    end_formal_at = request.form.get('end_formal_at')
    own_release_apply_status_id = request.form.get('own_release_apply_status_id')
    if own_release_apply_status_id:
        user_id = session.get('user_data').get('user_id')
        user_data = User.objects.filter(id=user_id)
        if own_release_apply_status_id == '1':
            release_applys, total = user_data.created_release_applys_by_pagination(page_num, page_size)
        elif own_release_apply_status_id == '2':
            release_applys, total = user_data.waitting_confirmed_release_applys_by_pagination(page_num, page_size)
        elif own_release_apply_status_id == '3':
            release_applys, total = get_own_release_apply_by_type(user_id, page_num, release_apply_type='tester')
        elif own_release_apply_status_id == '4':
            release_applys, total = get_own_release_apply_by_type(user_id, page_num, release_apply_type='operator')
        else:
            release_applys = None
            total = 0
    else:
        kwargs = {}
        if title:
            kwargs['title__contains'] = title
        if applier:
            kwargs['applier__username__contains'] = applier
        if tester:
            kwargs['tester_id'] = tester
        if operator:
            kwargs['operator_id'] = operator
        if producter:
            kwargs['producter_id'] = producter
        if application_id:
            kwargs['application_id'] = application_id
        if state:
            kwargs['state'] = state
        if start_planned_time:
            kwargs['planned_at__gte'] = start_planned_time
        if end_planned_time:
            kwargs['planned_at__lte'] = start_planned_time
        if start_formal_at:
            kwargs['formal_at__gte'] = start_formal_at
        if end_formal_at:
            kwargs['formal_at__lte'] = end_formal_at
        release_applys = get_release_apply_by_page(page_num, filter_type='list', **kwargs)
        total = get_release_apply_count(filter_type='list', **kwargs)
    page_count = total / page_size + 1
    release_apply_list = []
    for release_apply in release_applys:
        operator_name = release_apply.operator.username if release_apply.operator else ''
        applier_name = release_apply.applier.username if release_apply.applier else ''
        tester_name = release_apply.tester.username if release_apply.tester else ''
        producter_name = release_apply.producter.username if release_apply.producter else ''
        application_name = release_apply.application.name if release_apply.application else ''
        release_apply_list.append({'release_apply_id': release_apply.id, 'title': release_apply.title or '',
                                   'application_name': application_name,
                                   'state': release_apply.state or '', 'applier_name': applier_name,
                                   'tester_name': tester_name, 'operator_name': operator_name,
                                   'producter_name': producter_name, 'apply_time': str(release_apply.created_at)[:19],
                                   'planned_time': str(release_apply.planned_at)[:19],
                                   'finish_time': str(release_apply.updated_at)[
                                                  :19] if release_apply.updated_at else ''})
    result = {'status': 200, 'data': {'total': total, 'page_num': page_num, 'page_count': page_count,
                                      'release_apply_list': release_apply_list}}
    return json.dumps(result)


@release_apply.route('/update/releaseapplystate/', methods=['GET', 'POST'])
@login_required
def update_releaseapplystate():
    user_id = session["user_data"]["user_id"]
    action_type = request.form.get('action_type')
    reject_reason = request.form.get('reject_reason') or None
    release_apply_id = request.form.get('release_apply_id')
    result = {'status': 1001, 'message': '请求失败'}
    try:
        user_data = User.objects.filter(id=user_id)[0]
    except:
        user_data = None
    try:
        release_apply_data = ReleaseApply.objects.filter(id=release_apply_id)[0]
    except:
        release_apply_data = None
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    now_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    if user_data.id == release_apply_data.applier_id:
        if action_type == RA_USER_ACTION_OPERATOR_CLAIMED:
            release_apply_data.operator_id = user_id
            release_apply_data.save()
        if action_type == RA_USER_ACTION_OPERATOR_EXECUTED:
            release_apply_data.formal_at = now_time
            release_apply_data.save()
        if action_type == RA_USER_ACTION_DEVELOPER_BUILD_CONFIRMED or action_type == RA_USER_ACTION_TEAM_LEADER_BUILD_CONFIRMED:
            git_url = release_apply_data.application.git_url if release_apply_data.application else None
            if git_url:
                bulidqueue_data = BulidQueue(git_url=git_url, release_apply_id=release_apply_id)
                bulidqueue_data.save()
        if state_transfer(user_data, action_type, release_apply_data, reject_reason):
            result = {'status': 200, 'message': '请求成功'}
    return json.dumps(result)

@release_apply.route('/get/taskpad/', methods=['POST'])
def get_taskpad():
    taskpad_type = request.form.get('taskpad_type')
    page_num = int(request.form.get('page_num') or 1)
    kwargs = {}
    if page_num < 1:
        page_num = 1
    if taskpad_type == "own":
        user_id = session.get("user_data").get("user_id")
        kwargs['waitting_confirmer_id'] = user_id
        release_applys = get_release_apply_by_page(page_num, filter_type='taskpad', **kwargs)
        total = get_release_apply_count(filter_type='taskpad', **kwargs)
    else:
        release_applys = get_release_apply_by_page(page_num, filter_type='taskpad', **kwargs)
        total = get_release_apply_count(filter_type='taskpad', **kwargs)
    release_apply_list = []
    page_count = total / page_size + 1
    for data in release_applys:
        producter = data.producter.username if data.producter else ''
        tester = data.tester.username if data.tester else ''
        operator = data.operator.username if data.operator else ''
        application = data.application.name if data.application else ''
        applier = data.applier.username if data.applier else ''
        release_apply_list.append({'release_apply_id': data.id, 'title': data.title,
                                   'release_type': data.release_type, 'producter': producter,
                                   'tester': tester, 'operator': operator, 'state': data.state,
                                   'planned_at': str(data.planned_at)[:19], 'deploy': data.deploy,
                                   'application': application, 'created_at': str(data.created_at)[:19],
                                   'applier': applier})
    result = {'status': 200, 'data': {'total': total, 'page_num': page_num, 'page_count': page_count,
                                      'release_apply_list': release_apply_list}}
    return json.dumps(result)

@release_apply.route('/get/build_log/', methods=['GET'])
def get_build_log():
    release_apply_id = request.args.get('release_apply_id')
    releaseapplybuild_id = request.args.get('releaseapplybuild_id')
    if releaseapplybuild_id:
        try:
            releaseapplybuild_datas = ReleaseapplyBuild.objects.filter(release_apply_id=release_apply_id,
                                                                       id__gt=releaseapplybuild_id)
        except Exception, e:
            result = {'status': 1001, 'message': '数据库异常'}
            return json.dumps(result)
    else:
        try:
            releaseapplybuild_datas = ReleaseapplyBuild.objects.filter(release_apply_id=release_apply_id)
        except Exception, e:
            result = {'status': 1001, 'message': '数据库异常'}
            return json.dumps(result)
    releaseapplybuild_list = []
    is_build = BulidQueue.objects.filter(release_apply_id=release_apply_id).order_by('-id')[0].is_build if BulidQueue.objects.filter(release_apply_id=release_apply_id) else False
    for releaseapplybuild_data in releaseapplybuild_datas:
        releaseapplybuild_list.append(
            {'releaseapplybuild_id': releaseapplybuild_data.id, 'message': releaseapplybuild_data.message,
             'created_at': str(releaseapplybuild_data.created_at)[:19]})
    return json.dumps({'status': 200, 'message': '请求成功', 'data': {'releaseapplybuild_list': releaseapplybuild_list, 'is_build': is_build}})

@release_apply.route('/download/<path:path>')
@login_required
def download_file(path):
    path = 'crons/{0}'.format(path)
    try:
        file = send_file(path)
    except:
        file = json.dumps({'status': 1001, 'message': '文件不存在'})
    return file


