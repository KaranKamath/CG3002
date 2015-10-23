#!/usr/bin/env python
import argparse
import logging
import sys
import time
from math import atan2, pi
from scipy.signal import medfilt
from db import DB
from location_approximator import LocationApproximator
from utils import CommonLogger, init_logger, now
from vector_ops import dot_3d, cross_3d, normalize_3d
from directions_utils import convert_heading_to_horizontal_axis

LOG_FILENAME = '/home/pi/logs/localizer.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Localizer(object):

    imu_timestamp = now()
    mag_min = [32767, 32767, 32767]
    mag_max = [-32768, -32768, -32768]
    coords_delay = 4
    coords_offset = 0
    median_window = []

    def __init__(self, logger, init_x=0, init_y=0):
        self.db = DB(logger)
        self.log = logger

    def _get_altitude(self, data):
        return data[0] / 1000

    def _get_heading(self, imu_data):
        # a = [-16100, 1300, 500]
        raw_heading = None
        for data in imu_data:
            a = data[1:4]
            m = data[4:7]
            f = [0, 0, -1]
            raw_heading = int(round(self._calculate_raw_heading(a, m, f)))
            raw_heading = self._filter_heading(raw_heading)
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
        self.loc_approx.append_to_buffers(data, heading)
        if self.coords_offset == self.coords_delay:
            self.coords_offset = 0
            return self.loc_approx.get_new_position()
        else:
            self.coords_offset += 1
            return self.loc_approx.get_position()

    def _process_imu(self, imu_data):
        if not imu_data:
            return
        latest_imu_data = imu_data[-1]
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
        self.log.info('Waiting for inital x, y and map north...')
        timestamp, x, y, heading, alt = self.db.fetch_location(True)
        self.map_north = heading
        self.init_x = x
        self.init_y = y
        self.log.info('Set initial [x, y] to [%s, %s]', x, y)
        self.log.info('Set map north to %s', heading)

    def start(self):
        self._initalize_location()
        self.loc_approx = LocationApproximator(self.init_x,
                                               self.init_y,
                                               self.log)
        while True:
            data = self._get_latest_imu_readings()
            self._process_imu(data)
            time.sleep(0.2)


localizer = Localizer(logger)
localizer.start()
