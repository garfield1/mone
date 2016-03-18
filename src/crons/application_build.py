#!/usr/bin/env python
#encoding=utf-8
"""
jenkins后台构建轮询deamon
找出数据库中等待构建和正在构建的任务，进行执行，执行完的更新数据库中的状态
"""
from _django_orm import *
AB_STATE_WAITTING_BUILD = "等待构建"
AB_STATE_BUILDING = "构建中"
AB_STATE_BUILDED = "构建完成"



