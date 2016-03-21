# flask_with_django_orm_demo
安装说明：
依赖
pip install gittle
yum groupinstall "Development Tools"

pip install flask flask-login requests Django==1.6.11 eralchemy python-ldap
pip install gitpython
使用bitnami reviewboard简化安装环境
https://bitnami.com/stack/reviewboard/installer
安装完后进入/opt/bitnami-reviewboard/下执行./use_reviewboard加载环境

交互式测试

python  -i ./seeds.py

Django版本使用1.6.11,bitnami内置了各种mysql包驱动等
visit:
http://10.2.81.207:5000/admin/
pip uninstall Django
pip install Django==1.6.11

sqlitespy sqlite view tools

http://www.yunqa.de/delphi/products/sqlitespy/index

建议开发环境

vim + xshell连接远程centos6.x
使用samba映射远程开发目录，使用sqlitespy在windows下查看数据库数据


erd生成
https://github.com/Alexis-benoist/eralchemy

centos install oracle jdk with remove embedded openjdk
http://javawind.net/p144

Apache Maven 3.3.9 (bb52d8502b132ec0a5a3f4c09453c07478323dc5; 2015-11-11T00:41:47+08:00)
Maven home: /export/program/apache-maven-3.3.9
Java version: 1.7.0_79, vendor: Oracle Corporation
Java home: /export/program/jdk1.7.0_79/jre
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "2.6.32-573.18.1.el6.x86_64", arch: "amd64", family: "unix"


/etc/profile:
export JAVA_HOME=/export/program/jdk1.7.0_79
export CLASS_PATH=$JAVA_HOME/lib
export M2_HOME=/export/program/apache-maven-3.3.9
export PATH=$JAVA_HOME/bin:$PATH:$M2_HOME/bin
export LANG='en_US.UTF-8'

