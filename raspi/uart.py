#!/usr/bin/env python
import logging
import sys
import time
import serial
from db import DB
from utils import CommonLogger, init_logger
from audio_driver import AudioDriver

LOG_FILENAME = '/home/pi/logs/uart.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class UartHandler(object):

    def __init__(self, logger, serial_line='/dev/ttyAMA0',
                 baud_rate=115200, timeout=1):
        self.ser = serial.Serial(serial_line, baud_rate, timeout=timeout)
        self.logger = logger
        self.db = DB(logger)
        self.audio = AudioDriver()
        self.logger.info('Opening serial line')

    def _serial_read_line(self):
        return self.ser.readline().strip()

    def _wait_for_begin(self):
        self.audio.prompt_begin()
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
        self.audio.prompt_enter_info()
        _input = self._serial_read_line()
        while not _input or _input.count('*') != 5:
            _input = self._serial_read_line()
        self.ser.write('ACK')
        self.logger.error('Got data %s', _input)
        o_bldg, o_level, o_node, d_bldg, d_level, d_node = _input.split('*')
        self.db.insert_origin_and_destination(o_bldg, o_level, o_node,
                                              d_bldg, d_level, d_node)
        self.logger.info('Got Origin [Building %s, Level %s, Node %s]',
                         o_bldg, o_level, o_node)
        self.logger.info('Got Destination [Building %s, Level %s, Node %s]',
                         d_bldg, d_level, d_node)

    def read_data(self):
        self.logger.info('Receiving data...')
        log_counter = 0
        while True:
            data = self._serial_read_line()
            if data:
                (packet_type, data) = self._parse_data(data)
                self.db.insert_data(packet_type, data)
                log_counter += 1
                if log_counter > 50:
                    self.logger.info('Receiving data...')
                    log_counter = 0
                # self.logger.info('Stored data [type: %s, data: %s]',
                #                  packet_type, data)


uart = UartHandler(logger)
uart.perform_handshake()
uart.read_origin_and_destination()
uart.read_data()
