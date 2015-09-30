import time
from enum import Enum
from Database.db import DB

THRESHOLD = 6100

def now():
    return int(round(time.time() * 1000))

class StepState(Enum):
    undefined=0
    up=1
    down=2

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
            if self.step_states == StepState.up and step_states[0] == StepState.down:
                return 1
            else:
                return 0

        if self.step_state != StepState.undefined:
            step_states.insert(0, self.step_state)

        count = 0
        for i in range(len(step_states) - 1):
            if step_states[i] == StepState.up and step_states[i+1] == StepState.down:
                count = count + 1

        return count

    def get_step_states(self, average_vals):
        return map(lambda x: get_state_for_num(x), average_vals)
            
    def update_count(self):
        fetched_data = sorted(self.db.fetch(sid=1, since=self.last_ts), key=lambda d: d[0])

        fetched_values = [ (datapoint[2][0] + datapoint[2][1] + datapoint[2][2]) * 1.0 / 3.0 \
                            for datapoint in fetched_data]

        if len(fetched_values) < 1:
            return

        step_states = self.get_step_states(fetched_values)

        self.count = self.count + self.calculate_steps(step_states)

        self.step_state = step_states[-1]

