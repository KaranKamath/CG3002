import sqlite3
import json
import time


class DB(object):

    def __init__(self, db_name='/home/pi/db/uart.db'):
        if db_name.rfind('.db') == -1:
            db_name += '.db'

        self.conn = sqlite3.connect(db_name, isolation_level=None)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS
            sensor_data(timestamp INTEGER,
                        sensor_id INTEGER,
                        sensor_data TEXT,
                        PRIMARY KEY (timestamp))
        """)

    def insert(self, sid, raw_data):
        data = json.dumps(raw_data)
        timestamp = int(round(time.time() * 1000))

        query = 'INSERT INTO sensor_data values(?, ?, ?)'
        self.conn.execute(query, [timestamp, sid, data])

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
        delete_query = 'DELETE FROM sensor_data WHERE timestamp IN (?)'
        timestamps_str = ','.join([str(t) for t in timestamps_to_delete])
        self.conn.execute(delete_query, [timestamps_str])

if __name__ == '__main__':
    foo = DB('uart.db')
    print foo.fetch()
    foo.insert(1, {'data': {'x': 1, 'y': 2, 'z': 3}})
    print foo.fetch()
    print foo.fetch(auto_delete=True)
    print foo.fetch()
