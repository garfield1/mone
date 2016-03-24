#!/usr/bin/env bash
#/opt/reviewboard-2.5.1.1-0/use_reviewboard
rm ../models/db.sqlite3
python ../clear_pyc.py .
python ../models/manage.py syncdb
python init_base.py
python init_worksheet.py
#python -i ./seeds.py
