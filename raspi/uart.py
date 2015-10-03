#!/usr/bin/env python
import logging
import logging.handlers
import argparse
import sys
import time
import serial

from db import DB

LOG_FILENAME = '/home/pi/logs/uart.log'
LOG_LEVEL = logging.INFO

parser = argparse.ArgumentParser(description="Uart service")
parser.add_argument("-l", "--log",
                    help="log file (default: " + LOG_FILENAME + ")")
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILENAME, when='midnight', backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s'))
logger.addHandler(handler)


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

    def __init__(self, logger):
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
        self.logger = logger
        self.db = DB()
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
            self.logger.info('Stored data '
                             '[device_id: %s, data: %s, seq_id: %s]',
                             device_id, data, seq_id)
            self.db.insert(device_id, data)

    def close(self):
        self.ser.close()

    def perform_handshake(self):
        self._wait_for_begin()
        self._sync_acks()
        self.logger.info('Handshake done...')

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
    uart.stream_data()
except KeyboardInterrupt:
    uart.close()
