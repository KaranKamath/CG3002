import sys

lts = sys.argv[1]

from database.db import DB

print (db.fetch(sid=1, since=lts))[2][0]
