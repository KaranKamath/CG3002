import sqlite3
import json
import time


class DB(object):
    RETRY_TIMEOUT = 10

    def __init__(self, db_name='/home/pi/db/uart.db'):
        if db_name.rfind('.db') == -1:
            db_name += '.db'

        self.conn = sqlite3.connect(db_name)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS
            sensor_data(timestamp INTEGER,
                        sensor_id INTEGER,
                        sensor_data TEXT,
                        PRIMARY KEY (timestamp))
        """)
        self.conn.commit()

    def insert(self, sid, raw_data):
        data = json.dumps(raw_data)
        timestamp = int(round(time.time() * 1000))

        query = 'INSERT INTO sensor_data values(?, ?, ?)'
        self.conn.execute(query, [timestamp, sid, data])
        self.conn.commit()

    def fetch(self, since=0, sid=None, raw_data=None, auto_delete=False):
        params = [since]
        query = 'SELECT * FROM sensor_data WHERE timestamp >= ?'

        if sid is not None:
            query += ' AND sensor_id=?'
            params.append(sid)

        if raw_data is not None:
            query += ' AND sensor_data=?'
            params.append(json.dumps(raw_data))

        ret_val = []
        for row in self.conn.execute(query, params):
            ret_val.append([row[0], row[1], json.loads(row[2])])

        if auto_delete:
            self.delete([v[0] for v in ret_val])

        return ret_val

    def delete(self, timestamps_to_delete):
        delete_query = 'DELETE FROM sensor_data WHERE timestamps IN (?)'
        timestamps_str = ','.join(timestamps_to_delete)
        self.conn.execute(delete_query, [timestamps_str])
        self.conn.commit()

if __name__ == '__main__':
    foo = DB()
    print foo.fetch()
    foo.insert(1, {'data': {'x': 1, 'y': 2, 'z': 3}})
    print foo.fetch()
