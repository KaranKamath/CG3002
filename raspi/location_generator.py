import time
from math import atan2, pi

from db import DB
from utils import vector_dot_3d, vector_cross_3d, vector_normalize_3d


class LocationGenerator(object):

    device_timestamps = {
        0: 0,
        1: 0
    }
    mag_min = [32767, 32767, 32767]
    mag_max = [-32768, -32768, -32768]

    def __init__(self, db_location):
        self.db = DB(db_location)
        timestamp = int(round(time.time() * 1000))
        for device in self.device_timestamps:
            self.device_timestamps[device] = timestamp

    def _get_data(self, sid, timestamp):
        return self.db.fetch_data(sid=sid, since=timestamp,
                                  auto_delete=True)

    def _get_altitude(self, data):
        return data[0] / 1000

    def _get_heading(self, data):
        a = data[1:4]
        m = data[4:7]
        f = [0, 0, 1]

        m = (m[0] - (self.mag_min[0] + self.mag_max[0]) / 2,
             m[1] - (self.mag_min[1] + self.mag_max[1]) / 2,
             m[2] - (self.mag_min[2] + self.mag_max[2]) / 2)
        e = vector_normalize_3d(vector_cross_3d(m, a))
        n = vector_normalize_3d(vector_cross_3d(a, e))
        heading = atan2(vector_dot_3d(e, f),
                        vector_dot_3d(n, f)) * 180 / pi
        return (heading + 360) if heading < 0 else heading

    def _get_latest_readings(self):
        latest_data = {}
        for (k, v) in self.device_timestamps.items():
            data = self._get_data(k, v)
            if data:
                self.device_timestamps[k] = data[-1][0]
                latest_data[k] = [d[2] for d in data]
            else:
                latest_data[k] = None
        return latest_data

    def start(self):
        while True:
            data = self._get_latest_readings()
            imu_data = data[0]
            latest_imu_data = imu_data[-1]
            altitude = self._get_altitude(latest_imu_data)
            heading = self._get_heading(latest_imu_data)
            print altitude, heading
            time.sleep(0.5)


generator = LocationGenerator('/home/pi/db/uart.db')
generator.start()
