import logging
from enum import Enum

STEP_LENGTH = 40
STEP_THRESHOLD = 2000


class StepCounterState(Enum):
    peak = 0
    non_peak = 1


class StepCounter(object):

    def __init__(self, logger=logging.getLogger(__name__)):
        self.log = logger
        self.state = StepCounterState.non_peak

    def detect_step(self, data):
        gyro_y = data[-2]
        if gyro_y > STEP_THRESHOLD:
            if self.state != StepCounterState.peak:
                self.state = StepCounterState.peak
                self.log.info("Step detected")
                return True
        else:
            self.state = StepCounterState.non_peak
        return False


if __name__ == "__main__":
    from db import DB
    from utils import now
    db = DB(db_name='uart.db')
    obj = StepCounter()
    timestamp = now()
    while True:
        data = db.fetch_data(sid=0, since=timestamp)
        timestamp = data[-1][0]
        for d in data:
            print obj.detect_step(d[2])
