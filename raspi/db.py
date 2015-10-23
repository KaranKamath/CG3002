import sqlite3
import json
import time


class DB(object):
    data_to_insert = []
    batch_size = 2
    initial_timestamp = 0
    block_timeout = 0.1 # 100ms as data incoming at 10Hz

    def __init__(self, logger, db_name='/home/pi/db/uart.db'):
        if db_name.rfind('.db') == -1:
            db_name += '.db'
        self.db_name = db_name
        self.log = logger
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
            nav_coords(building INTEGER,
                       level INTEGER,
                       origin INTEGER,
                       destination INTEGER)
        """)
        self.conn.execute('PRAGMA journal_mode = WAL')
        self._close_conn()

    def _open_conn(self):
        self.conn = sqlite3.connect(self.db_name, isolation_level=None)

    def _close_conn(self, commit=True):
        if commit:
            self.conn.commit()
        self.conn.close()
        self.conn = None

    def insert_origin_and_destination(self, bldg, level, orig, dstn):
        self._open_conn()
        self.conn.execute('DELETE FROM nav_coords')
        query = 'INSERT INTO nav_coords values(?, ?, ?, ?)'
        params = [int(bldg), int(level), int(orig), int(dstn)]
        self.conn.execute(query, params)
        self._close_conn()

    def fetch_origin_and_destination(self):
        query = 'SELECT * FROM nav_coords LIMIT 1'
        self._open_conn()
        data = list(self.conn.execute(query))
        blk_counter = 0
        while not data:
            time.sleep(self.block_timeout)
            blk_counter += 1
            if blk_counter >= 10:
                self.log.info("Still waiting on data...")
                blk_counter = 0
            data = list(self.conn.execute(query))
        self._close_conn(commit=False)
        return [str(d) for d in data[0]]

    def insert_data(self, sid, raw_data):
        data = json.dumps(raw_data)
        timestamp = int(round(time.time() * 1000))
        self.data_to_insert.append([timestamp, sid, data])
        if len(self.data_to_insert) >= self.batch_size:
            self._open_conn()
            self.conn.execute('BEGIN TRANSACTION')
            query = 'INSERT INTO sensor_data values(?, ?, ?)'
            self.conn.executemany(query, [d for d in self.data_to_insert])
            self.conn.execute('END TRANSACTION')
            self._close_conn()
            self.data_to_insert = []

    def fetch_data(self, since=0, sid=None):
        params = [since]
        query = 'SELECT * FROM sensor_data WHERE timestamp > ?'
        if sid is not None:
            query += ' AND sensor_id=?'
            params.append(sid)

        self._open_conn()
        data = list(self.conn.execute(query, params))
        blk_counter = 0
        while not data:
            time.sleep(self.block_timeout)
            blk_counter += 1
            if blk_counter >= 10:
                self.log.info("Still waiting on data...")
                blk_counter = 0
            data = list(self.conn.execute(query, params))
        self._close_conn(commit=False)
        return [[d[0], d[1], json.loads(d[2])] for d in data]

    def delete_data(self, t_stmps_to_delete):
        self._open_conn()
        self.conn.execute('BEGIN TRANSACTION')
        delete_query = 'DELETE FROM sensor_data WHERE timestamp = (?)'
        self.conn.executemany(delete_query,
                              [(str(t),) for t in t_stmps_to_delete])
        self.conn.execute('END TRANSACTION')
        self._close_conn()

    def insert_location(self, x, y, heading, altitude, is_initial=False):
        self._open_conn()
        timestamp = self.initial_timestamp if is_initial else\
            int(round(time.time() * 1000))
        query = 'INSERT INTO user_location values(?, ?, ?, ?, ?)'
        self.conn.execute(query, [timestamp, x, y, heading, altitude])
        self._close_conn()

    def fetch_location(self, allow_initial=False):
        self._open_conn()
        query = 'SELECT * FROM user_location ORDER BY timestamp DESC LIMIT 1'
        data = list(self.conn.execute(query))
        blk_counter = 0
        while not data or (not allow_initial and
                           data[0][0] == self.initial_timestamp):
            time.sleep(self.block_timeout)
            blk_counter += 1
            if blk_counter >= 10:
                self.log.info("Still waiting on data...")
                blk_counter = 0
            data = list(self.conn.execute(query))
        self._close_conn(commit=False)
        return data[0]

    def delete_locations(self):
        self._open_conn()
        self.conn.execute('DELETE FROM user_location')
        self._close_conn()

if __name__ == '__main__':
    foo = DB('uart.db')
    foo.insert_origin_and_destination(1, 2, 23423, 24)
    print foo.fetch_origin_and_destination()
    foo.insert_location(0, 0, 0, 0, True)
    print foo.fetch_location(allow_initial=True)
    time.sleep(0.1)
    foo.insert_location(0, 0, 0, 0, False)
    print foo.fetch_location()
