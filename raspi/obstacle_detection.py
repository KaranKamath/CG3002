#!/usr/bin/env python
import time
import logging
import sys
from scipy.signal import medfilt
from db import DB
from utils import CommonLogger, init_logger, now
from motor_driver import MotorDriver

LOG_FILENAME = '/home/pi/logs/obstacle_detector.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)

DELTA_TIME = 1  # 1 second

MEDIAN_WINDOW = 3
MAX_SENSOR_VAL = 301
THRESHOLD_USOUND_HIGH = 70


class ObstacleDetector(object):

    def __init__(self, logger):
        self.past_vals = []
        self.db = DB(logger)
        self.logger = logger
        self.motor_driver = MotorDriver()
        self.logger.info('Starting up obstacle detector...')

    def get_current_data(self):
        one_second_ago = now() - DELTA_TIME
        fetched_data = self.db.fetch_data(sid=1, since=one_second_ago)

        if not fetched_data:
            self.logger.info('No data fetched by obstacle detector')
            return []

        fetched_data = sorted(fetched_data, key=lambda x: x[0])

        latest_data = [x[2] for x in fetched_data][-1]

        # clean up 0s
        for i in range(len(latest_data)):
            if latest_data[i] == 0:
                latest_data[i] = MAX_SENSOR_VAL

        self.past_vals.append(latest_data)

        if len(self.past_vals) > MEDIAN_WINDOW:
            self.past_vals = self.past_vals[(-1 * MEDIAN_WINDOW):]
        else:
            self.logger.info(
                'Not enough data to filter, returning raw: %s', latest_data)
            return latest_data

        self.logger.info('Selecting latest data: %s', latest_data)

        filtered_vals = []
        filtered_vals.append(latest_data[0])
        # filtered_vals.append(medfilt(
        #    [x[0] for x in self.past_vals], MEDIAN_WINDOW)[MEDIAN_WINDOW / 2])
        filtered_vals.append(medfilt(
            [x[1] for x in self.past_vals], MEDIAN_WINDOW)[MEDIAN_WINDOW / 2])
        filtered_vals.append(medfilt(
            [x[2] for x in self.past_vals], MEDIAN_WINDOW)[MEDIAN_WINDOW / 2])
        filtered_vals.append(latest_data[3])
        filtered_vals.append(latest_data[4])
        # filtered_vals.append(medfilt(
        #    [x[3] for x in self.past_vals], MEDIAN_WINDOW)[MEDIAN_WINDOW / 2])
        # filtered_vals.append(medfilt(
        #    [x[4] for x in self.past_vals], MEDIAN_WINDOW)[MEDIAN_WINDOW / 2])

        self.logger.info('Filtered Values: %s', filtered_vals)

        return filtered_vals

    def get_normalized_val(self, value):
        if 0 < value < THRESHOLD_USOUND_HIGH:
            return 101 - (value * 100.0 / THRESHOLD_USOUND_HIGH)
        return False

    @property
    def obstacle_map(self):

        vals = self.get_current_data()

        if len(vals) == 0:
            self.logger.info('Cannot create map due to data missing')
            return None

        obstacle_map = {}

        self.logger.info('Vals: %s', vals)

        obstacle_map['front'] = self.get_normalized_val(vals[0])
        obstacle_map['left'] = self.get_normalized_val(vals[1])
        obstacle_map['right'] = self.get_normalized_val(vals[2])
        obstacle_map['front_left'] = self.get_normalized_val(vals[3])
        obstacle_map['front_right'] = self.get_normalized_val(vals[4])

        self.logger.info('Obstacle map: %s', obstacle_map)

        return obstacle_map

    def drive_actuators(self, obstacle_map):
        self.motor_driver.left_motor(max(obstacle_map['left'], obstacle_map['front_left']))
        self.motor_driver.right_motor(max(obstacle_map['right'], obstacle_map['front_right']))
        self.motor_driver.center_motor(obstacle_map['front'])

    def start(self):
        """ This runs in the daemon """
        while True:
            self.drive_actuators(self.obstacle_map)
            time.sleep(0.5)

obsdet = ObstacleDetector(logger)
obsdet.start()
