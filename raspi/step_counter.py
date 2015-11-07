from math import sin, cos, radians
import logging
from enum import Enum

STEP_LENGTH = 40
STEP_THRESHOLD = 5000


class StepCounterState(Enum):
    peak = 0
    non_peak = 1


class StepCounter(object):

    def __init__(self, logger):
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
    f = DB(logging.getLogger(__name__))
    j = StepCounter(logging.getLogger(__name__))
    timestamp = now()
    while True:
        data = f.fetch_data(sid=0, since=timestamp)
        print "got data"
        timestamp = data[-1][0]
        for d in data:
            print j.detect_step(d[2], 0)
