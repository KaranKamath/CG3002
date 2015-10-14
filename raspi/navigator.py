#!/usr/bin/env python
import argparse
import logging
import sys
from time import sleep
from db import DB
from maps_repo import MapsRepo
from utils import run_dijkstra, CommonLogger
from nav_prompts import NavPrompts
from logging.handlers import TimedRotatingFileHandler

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
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Navigator(object):

    def __init__(self, logger):
        self.db = DB('/home/pi/db/uart.db')
        self.maps = MapsRepo()
        self.nav_prompts = NavPrompts()
        self.logger = logger
        self.logger.info("Starting navigator...")

    def start(self):
        self.wait_for_origin_and_destination()
        self.generate_path()

    def navigate(self):
        self.end = False
        while not end:
            continue
        self.nav_prompts.prompt('finish')

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
        self.path = run_dijkstra(self.maps.map(self.building, self.level),
                                 self.origin, self.destination)
        self.logger.info("Got path: %s", str(self.path))


nav = Navigator(logger)
nav.start()
nav.navigate()
