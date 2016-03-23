#!/usr/bin/env python
#encoding=utf-8
from _django_orm import *

org_list = ["系统研发组", "平台架构和基础运维", "基础运维", "平台架构", "交易前台", "交易后台", "前端", "测试", "数据分析"]
org_model_list = [Organization.objects.create(name=org) for org in org_list]

role_list = ["系统管理员", "研发主管", "测试主管", "测试工程师", "研发工程师", "研发经理", "运维主管", "运维工程师", "产品经理"]
role_model_list = [Role.objects.create(name=role) for role in role_list]

user_list = [("叶新强","11212","yexinqiang@meizu.com"), ("孟庆宇","10941","mengqingyu@meizu.com"), ("贾晓辉","10807","jiaxiaohui@meizu.com"),
             ("陈慧","10435","chenhui@meizu.com"), ("李威","10409","liwei2@meizu.com"), ("皇甫泽鹏","10555","huangfuzepeng@meizu.com"),
             ("李万成","10559","liwancheng@meizu.com"), ("刘露","10552","liulu@meizu.com"), ("徐丰甜","10631","xufengtian@meizu.com"),
             ("时磊","11067","shilei2@meizu.com"), ("刘文彬","6616","wenbin@meizu.com"), ("邓琼川","10432","dengqiongchuan@meizu.com"),
             ("毛凌志","10256","maolingzhi@meizu.com"), ("顾超","11039","guchao@meizu.com"), ("胡浩","10429","huhao@meizu.com"),
             ("颜伟伟","10993","yanweiwei@meizu.com"), ("蒋方涛","10181","jiangfangtao@meizu.com"), ("农全","10541","nongquan@meizu.com"),
             ("曹玉齐","8524","caoyuqi@meizu.com"), ("杨华亮","10815","yanghualiang@meizu.com"), ("靳明豪","10277","jinminghao@meizu.com"),
             ("刘许鹏","8315","liuxupeng@meizu.com"), ("夏海虎","10834","xiahaihu@meizu.com"), ("张亚","10683","zhangya@meizu.com"),
             ("孙江敏","10275","sunjiangmin@meizu.com"), ("左培","6688","zuopei@meizu.com"), ("杨少槐","10916","yangshaohuai@meizu.com"),
             ("周楠","10533","zhounan@meizu.com"), ("连源","10427","lianyuan@meizu.com"), ("陈荣荣","10428","chenrongrong@meizu.com"),
             ("郭志强","10430","guozhiqiang@meizu.com"), ("邓文俊","10560","dengwenjun@meizu.com"), ("秦文露","11015","qinwenlu@meizu.com"),
             ("欧苦乐","11007","oukule@meizu.com"), ("胡霄元","11217","huxiaoyuan@meizu.com"), ("王晶城","10660","wangjingcheng@meizu.com"),
             ("段鹏","10657","duanpeng@meizu.com"), ("金晓天","10562","jinxiaotian@meizu.com"), ("徐龙春","10959","xulongchun@meizu.com"),
             ("陈凯伟","10404","chenkaiwei@meizu.com"), ("胡子翅","10278","huzichi@meizu.com"), ("乐尉","11168","lewei@meizu.com"),
             ("潘爱华","10279","panaihua@meizu.com"), ("陈景辉","10698","chenjinghui@meizu.com"), ("陈莹","10659","chenying@meizu.com"),
             ("朱洽成","10937","zhuqiacheng@meizu.com"), ("夏燕飞","10271","xiayanfei@meizu.com"), ("江涛","6431","jiangtao@meizu.com"),
             ("赵祖刚","10545","zhaozugang@meizu.com"), ("韩国星","10544","hanguoxing@meizu.com"), ("吴海永","10870","wuhaiyong@meizu.com"),
             ("陈耕","10776","chengeng@meizu.com"), ("周朋","10707","zhoupeng1@meizu.com"), ("胡威","7161","huwei@meizu.com"),
             ("瞿涛","7339","qutao@meizu.com"), ("王明","11170","wangming@meizu.com"), ("童飞","502104","tongfei@meizu.com")]
user_model_list =  [User.objects.create(username=username,meizu_id=meizu_id,email=email) for username,meizu_id,email in user_list]



