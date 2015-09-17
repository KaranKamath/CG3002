import db_setup_clean
import db_utils

db_setup_clean.reset_db('test')
db_utils.set_db('test')

fetched = db_utils.fetch()

assert fetched == [], 'There should be nothing to fetch! Found: ' + str(fetched)
print "PASS"

sid = 2
sdata = [2, 334, 54, 9495]

db_utils.insert(sid, sdata)

fetched = db_utils.fetch()

assert len(fetched) == 1, 'There should be only one row'
print "PASS"
assert fetched[0] == [sid, sdata]
print "PASS"

import time
ts1 = int(round(time.time() * 1000))

db_utils.insert(1, sdata)

fetched = db_utils.fetch()
assert len(fetched) == 2
print 'PASS'

fetched = db_utils.fetch(sid=2)
assert len(fetched) == 1
print 'PASS'
assert fetched[0] == [2, sdata], sdata
print 'PASS'

fetched = db_utils.fetch(since=ts1)
assert len(fetched) == 1
print 'PASS'
assert fetched[0] == [1, sdata], sdata
print 'PASS'
