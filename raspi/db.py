import sqlite3
import json
import time


class DB(object):

    def __init__(self, db_name='uart.db'):
        if db_name.rfind('.db') == -1:
            db_name += '.db'
        self.db_name = db_name
        self._setup()

    def _setup(self):
        self._open_conn()
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS
            sensor_data(timestamp INTEGER,
                        sensor_id INTEGER,
                        sensor_data TEXT,
                        PRIMARY KEY (timestamp))
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS
            user_location(timestamp INTEGER,
                          x INTEGER,
                          y INTEGER,
                          heading INTEGER,
                          altitude INTEGER,
                          PRIMARY KEY (timestamp))
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS
            nav_coords(origin INTEGER,
                       destination INTEGER)
        """)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self._close_conn()

    def _open_conn(self):
        self.conn = sqlite3.connect(self.db_name, isolation_level=None)

    def _close_conn(self, commit=True):
        if commit:
            self.conn.commit()
        self.conn.close()
        self.conn = None

    def insert_origin_and_destination(self, origin, destination):
        self._open_conn()

        # clear existing nav coords
        query = 'TRUNCATE TABLE nav_coords'
        self.conn.execute(query)

        # insert new ones
        query = 'INSERT INTO nav_coords values(?, ?)'
        self.conn.execute(query, origin, destination)
        self._close_conn()

    def insert_data(self, sid, raw_data):
        self._open_conn()
        data = json.dumps(raw_data)
        timestamp = int(round(time.time() * 1000))
        query = 'INSERT INTO sensor_data values(?, ?, ?)'
        self.conn.execute(query, [timestamp, sid, data])
        self._close_conn()

    def insert_location(self, x, y, heading, altitude):
        self._open_conn()
        timestamp = int(round(time.time() * 1000))
        query = 'INSERT INTO user_location values(?, ?, ?, ?, ?)'
        self.conn.execute(query, [timestamp, x, y, heading, altitude])
        self._close_conn()

    def fetch_data(self, since=0, sid=None, raw_data=None, auto_delete=False):
        params = [since]
        query = 'SELECT * FROM sensor_data WHERE timestamp > ?'

        if sid is not None:
            query += ' AND sensor_id=?'
            params.append(sid)

        if raw_data is not None:
            query += ' AND sensor_data=?'
            params.append(json.dumps(raw_data))

        self._open_conn()
        ret_val = []
        for row in self.conn.execute(query, params):
            ret_val.append([row[0], row[1], json.loads(row[2])])
        self._close_conn(commit=False)

        if auto_delete:
            self.delete_data([v[0] for v in ret_val])
        return ret_val

    def delete_data(self, t_stmps_to_delete):
        self._open_conn()
        delete_query = 'DELETE FROM sensor_data WHERE timestamp = (?)'
        self.conn.executemany(delete_query,
                              [(str(t),) for t in t_stmps_to_delete])
        self._close_conn()


if __name__ == '__main__':
    foo = DB()
    print foo.fetch_data()
    foo.insert_data(0, [30000])
    print foo.fetch_data()
    print foo.fetch_data(auto_delete=True)
    print foo.fetch_data()
    for i in range(10):
        foo.insert_data(0, [30000])
        time.sleep(0.5)
    print foo.fetch_data()
