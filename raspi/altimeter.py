from db import DB
import time
import sys

average = 0


def calibrate(db):
    global average
    counter = 100
    current = int(round(time.time()*1000))
    while counter > 0:
        data = db.fetch(since=current, sid=0)
        if data:
            current = data[-1][0]
            data = data[-1][2][0]
            average += data
            counter -= 1
    average /= 100


foo = DB()
calibrate(foo)
current = int(round(time.time()*1000))
while True:
    data = foo.fetch(since=current, sid=0)
    if data:
        data = data[-1]
        altitude = (data[2][0] - average) / 1000.0
        sys.stdout.flush()
        sys.stdout.write("Altitude: %s m   \r" % (altitude,))
        current = data[0]
