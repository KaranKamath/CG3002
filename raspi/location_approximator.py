import time
import numpy as np
from db import DB
from scipy import signal
from math import radians, cos, sin
from utils import now

STEP_LENGTH = 50  # cm
FILTER_ORDER = 3
FS = 5  # Sample Rate
CUTOFF = 2
ACC_MAX_VAL = (32768 * 2) - 1
ACC_NEG_RANGE = 32767
GYRO_MAX = 32768
THRESHOLD_GYRO = 0.03


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


class LocationApproximator(object):

    def __init__(self, x, y, logger):
        self.data_buffer = []
        self.step_count = 0
        self.last_batch_steps = 0
        self.last_batch_headings = []
        self.last_batch_data_buffer = []
        self.heading_buffer = []
        self.x = x
        self.y = y
        self.logger = logger
        self.calibrated = False
        self.threshold = THRESHOLD_GYRO
        self.gyro_x_buffer = []

    def is_calibrated(self):
        return self.calibrated

    def get_step_count(self):
        return self.step_count

    def flush(self):

        # if not self.calibrated:
        #    self.logger.info('Calibrating')
        #    self.logger.info('Data Buffer: %s', self.data_buffer)
        #    self.threshold = sorted(self.data_buffer)[-1]
        #    self.threshold *= 1.1
        #    self.logger.info('Threshold set to: %s', str(self.threshold))
        #    self.copy_and_clear_buffers()
        #    self.calibrated = True
        #    return

        #self.logger.info('\nThreshold: %s\n', self.threshold)
#        self.logger.info('\nFlushing values: %s', self.data_buffer)

        cumulative_buffer = self.last_batch_data_buffer + self.data_buffer

        low_passed_vals = butter_lowpass_filter(
            cumulative_buffer, CUTOFF, FS, FILTER_ORDER)

        low_passed_gyro_x = butter_lowpass_filter(
            self.gyro_x_buffer, 2, FS, FILTER_ORDER)

        peak_indices = signal.argrelextrema(low_passed_gyro_x, np.greater)[0]
        fall_indices = signal.argrelextrema(low_passed_gyro_x, np.less)[0]
        
        peak_vals = [low_passed_gyro_x[x] for x in peak_indices if low_passed_gyro_x[x] > 0.3]
        fall_vals = [low_passed_gyro_x[x] for x in fall_indices if low_passed_gyro_x[x] < -0.3]
        self.logger.info('Gyro Low Passed: %s', low_passed_gyro_x)
        self.logger.info('Gyro X Peaks: %s', len(peak_vals))
        self.logger.info('Gyro X Falls: %s', len(fall_vals))

        # self.logger.info('\nFiltered values: %s', low_passed_vals)

        peak_indices = signal.argrelmax(low_passed_vals)[0]
#        self.logger.info('\nPeak Indices: %s\n', peak_indices)
        self.logger.info([low_passed_vals[x] for x in peak_indices])
        peak_vals = [low_passed_vals[x] for x in peak_indices if low_passed_vals[x] > self.threshold]
        accepted_peaks = [x for x in peak_vals]

        # self.logger.info('Peak values: %s', accepted_peaks)

        if (len(accepted_peaks) * 2) > self.last_batch_steps:
            self.last_batch_steps = (
                len(accepted_peaks) * 2) - self.last_batch_steps
            self.step_count = self.step_count + self.last_batch_steps
        else:
            self.last_batch_steps = 0

        self.copy_and_clear_buffers()
        
        #self.logger.info('Batch Steps Counted: %s', str(self.last_batch_steps))
        # self.logger.info('Total Steps Counted: %s\n', str(self.step_count))

        average_dist = self.last_batch_steps * \
            STEP_LENGTH * 1.0 / len(self.last_batch_headings)
        vectorsX = [average_dist * cos(radians(heading))
                    for heading in self.last_batch_headings]
        vectorsY = [average_dist * sin(radians(heading))
                    for heading in self.last_batch_headings]

#        self.logger.info('Delta X: %s', str(sum(vectorsX)))
#        self.logger.info('Delta Y: %s', str(sum(vectorsY)))

        self.x = self.x + round(int(sum(vectorsX)))
        self.y = self.y + round(int(sum(vectorsY)))
#        self.logger.info('New X: %s', str(self.x))
#        self.logger.info('New Y: %s', str(self.y))

    def copy_and_clear_buffers(self):
        self.last_batch_headings = self.heading_buffer
        self.heading_buffer = []
        self.last_batch_data_buffer = self.data_buffer
        self.data_buffer = []
        self.gyro_x_buffer = []

    def append_to_buffers(self, fetched_data, heading):
        # fetched_data list format: Altimeter, Accelerometer X, Y, Z, Magnetometer X, Y, Z, Gyroscope X, Y, Z
        #fetched_data = sorted(self.db.fetch(sid=1, since=self.last_ts), key=lambda d: d[0])

        #self.logger.info('Data sent to localizer: %s', fetched_data)

        # fetched_values = [(abs(datapoint[1]) + abs(datapoint[2]) + abs(datapoint[3])) * 1.0 / 3.0
        #                  for datapoint in fetched_data]

        fetched_values = [datapoint[-2] for datapoint in fetched_data]
        #self.logger.info('Incoming Processed Data: %s', fetched_values)

        #self.logger.info('Values Rcvd: %s', str(len(fetched_values)))

        if len(fetched_values) < 1:
            print "no value"
            return

        normalized_vals = [v * 1.0 / GYRO_MAX for v in fetched_values]

        self.data_buffer.extend(normalized_vals)
        self.heading_buffer.append(heading)

        fetched_gyro_x_values = [datapoint[-3] for datapoint in fetched_data]
        self.gyro_x_buffer += [v * 1.0 / GYRO_MAX for v in fetched_gyro_x_values]

    def get_position(self):
        return (self.x, self.y)

    def get_new_position(self):
        self.flush()
        return (self.x, self.y)

# if __name__ == "__main__":
#    sc = StepCounter())
#    while True:
#        sc.update_count()
#        print 'Steps (Cumulative): ', sc.get_count()
#        #print 'Current State (0, 1, 2): ', sc.step_state
#        time.sleep(5)
