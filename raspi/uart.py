#!/usr/bin/env python
import logging
import argparse
import sys
import time
import serial
from db import DB
from logging.handlers import TimedRotatingFileHandler
from utils import CommonLogger

LOG_FILENAME = '/home/pi/logs/uart.log'
LOG_LEVEL = logging.INFO

p = argparse.ArgumentParser(description="Uart service")
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


class UartHandler():

    def __init__(self, logger, serial_line='/dev/ttyAMA0',
                 baud_rate=9600, timeout=1):
        self.ser = serial.Serial(serial_line, baud_rate, timeout=timeout)
        self.logger = logger
        self.db = DB('/home/pi/db/uart.db')
        self.logger.info('Opening serial line')

    def _serial_read_line(self):
        return self.ser.readline().strip()

    def _wait_for_begin(self):
        while True:
            if self._serial_read_line() == 'BEGIN':
                self.logger.info('Got BEGIN')
                return
            else:
                self.logger.info('Waiting for BEGIN')

    def _sync_acks(self):
        while True:
            self.ser.write('ACK')
            self.logger.info('Sent ACK')
            if self._serial_read_line() == 'ACK':
                self.logger.info('Got ACK')
                return
            else:
                self.logger.info('Waiting for ACK')

    def _parse_data(self, raw_data):
        data_components = raw_data.split('|')
        if len(data_components) == 2:
            packet_type = data_components[0]
            data = [int(d.strip()) for d in data_components[1].split(',')]
            return (packet_type, data)
        return (None, None)

    def perform_handshake(self):
        self._wait_for_begin()
        self._sync_acks()
        self.logger.info('Handshake done...')

    def read_origin_and_destination(self):
        self.logger.info('Waiting for origin and destination...')
        _input = self._serial_read_line()
        while not _input:
            _input = self._serial_read_line()
        self.ser.write('ACK')
        building, level, origin, destination = _input.split('*')
        self.db.insert_origin_and_destination(building, level, origin,
                                              destination)
        self.logger.info('Got [Building %s, Level %s, Start %s, End %s]',
                         building, level, origin, destination)

    def read_data(self):
        self.logger.info('Waiting for data...')
        while True:
            data = self._serial_read_line()
            if data:
                (packet_type, data) = self._parse_data(data)
                self.db.insert_data(packet_type, data)
                self.logger.info('Stored data [type: %s, data: %s]',
                                 packet_type, data)


uart = UartHandler(logger)
uart.perform_handshake()
uart.read_origin_and_destination()
uart.read_data()
