import time
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from db import DB
from scipy import signal

MIN_THRESHOLD = 0.2
FILTER_ORDER = 5
FS = 10 #Sample Rate
CUTOFF = 1
ACC_MAX_VAL = 32768

plt.axis([0, 1000, 0, 1])
plt.ion()
plt.show()
count = 0


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
  
def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def now():
    return int(round(time.time() * 1000))

class StepCounter(object):

    def __init__(self, l_ts=now()):
        self.last_ts = l_ts
        self.count = 0
        self.db = DB()

    def get_count(self):
        return self.count

    def update_count(self):
        fetched_data = sorted(self.db.fetch(sid=1, since=self.last_ts), key=lambda d: d[0])

        fetched_values = [ (datapoint[2][0] + datapoint[2][1] + datapoint[2][2]) * 1.0 / 3.0 \
                            for datapoint in fetched_data]

        if len(fetched_values) < 1:
            print "no value"
            return

        normalized_vals = [ v * 1.0 / ACC_MAX_VAL for v in fetched_values]
        low_passed_vals = butter_lowpass_filter(normalized_vals, CUTOFF, FS, FILTER_ORDER)
        peak_indices = signal.argrelmax(low_passed_vals)[0]
        peak_vals = [low_passed_vals[x] for x in peak_indices]
        accepted_peaks = [x for x in peak_vals if x > MIN_THRESHOLD]

        self.last_ts = fetched_data[-1][0]

        self.count = self.count + len(accepted_peaks)

if __name__ == "__main__":
    sc = StepCounter(l_ts=0)
    while True:
        sc.update_count()
        print 'Steps (Cumulative): ', sc.get_count()
        #print 'Current State (0, 1, 2): ', sc.step_state
        time.sleep(5)
