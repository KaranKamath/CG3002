import logging
import time
from db import DB

foo = DB(logging.getLogger(__name__))
timestamp = int(time.time())
mag_min = [32767, 32767, 32767]
mag_max = [-32768, -32768, -32768]
while True:
    foot_data = foo.fetch_data(sid=1, since=self.foot_imu_timestamp)
    timestamp = foo_data[-1][0]
    foo_data = [d[2] for d in foo_data]
    for data in foo_data:
        m = data[4:7]
        for i in range(3):
            if m[i] > mag_max[i]:
                mag_max[i] = m[i]
            if m[i] < mag_min[i]:
                mag_min[i] = m[i]
    print "MAX: ", mag_max
    print "MIN: ", mag_min
