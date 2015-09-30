import time
from enum import Enum
from Database.db import DB

THRESHOLD = 6100

def now():
    return int(round(time.time() * 1000))

class StepState(Enum):
    undefined=1
    up=2
    down=3

class StepCounter(object):

    def __init__(self, l_ts=now()):
        self.last_ts = l_ts
        self.count = 0
        self.db = DB()
        self.step_state = StepState.undefined

    def get_count(self):
        return self.count

    def update_count(self):
        fetched_data = self.db.fetch(sid=1, since=self.last_ts)
        print fetched_data

sc = StepCounter()
sc.update_count()
