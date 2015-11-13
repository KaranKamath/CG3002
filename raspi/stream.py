from db import DB
import time

f = DB()
while True:
    print f.fetch_data(sid=0, since=0)[-1]
    print f.fetch_data(sid=1, since=0)[-1]
    time.sleep(1)
