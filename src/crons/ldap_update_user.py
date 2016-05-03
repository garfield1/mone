#coding=utf-8
import sys
sys.path.append('..')
import ldap
import ldap.dn
import os
os.environ['DJANGO_SETTING_MODULE']='models.zz.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "models.zz.settings")
from models.mone.models import User

LDAP_developer_BASE_DN = 'OU=系统开发组,OU=线上销售,OU=销售事业二部,OU=营销中心,OU=魅族科技,DC=meizu,DC=com'
LDAP_producter_BASE_DN = 'OU=产品经理组,OU=线上销售,OU=销售事业二部,OU=营销中心,OU=魅族科技,DC=meizu,DC=com'
LDAP_HOST = '172.16.1.110'
MGR_CRED = 'hfsystem'
MGR_PASSWD = 'BU3V-9G79-1AEY-J0SX'

class LdapMgmt():
    def __init__(self, ldap_host=None, mgr_cred=None,mgr_passwd=None):
        if not ldap_host:
            ldap_host = LDAP_HOST
        if not mgr_cred:
            mgr_cred = MGR_CRED
        if not mgr_passwd:
            mgr_passwd = MGR_PASSWD
        self.ldapconn = ldap.open(ldap_host)
        self.ldapconn.simple_bind(mgr_cred, mgr_passwd)

    def get_ldap_data(self, base_dn,filterstr='(objectClass=*)',attrib=None,scope=ldap.SCOPE_SUBTREE):
        s = self.ldapconn.search_s(base_dn, scope,filterstr,attrlist=attrib)
        return s

def check_user(email):
    user_datas = User.objects.filter(email=email)
    if user_datas:
        return user_datas[0]
    else:
        return False

def add_user(**kwargs):
    user_data = User(**kwargs)
    user_data.save()
    return user_data

def update_user(user_type):
    '''
    当user_type 为 developer： 同步开发
    当user_type 为 producter： 同步产品
    :param user_type:
    :return:
    '''
    l = LdapMgmt()
    if user_type == "developer":
        LDAP_BASE_DN = LDAP_developer_BASE_DN
    elif user_type == "producter":
        LDAP_BASE_DN = LDAP_producter_BASE_DN
    try:
        all_user_data = l.get_ldap_data(LDAP_BASE_DN)
    except:
        print "服务器繁忙，请稍后再试"
        return "failure"
    for data in all_user_data:
        attrib_dict1 = data[1]
        email = attrib_dict1.get("mail")[0] if attrib_dict1.get("mail") else None
        if email:
            user_data = check_user(email)
            if not user_data:
                meizu_id = attrib_dict1.get("employeeID")[0] if attrib_dict1.get("employeeID") else None
                username = attrib_dict1.get("displayName")[0] if attrib_dict1.get("displayName") else None
                if add_user(username=username, email=email, meizu_id=meizu_id):
                    print "success: %s" % email
                else:
                    print "failure: %s" % email


if __name__ == "__main__":
    if 2 == len(sys.argv):
        print "参数检查正确"
    else:
        print "输入需要同步的用户类型"
        sys.exit(0)
    user_type = sys.argv[1]
    update_user(user_type)







