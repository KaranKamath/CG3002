#!/usr/bin/env python
import logging
import argparse
import sys
import time
import serial
from db import DB
from utils import CommonLogger, init_logger

LOG_FILENAME = '/home/pi/logs/uart.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class UartHandler(object):

    def __init__(self, logger, serial_line='/dev/ttyAMA0',
                 baud_rate=9600, timeout=1):
        self.ser = serial.Serial(serial_line, baud_rate, timeout=timeout)
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
