import time
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from db import DB

THRESHOLD = 6100

plt.axis([0, 1000, 0, 1])
plt.ion()
plt.show()
count = 0


def now():
    return int(round(time.time() * 1000))


class StepState(Enum):
    undefined = 0
    up = 1
    down = 2


def get_state_for_num(num):
    if num > THRESHOLD:
        return StepState.up
    else:
        return StepState.down


class StepCounter(object):

    def __init__(self, l_ts=now()):
        self.last_ts = l_ts
        self.count = 0
        self.db = DB()
        self.step_state = StepState.undefined

    def get_count(self):
        return self.count

    def calculate_steps(self, step_states):

        if len(step_states) == 1:
            if self.step_states == StepState.up and \
                    step_states[0] == StepState.down:
                return 1
            else:
                return 0

        if self.step_state != StepState.undefined:
            step_states.insert(0, self.step_state)

        count = 0
        for i in range(len(step_states) - 1):
            if step_states[i] == StepState.up and \
                    step_states[i + 1] == StepState.down:
                count = count + 1

        return count

    def get_step_states(self, average_vals):
        return map(lambda x: get_state_for_num(x), average_vals)
 
    def movingaverage(self, interval, window_size):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window)

    def update_count(self):
        fetched_data = sorted(self.db.fetch(sid=1, since=self.last_ts), key=lambda d: d[0])

        fetched_values = [ (datapoint[2][0] + datapoint[2][1] + datapoint[2][2]) * 1.0 / 3.0 \
                            for datapoint in fetched_data]

        if len(fetched_values) < 1:
            print "no value"
            return

        for i in fetched_values:
            plt.scatter(i, count)
            plt.draw()
            count += 1
            time.sleep(0.05)

        fetched_values = self.movingaverage(fetched_values, 3)
        fetched_values = fetched_values[2:-2]
        print fetched_values

        self.last_ts = fetched_data[-1][0]

        step_states = self.get_step_states(fetched_values)

        self.count = self.count + self.calculate_steps(step_states)

        self.step_state = step_states[-1]

if __name__ == "__main__":
    sc = StepCounter(l_ts=0)
    while True:
        sc.update_count()
        print 'Steps (Cumulative): ', sc.get_count()
        print 'Current State (0, 1, 2): ', sc.step_state
        time.sleep(5)
