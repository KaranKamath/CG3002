import sys
import time
from db import DB

sid = sys.argv[1]
lts = sys.argv[2] if len(sys.argv) >= 3 else int(round(time.time() * 1000))
foo = DB()

for entry in foo.fetch(sid=sid, since=lts):
    print entry[2]
