# coding=utf-8
import re
import shutil
import gevent
import time
import subprocess
from _django_orm import *

def get_file_name(git_url):
    '''
	获取文件名
	:param git_url:
	:return:
	'''
    file_path = git_url.split('/')[-1]
    p = re.compile(r'([\s\S]*).git')
    file_name = p.findall(file_path)
    return file_name[0]

def save_build_message(release_apply_id, message, created_at):
    applicationbuild_data = ReleaseapplyBuild(release_apply_id=release_apply_id, message=message, created_at=created_at)
    applicationbuild_data.save()

def log(content="debug", path='/tmp/test.log'):
    # logging.basicConfig(level=logging.DEBUG,
    # format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    #                     datefmt='%a, %d %b %Y %H:%M:%S',
    #                     filename=path,
    #                     filemode='w')
    # logging.info(content)
    fsock = open(path, 'a')
    now = time.strftime("%Y-%m-%d %H %M %S", time.localtime())
    result = '%s--%s\n' % (now, content)
    fsock.write(result)
    fsock.close()
    return result

def build(git_url, release_apply_id, formal_mvn_command):
    '''
	构建
	:param git_url:
	:return:
	'''
    file_name = get_file_name(git_url)
    command_rm = 'rm -rf {0}'.format(file_name)
    command_git = 'git clone {0}'.format(git_url)
    if os.path.exists(file_name):
        os.system(command_rm)
    os.system(command_git)
    os.chdir(file_name)
    ps = subprocess.Popen(formal_mvn_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    while True:
        data = ps.stdout.readline()
        if ps.poll() is not None:
            break
        else:
            ISOTIMEFORMAT = '%Y-%m-%d %X'
            now_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
            save_build_message(release_apply_id, data, now_time)

def save_mvn_file(application_id, Application_file_path, application_name):
    '''
    保存文件，备份
    :param Application_file_path:
    :param application_name:
    :return:
    '''
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    now_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    suffix = os.path.splitext(Application_file_path)[1]
    file_name = str(now_time) + suffix
    save_file_path = application_name + '/' + file_name
    try:
        build_file_data = build_file(application_id=application_id, file_path=save_file_path, file_name=file_name, created_at=now_time)
        build_file_data.save()
        if not os.path.exists(application_name):
            os.mkdir(application_name)
        shutil.copy(Application_file_path, save_file_path)
        return True
    except Exception, e:
        print e
        return False

def main():
    for build_queue in BulidQueue.objects.filter(is_build=False):
        releaseapplybuilds = ReleaseapplyBuild.objects.filter(release_apply_id=build_queue.release_apply_id)
        releaseapplybuilds.delete()
        try:
            formal_mvn_command = "mvn "
            last_mvn_command = build_queue.release_apply.application.formal_mvn
            if last_mvn_command:
                mvn_command_list = last_mvn_command.split(' ')
                for data in mvn_command_list:
                    formal_mvn_command = formal_mvn_command + "'" + data + "'" + " "
            else:
                formal_mvn_command = 'mvn clean package'
        except Exception, e:
            formal_mvn_command = 'mvn clean package'
        save_mvn_file(build_queue.release_apply.application_id, build_queue.release_apply.application.file_path, build_queue.release_apply.application.name)
        # g1 = gevent.spawn(build, build_queue.git_url, build_queue.release_apply_id, formal_mvn_command)
        # g1.join()
        build_queue.start_build = True
        build_queue.save()
        build(build_queue.git_url, build_queue.release_apply_id, formal_mvn_command)
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        updated_at = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
        release_apply_data = build_queue.release_apply
        release_apply_data.updated_at = updated_at
        release_apply_data.save()
        build_queue.is_build = True
        build_queue.end_build = True
        build_queue.save()

if __name__ == "__main__":
    main()
