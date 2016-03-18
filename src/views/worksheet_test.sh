#!/usr/bin/sh bash
rm ../models/db.sqlite3
python ../clear_pyc.py .
python ../models/manage.py syncdb
python -i ./_worksheet.py

