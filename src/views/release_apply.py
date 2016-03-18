#!/usr/bin/env python
#encoding=utf-8
from flask import Blueprint
from _release_apply import *
release_apply = Blueprint('release_apply', __name__)

@release_apply.route('/')
def index():
	ll = len(User.objects.all())
	print ll
	return str(ll)

if __name__ == "__main__":
	from _django_orm import *
	from flask import Flask
	app = Flask('my_application')
	app.register_blueprint(release_apply, url_prefix='/release_apply')
	print User.objects.all()
	print "zz"
	app.run(host='0.0.0.0',debug= True)
