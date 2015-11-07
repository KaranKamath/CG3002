#!/usr/bin/env python
import logging
import sys
import time
from db import DB
from step_counter import StepCounter
from heading_calculator import HeadingCalculator
from utils import CommonLogger, init_logger, now

from gyro_heading import get_new_heading

LOG_FILENAME = '/home/pi/logs/localizer.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Localizer(object):

    foot_imu_timestamp = now()
    back_imu_timestamp = now()

    def __init__(self, logger):
        self.db = DB(logger)
        self.sc = StepCounter(logger)
        self.hc = HeadingCalculator(logger)
        self.log = logger
        self.gyro_angle = None

    def _get_altitude(self, data):
        return data[0] / 1000.0

    def _get_heading(self, imu_data):
        if self.gyro_angle is None:
            self.gyro_angle = self.hc.get_heading(imu_data)
            return self.gyro_angle
        else:
            heading = self.hc.get_heading(imu_data)
            for data in imu_data:
                a = data[1:4]
                g = data[7:]
                new_angle = get_new_heading(self.gyro_angle, a, g)
                self.log.info(new_angle)
                self.gyro_angle = new_angle
            return heading

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
        # with open('/home/pi/test_data.txt', 'a') as f:
        #     f.write(str(heading) + ', ')
        #     f.write(str(imu_data['foot'][-1][-2]) + ', ')
        #     f.write(str(imu_data['back'][-1][-3]) + '\n')
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
        self.hc.set_map_north(heading)
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
