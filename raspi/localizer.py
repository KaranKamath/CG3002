#!/usr/bin/env python
import argparse
import logging
import sys
import time
import numpy as np
from pykalman import KalmanFilter
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

    foot_imu_timestamp = now()
    back_imu_timestamp = now()
    mag_min = [32767, 32767, 32767]
    mag_max = [-32768, -32768, -32768]
    coords_delay = 4
    coords_offset = 0
    median_window = []
    prev_heading = None
    heading_offset = 0
    kalman_heading_mean = np.zeros((1,1))
    kalman_heading_covariance = np.zeros((1,1))
    kf = KalmanFilter(n_dim_state=1, n_dim_obs=1)

    def __init__(self, logger):
        self.db = DB(logger)
        self.sc = StepCounter(logger)
        self.log = logger

    def _get_altitude(self, data):
        return data[0] / 1000.0

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
        raw_heading = None
        for data in imu_data:
            a = data[1:4]
            m = data[4:7]
            f = [0, 0, -1]
            raw_heading = int(round(self._calculate_raw_heading(a, m, f)))

            self.kalman_heading_mean, self.kalman_heading_covariance = kf.filter_update(self.kalman_heading_mean, self.kalman_heading_covariance, raw_heading)
            raw_heading = self.kalman_heading_mean[0]
            raw_heading = self._filter_heading(raw_heading)
            # self._is_interference(data[INDEX_GYRO_X], raw_heading)
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

    def _process_imu(self, imu_data):
        if not imu_data:
            return
        altitude = self._get_altitude(imu_data['back'][-1])
        heading = self._get_heading(imu_data['back'])
        x, y = self._get_coords(imu_data['foot'], heading)
        self.db.insert_location(x, y, heading, altitude)
        self.log.info('Updated location to %s, %s, %s, %s',
                      x, y, heading, altitude)

    def _get_latest_imu_readings(self):
        foot_data = self.db.fetch_data(sid=0, since=self.foot_imu_timestamp)
        self.foot_imu_timestamp = foot_data[-1][0]
        back_data = self.db.fetch_data(sid=1, since=self.back_imu_timestamp)
        self.back_imu_timestamp = back_data[-1][0]
        return {
            'foot': [d[2] for d in foot_data],
            'back': [d[2] for d in back_data]
        }

    def _initalize_location(self):
        timestamp, x, y, heading, alt = self.db.fetch_location()
        self.map_north = heading
        self.sc.reset_x_and_y(x, y)
        self.db.clear_reset()
        self.log.info('Set [x, y] to [%s, %s]', x, y)
        self.log.info('Set map north to %s', heading)

    def start(self):
        self.log.info('Waiting for inital x, y and map north...')
        self._initalize_location()
        while True:
            if self.db.is_reset():
                self._initalize_location()
            data = self._get_latest_imu_readings()
            self._process_imu(data)
            time.sleep(0.2)


localizer = Localizer(logger)
localizer.start()
