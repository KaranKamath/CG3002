#!/usr/bin/env python
import argparse
import logging
import sys
from time import sleep
from db import DB
from maps_repo import MapsRepo
from utils import CommonLogger, dijkstra, euclidean_dist, init_logger
from prompts_manager import PromptsManager
from directions_utils import calc_directions


LOG_FILENAME = '/home/pi/logs/navi.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Navigator(object):

    ANGLE_THRESHOLD = 10
    DISTANCE_THRESHOLD = 100

    def __init__(self, logger):
        self.db = DB('/home/pi/db/uart.db')
        # self.db = DB('uart.db')
        self.maps = MapsRepo()
        self.prompts = PromptsManager()
        self.log = logger
        self.log.info("Starting navigator...")

    @property
    def next_node(self):
        return self.graph[self.path[self.next_node_idx]]

    @property
    def user_location(self):
        timestamp, x, y, heading, alt = self.db.fetch_location()
        while not timestamp:
            timestamp, x, y, heading, alt = self.db.fetch_location()
        return (x, y, heading, alt)

    def start(self):
        self.wait_for_origin_and_destination()
        self.generate_path()

    def navigate_to_next_node(self):
        x, y, heading, alt = self.user_location
        dist, angle = calc_directions(x, y, heading,
                                      self.next_node['x'],
                                      self.next_node['y'],
                                      self.north)
        self.log.info('Next node %s @[%scm, %sdeg]',
                      self.path[self.next_node_idx], dist, angle)
        self.generate_prompt(dist, angle)

    def generate_prompt(self, dist, angle):
        if dist < self.DISTANCE_THRESHOLD:
            self.log.info('Reached node %s',
                          self.path[self.next_node_idx])
            self.next_node_idx += 1
            self.log.info('Navigating to node %s',
                          self.path[self.next_node_idx])
            self.navigate_to_next_node()
        elif abs(angle) < self.ANGLE_THRESHOLD:
            if dist > 0:
                self.log.info('Prompting straight')
                self.prompts.prompt('straight')
            else:
                self.prompts.prompt('finish')
        elif angle > 0:
            self.log.info('Prompting right')
            self.prompts.prompt('right')
        else:
            self.log.info('Prompting left')
            self.prompts.prompt('left')

    def wait_for_origin_and_destination(self):
        self.log.info("Waiting for origin and destination...")
        bldg, level, orig, dest = self.db.fetch_origin_and_destination()
        while not bldg or not level or not orig or not dest:
            sleep(0.5)
            bldg, level, orig, dest = self.db.fetch_origin_and_destination()
        self.log.info("Got bldg: %s, level: %s, orig: %s, dest: %s",
                      bldg, level, orig, dest)
        self.building = bldg
        self.level = level
        self.origin = orig
        self.destination = dest
        self.graph = self.maps.map(self.building, self.level)
        self.north = self.maps.north_heading(self.building, self.level)
        self.db.insert_location(self.graph[orig]['x'],
                                self.graph[orig]['x'],
                                0, 0)

    def generate_path(self):
        self.log.info("Generating path...")
        self.path = dijkstra(self.graph, self.origin, self.destination)
        self.log.info("Got path: %s", str(self.path))
        self.acquire_next_node()

    def acquire_next_node(self):
        x, y, heading, alt = self.user_location
        min_dist = sys.maxint
        min_dist_node_idx = 0
        for i in range(len(self.path)):
            node = self.path[i]
            node_x = self.graph[node]['x']
            node_y = self.graph[node]['y']
            dist = euclidean_dist(node_x, node_y, x, y)
            if dist < min_dist:
                min_dist = dist
                min_dist_node_idx = i
        self.next_node_idx = min_dist_node_idx


nav = Navigator(logger)
nav.start()
while True:
    nav.navigate_to_next_node()
    sleep(3)
