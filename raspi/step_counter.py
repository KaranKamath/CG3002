from math import sin, cos, radians
import logging

STEP_LENGTH = 36


class StepCounter(object):

    STEP_THRESHOLD = 5000
    TURN_THRESHOLD = 1000

    def __init__(self, x, y, logger):
        self.x = x
        self.y = y
        self.log = logger
        self.state = 0
        self.step_count = 0
        self.prev_val = 0
        self.turn_history = []

    def did_turn(self, gyroX):
        if abs(gyroX) > TURN_THRESHOLD:
            self.log.info("Turn Detected")
            self.turn_history.append((self.x, self.y))

        if len(self.turn_history) > 5:
            self.turn_history = self.turn_history[-5:]

    def update_coords(self, data, heading):
        if data[-2] > self.STEP_THRESHOLD:
            if self.state != 1:
                self.state = 1
                self.log.info("Step detected")
                self._update_x_and_y(heading)
                return (self.x, self.y)

        else:
            if self.state != -1:
                self.state = -1
        return (self.x, self.y)

    def _update_x_and_y(self, heading):
        self.x += int(round(2 * STEP_LENGTH * cos(radians(heading))))
        self.y += int(round(2 * STEP_LENGTH * sin(radians(heading))))


if __name__ == "__main__":
    from db import DB
    from utils import now
    f = DB(logging.getLogger(__name__))
    timestamp = now()
    j = StepCounter(0, 0)
    while True:
        data = f.fetch_data(sid=0, since=timestamp)
        print "got data"
        timestamp = data[-1][0]
        for d in data:
            print d
            print j.update_coords(d[2], 0)
