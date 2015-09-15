import logging
import serial

LOG_FILENAME = '/home/pi/logs/uart.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO)


class UartHandler():

    def __init__(self):
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=10)
        self.logger = logging

        self.logger.info('Opening serial line')
        self.ser.open()
        self._perform_handshake()
        self._stream_data()

    def _serial_read_line(self):
        return self.ser.readline().strip()

    def _perform_handshake(self):
        self._wait_for_begin()
        self._sync_acks()

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

    def _stream_data(self):
        try:
            while True:
                data = self._serial_read_line()
                if data:
                    self._parse_data(data)
                    self.ser.write('ACK')
        except KeyboardInterrupt:
            self.ser.close()

    def _parse_data(self, raw_data):
        data_components = raw_data.split('|')
        if len(data_components) == 3:
            device_id = data_components[0]
            data = [d.strip() for d in data_components[1].split(',')]
            seq_id = data_components[2]

            logging.info('Received data '
                         '[device_id: %s, data: %s, seq_id: %s]',
                         device_id, data, seq_id)
            self._store_data(device_id, data, seq_id)

    def _store_data(self, device_id, data, seq_id):
        pass


if __name__ == '__main__':
    uart = UartHandler()
