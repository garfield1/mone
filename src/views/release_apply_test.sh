#!/usr/bin/sh bash
rm ../models/db.sqlite3
python ../models/manage.py syncdb
python -i ./_release_apply.py

