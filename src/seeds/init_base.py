#!/usr/bin/env python
#encoding=utf-8
from _django_orm import *
# 用户
user_list = [("叶新强","011212","yexinqiang@meizu.com"), ("孟庆宇","010941","mengqingyu@meizu.com"), ("贾晓辉","010807","jiaxiaohui@meizu.com"),
             ("陈慧","010435","chenhui@meizu.com"), ("李威","010409","liwei2@meizu.com"), ("皇甫泽鹏","010555","huangfuzepeng@meizu.com"),
             ("李万成","010559","liwancheng@meizu.com"), ("刘露","010552","liulu@meizu.com"), ("徐丰甜","10631","xufengtian@meizu.com"),
             ("时磊","011067","shilei2@meizu.com"), ("刘文彬","006616","wenbin@meizu.com"), ("邓琼川","010432","dengqiongchuan@meizu.com"),
             ("毛凌志","010256","maolingzhi@meizu.com"), ("顾超","011039","guchao@meizu.com"), ("胡浩","010429","huhao@meizu.com"),
             ("颜伟伟","010993","yanweiwei@meizu.com"), ("蒋方涛","010181","jiangfangtao@meizu.com"), ("农全","010541","nongquan@meizu.com"),
             ("曹玉齐","008524","caoyuqi@meizu.com"), ("杨华亮","010815","yanghualiang@meizu.com"), ("靳明豪","010277","jinminghao@meizu.com"),
             ("刘许鹏","008315","liuxupeng@meizu.com"), ("夏海虎","010834","xiahaihu@meizu.com"), ("张亚","010683","zhangya@meizu.com"),
             ("孙江敏","010275","sunjiangmin@meizu.com"), ("左培","006688","zuopei@meizu.com"), ("杨少槐","010916","yangshaohuai@meizu.com"),
             ("周楠","010533","zhounan@meizu.com"), ("连源","010427","lianyuan@meizu.com"), ("陈荣荣","010428","chenrongrong@meizu.com"),
             ("郭志强","010430","guozhiqiang@meizu.com"), ("邓文俊","010560","dengwenjun@meizu.com"), ("秦文露","011015","qinwenlu@meizu.com"),
             ("欧苦乐","011007","oukule@meizu.com"), ("胡霄元","011217","huxiaoyuan@meizu.com"), ("王晶城","010660","wangjingcheng@meizu.com"),
             ("段鹏","010657","duanpeng@meizu.com"), ("金晓天","010562","jinxiaotian@meizu.com"), ("徐龙春","010959","xulongchun@meizu.com"),
             ("陈凯伟","010404","chenkaiwei@meizu.com"), ("胡子翅","010278","huzichi@meizu.com"), ("乐尉","011168","lewei@meizu.com"),
             ("潘爱华","010279","panaihua@meizu.com"), ("陈景辉","010698","chenjinghui@meizu.com"), ("陈莹","010659","chenying@meizu.com"),
             ("朱洽成","010937","zhuqiacheng@meizu.com"), ("夏燕飞","010271","xiayanfei@meizu.com"), ("江涛","006431","jiangtao@meizu.com"),
             ("赵祖刚","010545","zhaozugang@meizu.com"), ("韩国星","010544","hanguoxing@meizu.com"), ("吴海永","010870","wuhaiyong@meizu.com"),
             ("陈耕","010776","chengeng@meizu.com"), ("周朋","010707","zhoupeng1@meizu.com"), ("胡威","007161","huwei@meizu.com"),
             ("瞿涛","007339","qutao@meizu.com"), ("王明","011170","wangming@meizu.com"), ("童飞","502104","tongfei@meizu.com")]
user_model_list = [User.objects.create(username=username,meizu_id=meizu_id,email=email) for username,meizu_id,email in user_list]
# 组织
org_list = ["系统研发组", "平台架构和基础运维", "基础运维", "平台架构", "交易前台", "交易后台", "前端", "测试", "数据分析"]
org_leader_list = ["毛凌志", "李威", "刘文彬", "李威", "郭志强", "胡子翅", "江涛", "瞿涛", "刘许鹏"]
org_model_list = [Organization(name=org) for org in org_list]
Organization.objects.bulk_create(org_model_list)
Organization.objects.filter(name__in=org_list[1:]).update(parent=Organization.objects.get(name="系统研发组"))
Organization.objects.filter(name__in=["基础运维", "平台架构"]).update(parent=Organization.objects.get(name="平台架构和基础运维"))
for index in range(len(org_list)):
    org = Organization.objects.get(name=org_list[index])
    org.leader = User.objects.get(username=org_leader_list[index])
    org.save()
# 角色
# role_list = ["系统管理员", "研发主管", "测试主管", "测试工程师", "研发工程师", "研发经理", "运维主管", "运维工程师", "产品经理"]
role_list = ["系统管理员", "测试工程师", "研发工程师", "运维工程师", "产品经理"]
role_model_list = [Role(name=role) for role in role_list]
Role.objects.bulk_create(role_model_list)
# 增加系统管理员用户
role_sys = Role.objects.get(name="系统管理员")
user_sys_list = ["皇甫泽鹏", "徐丰甜", "毛凌志"]
for user_sys in user_sys_list:
    role_sys.user.add(User.objects.get(username=user_sys))