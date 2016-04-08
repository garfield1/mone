# coding=utf-8
import re
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

def build(git_url, release_apply_id):
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
    command_bulit = 'mvn clean package'
    log(command_bulit)
    ps = subprocess.Popen(command_bulit, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    log(ps)
    while True:
        data = ps.stdout.readline()
        log(data)
        if ps.poll() is not None:
            break
        else:
            ISOTIMEFORMAT = '%Y-%m-%d %X'
            now_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
            save_build_message(release_apply_id, data, now_time)

def main():
    for build_queue in BulidQueue.objects.filter(is_build=False):
        releaseapplybuilds = ReleaseapplyBuild.objects.filter(release_apply_id=build_queue.release_apply_id)
        releaseapplybuilds.delete()
        g1 = gevent.spawn(build, build_queue.git_url, build_queue.release_apply_id)
        g1.join()
        build_queue.is_build = True
        build_queue.save()


if __name__ == "__main__":
    main()
