#!/usr/bin/env python
import argparse
import logging
import sys
import time
from math import atan2, pi
from logging.handlers import TimedRotatingFileHandler

from db import DB
from location_approximator import LocationApproximator
from utils import CommonLogger
from vector_ops import dot_3d, cross_3d, normalize_3d

LOG_FILENAME = '/home/pi/logs/localizer.log'
LOG_LEVEL = logging.INFO

p = argparse.ArgumentParser(description="Localizer service")
p.add_argument("-l", "--log", help="log file (default: " + LOG_FILENAME + ")")
args = p.parse_args()
if args.log:
    LOG_FILENAME = args.log

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
h = TimedRotatingFileHandler(LOG_FILENAME, when='H', backupCount=3)
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logger.addHandler(h)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Localizer():

    device_timestamps = {
        0: 0,
        1: 0
    }
    mag_min = [32767, 32767, 32767]
    mag_max = [-32768, -32768, -32768]
    coords_delay = 4
    coords_offset = 0

    def __init__(self, logger, init_x=0, init_y=0):
        self.db = DB('/home/pi/db/uart.db')
        # self.db = DB('uart.db')
        self.loc_approx = LocationApproximator(init_x, init_y, logger)
        self.log = logger
        timestamp = int(round(time.time() * 1000))
        for device in self.device_timestamps:
            self.device_timestamps[device] = timestamp

    def _get_data(self, sid, timestamp):
        return self.db.fetch_data(sid=sid, since=timestamp,
                                  auto_delete=True)

    def _get_altitude(self, data):
        return data[0] / 1000

    def _get_heading(self, data):
        a = data[1:4]
        m = data[4:7]
        f = [0, 0, 1]

        m = (m[0] - (self.mag_min[0] + self.mag_max[0]) / 2,
             m[1] - (self.mag_min[1] + self.mag_max[1]) / 2,
             m[2] - (self.mag_min[2] + self.mag_max[2]) / 2)
        e = normalize_3d(cross_3d(m, a))
        n = normalize_3d(cross_3d(a, e))
        heading = atan2(dot_3d(e, f),
                        dot_3d(n, f)) * 180 / pi
        return (heading + 360) if heading < 0 else heading

    def _get_coords(self, data, heading):
        self.loc_approx.append_to_buffers(data, heading)
        if self.coords_offset == self.coords_delay:
            self.coords_offset = 0
            return self.loc_approx.get_new_position()
        else:
            self.coords_offset += 1
            return self.loc_approx.get_position()

    def _get_latest_readings(self):
        latest_data = {}
        for (k, v) in self.device_timestamps.items():
            data = self._get_data(k, v)
            if data:
                self.device_timestamps[k] = data[-1][0]
                latest_data[k] = [d[2] for d in data]
            else:
                latest_data[k] = None
        return latest_data

    def _process_imu(self, imu_data):
        if imu_data:
            latest_imu_data = imu_data[-1]
            altitude = self._get_altitude(latest_imu_data)
            heading = self._get_heading(latest_imu_data)
            x, y = self._get_coords(imu_data, heading)
            self.db.insert_location(x, y, heading, altitude)

    def start(self):
        self.log.info('Starting up...')
        while True:
            data = self._get_latest_readings()
            self.log.info('Got data: %s', str(data))
            self._process_imu(data[0])
            time.sleep(0.5)


generator = Localizer(logger)
generator.start()
