import time
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from db import DB
from scipy import signal
from math import radians, cos, sin

THRESHOLD_CALLS = 4
STEP_LENGTH = 50 #cm
THRESHOLD_MIN_NORM_VAL = 0.2
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

class LocationApproximator(object):

    def __init__(self):
        self.call_count = 0
        self.data_buffer = []
        self.step_count = 0
        self.last_batch_steps = 0
        self.heading_buffer = []

    def get_step_count(self):
        return self.step_count

    def get_new_position(self, fetched_data, heading, x, y):
        # fetched_data list format: Altimeter, Accelerometer X, Y, Z, Magnetometer X, Y, Z, Gyroscope X, Y, Z
        #fetched_data = sorted(self.db.fetch(sid=1, since=self.last_ts), key=lambda d: d[0])

        fetched_values = [ (datapoint[1] + datapoint[2] + datapoint[3]) * 1.0 / 3.0 \
                            for datapoint in fetched_data]

        if len(fetched_values) < 1:
            print "no value"
            return

        normalized_vals = [ v * 1.0 / ACC_MAX_VAL for v in fetched_values]

        self.data_buffer.append(normalized_vals)
        self.heading_buffer.append(heading)
        self.call_count = self.call_count + 1

        if self.call_count == THRESHOLD_CALLS:
            print "Update Iter. Work to do"
            self.call_count = 0
        else:
            print "Iter ", self.call_count
            return (x, y)

        low_passed_vals = butter_lowpass_filter(self.data_buffer, CUTOFF, FS, FILTER_ORDER)
        peak_indices = signal.argrelmax(low_passed_vals)[0]
        peak_vals = [low_passed_vals[x] for x in peak_indices]
        accepted_peaks = [x for x in peak_vals if x > MIN_NORM_THRESHOLD]

        self.last_batch_steps = len(accepted_peaks)
        self.last_batch_headings = self.heading_buffer

        self.heading_buffer = []
        self.data_buffer = []
        self.count = self.count + len(accepted_peaks)

        average_dist = self.last_batch_steps * STEP_LENGTH * 1.0 / len(last_batch_headings)
        vectorsX = [average_dist * cos(radians(heading)) for heading in self.last_batch_headings]
        vectorsY = [average_dist * sin(radians(heading)) for heading in self.last_batch_headings]

        return ( x + sum(vectorsX), y + sum(vectorsY) )

#if __name__ == "__main__":
#    sc = StepCounter())
#    while True:
#        sc.update_count()
#        print 'Steps (Cumulative): ', sc.get_count()
#        #print 'Current State (0, 1, 2): ', sc.step_state
#        time.sleep(5)
