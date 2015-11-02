#!/usr/bin/env python
import argparse
import logging
import sys
import time
from math import atan2, pi
from scipy.signal import medfilt
from db import DB
from location_approximator import LocationApproximator
from step_counter import StepCounter
from utils import CommonLogger, init_logger, now
from vector_ops import dot_3d, cross_3d, normalize_3d
from directions_utils import convert_heading_to_horizontal_axis

LOG_FILENAME = '/home/pi/logs/localizer.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)

THRESHOLD_TURN = 1500
THRESHOLD_HEADING = 20
INDEX_GYRO_X = -3
 
class Localizer(object):

    imu_timestamp = now()
    mag_min = [32767, 32767, 32767]
    mag_max = [-32768, -32768, -32768]
    coords_delay = 4
    coords_offset = 0
    median_window = []
    prev_heading = None
    heading_offset = 0

    def __init__(self, logger):
        self.db = DB(logger)
        self.sc = StepCounter(logger)
        self.log = logger

    def _get_altitude(self, data):
        return data[0] / 1000

    def _get_heading_delta(self, new_heading):
        if self.prev_heading is None:
            return 0
        else:
            return abs(new_heading - self.prev_heading)

    def _is_interference(self, gyroX, new_heading):
        if abs(gyroX) < THRESHOLD_TURN and \
            self._get_heading_delta(new_heading) > THRESHOLD_HEADING:
           
            self.log.info("Interference trigger: gyro:%s heading_delta: %s", 
                abs(gyroX), self._get_heading_delta(new_heading)) 
            self.log.info("Interference Start / Stop")
            return False

        return True

    def _get_heading(self, imu_data):
        # a = [-16100, 1300, 500]
        raw_heading = None
        for data in imu_data:
            a = data[1:4]
            m = data[4:7]
            f = [0, 0, -1]
            raw_heading = int(round(self._calculate_raw_heading(a, m, f)))
            raw_heading = self._filter_heading(raw_heading)
            self._is_interference(data[INDEX_GYRO_X], raw_heading)
            self.prev_heading = raw_heading

        return convert_heading_to_horizontal_axis(raw_heading,
                                                  self.map_north)

    def _calculate_raw_heading(self, a, m, f):
        m = (m[0] - (self.mag_min[0] + self.mag_max[0]) / 2,
             m[1] - (self.mag_min[1] + self.mag_max[1]) / 2,
             m[2] - (self.mag_min[2] + self.mag_max[2]) / 2)
        e = normalize_3d(cross_3d(m, a))
        n = normalize_3d(cross_3d(a, e))
        heading = atan2(dot_3d(e, f), dot_3d(n, f)) * 180 / pi
        return (heading + 360) if heading < 0 else heading

    def _filter_heading(self, heading):
        self.median_window.append(heading)
        if len(self.median_window) <= 5:
            return heading
        self.median_window = self.median_window[1:]
        filtered_heading = medfilt(self.median_window, 5)[2]
        return filtered_heading

    def _get_coords(self, data, heading):
        x, y = None, None
        for d in data:
            x, y = self.sc.update_coords(d, heading)
        return x, y
        # self.loc_approx.append_to_buffers(data, heading)
        # if self.coords_offset == self.coords_delay:
        #     self.coords_offset = 0
        #     return self.loc_approx.get_new_position()
        # else:
        #     self.coords_offset += 1
        #     return self.loc_approx.get_position()

    def _process_imu(self, imu_data):
        if not imu_data:
            return
        latest_imu_data = imu_data[-1]
        print latest_imu_data[-3]
        altitude = self._get_altitude(latest_imu_data)
        heading = self._get_heading(imu_data)
        x, y = self._get_coords(imu_data, heading)
        self.db.insert_location(x, y, heading, altitude)
        self.log.info('Updated location to %s, %s, %s, %s',
                      x, y, heading, altitude)

    def _get_latest_imu_readings(self):
        data = self.db.fetch_data(sid=0, since=self.imu_timestamp)
        self.imu_timestamp = data[-1][0]
        return [d[2] for d in data]

    def _initalize_location(self):
        timestamp, x, y, heading, alt, is_reset = self.db.fetch_location(True)
        if is_reset:
            self.map_north = heading
            self.sc.reset_x_and_y(x, y)
            self.log.info('Set [x, y] to [%s, %s]', x, y)
            self.log.info('Set map north to %s', heading)

    def start(self):
        self.log.info('Waiting for inital x, y and map north...')
        while True:
            self._initalize_location()
            data = self._get_latest_imu_readings()
            self._process_imu(data)
            time.sleep(0.2)


localizer = Localizer(logger)
localizer.start()
