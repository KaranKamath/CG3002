import time
import sqlite3
import json

db_name = 'uart.db' #default

def set_db(new_name):
    global db_name
    db_name = new_name + '.db'

    print 'DB', db_name, 'selected'

def insert(sid, raw_data):

    sdata = json.dumps(raw_data)
    timestamp = int(round(time.time() * 1000))

    conn = sqlite3.connect(db_name)
    
    c = conn.cursor()
    
    c.execute(\
'''INSERT INTO sensor_data values(%s, %s, '%s')''' % (timestamp, sid, sdata))

    conn.commit()
    c.close()
    conn.close()

def fetch(since='0', sid=None, raw_data=None):
    
    query_string = '''SELECT * FROM sensor_data WHERE timestamp >= %s''' % (since)

    if sid is not None:
        query_string += ''' AND sensor_id=%s''' % (sid)

    if raw_data is not None:
        query_string += ''' AND sensor_data=%s''' % (json.dumps(raw_data))

    conn = sqlite3.connect(db_name)

    c = conn.cursor()

    c.execute(query_string)

    fetched_vals = c.fetchall()

    conn.commit()

    c.close()
    conn.close()

    data_to_return = [[row[1], json.loads(row[2])] for row in fetched_vals]

    return data_to_return
