import sqlite3
import json
import time


class DB(object):

    def __init__(self, db_name='uart.db'):
        if db_name.rfind('.db') == -1:
            db_name += '.db'

        self.conn = sqlite3.connect(db_name)
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data(timestamp INTEGER,
                sensor_id INTEGER, sensor_data TEXT)
            """)

    def insert(self, sid, raw_data):
        data = json.dumps(raw_data)
        timestamp = int(round(time.time() * 1000))

        query = 'INSERT INTO sensor_data values(?, ?, ?)'
        with self.conn:
            self.conn.execute(query, [timestamp, sid, data])

    def fetch(self, since=0, sid=None, raw_data=None):
        params = [since]
        query = 'SELECT * FROM sensor_data WHERE timestamp >= ?'

        if sid is not None:
            query += ' AND sensor_id=?'
            params.append(sid)

        if raw_data is not None:
            query += ' AND sensor_data=?'
            params.append(json.dumps(raw_data))

        data_to_return = []
        with self.conn:
            for row in self.conn.execute(query, params):
                data_to_return.append([row[1], json.loads(row[2])])
        return data_to_return

if __name__ == '__main__':
    foo = DB()
    print foo.fetch()
    foo.insert(1, {'data': {'x': 1, 'y': 2, 'z': 3}})
    print foo.fetch()
