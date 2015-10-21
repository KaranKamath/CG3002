#!/usr/bin/env python
import argparse
import logging
import sys
import time
from math import atan2, degrees

from db import DB
from maps_repo import MapsRepo
from prompts_enum import PromptDirn
from directions_utils import normalize
from audio_driver import AudioDriver
from motor_driver import MotorDriver
from obstacle_detection import ObstacleDetector
from utils import CommonLogger, dijkstra, euclidean_dist, init_logger


LOG_FILENAME = '/home/pi/logs/navi.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Navigator(object):

    ANGLE_THRESHOLD = 20
    DISTANCE_THRESHOLD = 75
    location_tstmp = 1

    def __init__(self, logger):
        self.log = logger
        self.log.info('Starting navigator...')
        self.db = DB()
        self.maps = MapsRepo()
        self.audio = AudioDriver()
        self.motors = MotorDriver()
        self.obstacle_detector = ObstacleDetector(self.db, self.log)
        self.current_prompt = None
        self.navigation_finished = False

    @property
    def next_node(self):
        return self.graph[self.next_node_id]

    @property
    def next_node_id(self):
        return self.path[self.next_node_idx]

    @property
    def user_location(self):
        data = self.db.fetch_location(timestamp=self.location_tstmp,
                                      blocking=True)
        self.location_tstmp = data[0]
        return data[1:]

    def start(self):
        self._wait_for_origin_and_destination()
        self._get_map()
        self._generate_path()
        self._acquire_next_node()
        while not self.navigation_finished:
            self._navigate_to_next_node()
            time.sleep(0.1)

    def stop(self):
        self.navigation_finished = True
        self.current_prompt = PromptDirn.end
        self.audio.prompt(self.current_prompt)
        self.motors.prompt(self.current_prompt)

    def _wait_for_origin_and_destination(self):
        self.log.info('Waiting for origin and destination...')
        bldg, level, orig, dest = self.db.fetch_origin_and_destination(True)
        self.log.info('Got bldg: %s, level: %s, orig: %s, dest: %s',
                      bldg, level, orig, dest)
        self.building = bldg
        self.level = level
        self.origin = orig
        self.destination = dest

    def _get_map(self):
        self.graph = self.maps.map(self.building, self.level)
        self.north = self.maps.north_heading(self.building, self.level)
        self.db.insert_location(self.graph[self.origin]['x'],
                                self.graph[self.origin]['y'],
                                self.north, 0, True)

    def _generate_path(self):
        self.log.info('Generating path...')
        self.path = dijkstra(self.graph, self.origin, self.destination)
        self.log.info('Got path: %s', str(self.path))

    def _acquire_next_node(self):
        x, y, heading, alt = self.user_location
        min_dist = sys.maxint
        min_dist_node_idx = 0
        for i in range(len(self.path)):
            node = self.path[i]
            node_x = self.graph[node]['x']
            node_y = self.graph[node]['y']
            dist = euclidean_dist(node_x, node_y, x, y)
            if dist < min_dist and dist > self.DISTANCE_THRESHOLD:
                min_dist = dist
                min_dist_node_idx = i
        self.next_node_idx = min_dist_node_idx

    def _navigate_to_next_node(self):
        x, y, heading, alt = self.user_location
        dist, angle = self._calc_directions(x, y,
                                            self.next_node['x'],
                                            self.next_node['y'],
                                            heading)
        self.log.info('Next node %s @[%scm, %sdeg]', self.next_node_id,
                      dist, angle)
        if dist < self.DISTANCE_THRESHOLD:
            self.audio.prompt_node_reached(self.next_node_id)
            self.log.info('Reached node %s', self.next_node_id)
            self.next_node_idx += 1
            if self.next_node_idx == len(self.path):
                self.log.info('Reached destination node')
                self.stop()
            else:
                self.log.info('Navigating to node %s', self.next_node_id)
                self._navigate_to_next_node()
        else:
            self._generate_prompt(angle)

    def _calc_directions(self, x, y, node_x, node_y, heading):
        distance = int(round(euclidean_dist(node_x, node_y, x, y)))
        if distance < self.DISTANCE_THRESHOLD:
            return (distance, 0)
        turn_to_angle = degrees(atan2(node_y - y, node_x - x)) - heading
        return (distance, int(round(normalize(turn_to_angle))))

    def _generate_prompt(self, angle):
        if abs(angle) < self.ANGLE_THRESHOLD:
            if self.current_prompt is None or \
                    self.current_prompt == PromptDirn.left and angle <= 0 or \
                    self.current_prompt == PromptDirn.right and angle >= 0:
                new_prompt = PromptDirn.straight
            else:
                new_prompt = self.current_prompt
        elif angle > 0:
            new_prompt = PromptDirn.left
        else:
            new_prompt = PromptDirn.right

        if self.current_prompt is None or self.current_prompt != new_prompt:
            self.current_prompt = new_prompt
            self.audio.prompt(new_prompt)
            self.motors.prompt(new_prompt)


nav = Navigator(logger)
nav.start()
