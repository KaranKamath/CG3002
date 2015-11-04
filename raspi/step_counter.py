from math import sin, cos, radians
import logging
from enum import Enum

STEP_LENGTH = 36
STEP_THRESHOLD = 5000


class StepCounterState(Enum):
    peak = 0
    non_peak = 1


class StepCounter(object):

    def __init__(self, logger):
        self.log = logger
        self.state = StepCounterState.non_peak
        self.x = 0
        self.y = 0

    def reset_x_and_y(self, x, y):
        self.x = x
        self.y = y

    def update_coords(self, data, heading):
        gyro_y = data[-2]
        if gyro_y > STEP_THRESHOLD:
            if self.state != StepCounterState.peak:
                self.state = StepCounterState.peak
                self.log.info("Step detected")
                self._update_x_and_y(heading)
        else:
            self.state = StepCounterState.non_peak
        return (self.x, self.y)

    def _update_x_and_y(self, heading):
        self.x += int(round(2 * STEP_LENGTH * cos(radians(heading))))
        self.y += int(round(2 * STEP_LENGTH * sin(radians(heading))))


if __name__ == "__main__":
    from db import DB
    from utils import now
    f = DB(logging.getLogger(__name__))
    timestamp = now()
    j = StepCounter(logging.getLogger(__name__))
    while True:
        data = f.fetch_data(sid=0, since=timestamp)
        print "got data"
        timestamp = data[-1][0]
        for d in data:
            print d
            print j.update_coords(d[2], 0)
