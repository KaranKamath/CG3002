#!/usr/bin/env python
import logging
import argparse
import sys
import time
import serial

from logging.handlers import TimedRotatingFileHandler

import db

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


class UartLogger(object):

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != '':
            self.logger.log(self.level, message.rstrip())

sys.stdout = UartLogger(logger, logging.INFO)
sys.stderr = UartLogger(logger, logging.ERROR)


class UartHandler():

    def __init__(self, logger, serial_line='/dev/ttyAMA0',
                 baud_rate=9600, timeout=1):
        self.ser = serial.Serial(serial_line, baud_rate, timeout=timeout)
        self.logger = logger
        self.db = db.DB('/home/pi/db/uart.db')
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
            data = self.ser.readline().strip()
            if data == 'ACK':
                self.logger.info('Got ACK')
                return
            else:
                self.logger.info('Waiting for ACK')

    def _parse_data(self, raw_data):
        data_components = raw_data.split('|')
        if len(data_components) == 3:
            device_id = data_components[0]
            data = [int(d.strip()) for d in data_components[1].split(',')]
            seq_id = data_components[2]
            return (device_id, data, seq_id)
        return (None, None, None)

    def _store_data(self, device_id, data, seq_id):
        if device_id and data and seq_id:
            self.db.insert_data(device_id, data)
            self.logger.info('Stored data '
                             '[device_id: %s, data: %s, seq_id: %s]',
                             device_id, data, seq_id)

    def _store_origin_and_destination(self, origin, destination):
        if origin and destination:
            self.db.insert_origin_and_destination(origin, destination)
            self.logger.info('Stored origin and destination '
                             '[origin: %s, destination: %s]',
                             origin, destination)

    def close(self):
        self.ser.close()

    def perform_handshake(self):
        self._wait_for_begin()
        self._sync_acks()
        self.logger.info('Handshake done...')

    def read_origin_and_destination(self):
        self.logger.info('Waiting for origin and destination...')
        origin = self._serial_read_line().strip()
        while not origin:
            origin = self._serial_read_line().strip()
        self.ser.write('ACK')

        destination = self._serial_read_line().strip()
        while not destination:
            destination = self._serial_read_line().strip()
        self.ser.write('ACK')
        self.logger.info('Got [%s, %s]', origin, destination)
        self._store_origin_and_destination(origin, destination)

    def stream_data(self):
        self.logger.info('Streaming data...')
        while True:
            data = self._serial_read_line()
            self.logger.info('Received data: %s', data)
            if data:
                (dev_id, data, seq_id) = self._parse_data(data)
                self._store_data(dev_id, data, seq_id)
                self.ser.write('ACK')


uart = UartHandler(logger)
try:
    uart.perform_handshake()
    uart.read_origin_and_destination()
    uart.stream_data()
except KeyboardInterrupt:
    uart.close()
