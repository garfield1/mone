# coding=utf-8
from functools import wraps
from flask import redirect, url_for, session

__author__ = 'huangfuzepeng'

def check_access(paras):
    '''
    check_access
    test_dic = [{"role_id": 2, "role_name": "运维"}]
    :param func:
    :return:
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            if not isinstance(paras, list):
                raise ValueError("装饰器传参错误")
            roles_set = set()
            for para in paras:
                role_id = para.get('role_id')
                roles_set.add(role_id)
            own_roles_list = session.get('own_roles_list')
            own_roles_set = set()
            for own_role in own_roles_list:
                own_roles_set.add(own_role)
            if not roles_set & own_roles_set:
                return redirect(url_for('user.index'))
            return func(*args, **kw)
        return wrapper
    return decorator




