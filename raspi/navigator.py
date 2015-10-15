#!/usr/bin/env python
import argparse
import logging
import sys
from time import sleep
from logging.handlers import TimedRotatingFileHandler

from db import DB
from maps_repo import MapsRepo
from utils import CommonLogger, dijkstra
from prompts_manager import PromptsManager
from directions_utils import calc_directions


LOG_FILENAME = '/home/pi/logs/navi.log'
LOG_LEVEL = logging.INFO

p = argparse.ArgumentParser(description="Navi service")
p.add_argument("-l", "--log", help="log file (default: " + LOG_FILENAME + ")")
args = p.parse_args()
if args.log:
    LOG_FILENAME = args.log

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
h = TimedRotatingFileHandler(LOG_FILENAME, when='H', backupCount=3)
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logger.addHandler(h)
# sys.stdout = CommonLogger(logger, logging.INFO)
# sys.stderr = CommonLogger(logger, logging.ERROR)


class Navigator(object):

    def __init__(self, logger):
        # self.db = DB('/home/pi/db/uart.db')
        self.db = DB('uart.db')
        self.maps = MapsRepo()
        self.prompts = PromptsManager()
        self.logger = logger
        self.logger.info("Starting navigator...")

    def start(self):
        self.wait_for_origin_and_destination()
        self.generate_path()

    def navigate_to_next_node(self):
        timestamp, x, y, heading, alt = self.db.fetch_location()
        while not timestamp:
            timestamp, x, y, heading, alt = self.db.fetch_location()
        dist, angle = calc_directions(x, y, heading,
                                      self.next_node['x'],
                                      self.next_node['y'],
                                      self.north)
        print dist, angle
        # self.prompts.prompt('finish')

    def wait_for_origin_and_destination(self):
        self.logger.info("Waiting for origin and destination...")
        bldg, level, orig, dest = self.db.fetch_origin_and_destination()
        while not bldg or not level or not orig or not dest:
            sleep(0.5)
            bldg, level, orig, dest = self.db.fetch_origin_and_destination()
        self.logger.info("Got bldg: %s, level: %s, orig: %s, dest: %s",
                         bldg, level, orig, dest)
        self.building = bldg
        self.level = level
        self.origin = orig
        self.destination = dest

    def generate_path(self):
        self.logger.info("Generating path...")
        self.graph = self.maps.map(self.building, self.level)
        self.north = self.maps.north_heading(self.building, self.level)
        self.path = dijkstra(self.graph, self.origin, self.destination)
        self.logger.info("Got path: %s", str(self.path))
        self.next_node_idx = 1
        self.next_node = self.graph[self.path[self.next_node_idx]]


nav = Navigator(logger)
nav.start()
while True:
    nav.navigate_to_next_node()
    sleep(3)
