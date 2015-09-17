import sys
import sqlite3

default_name = 'uart'

def reset_db(db_name=default_name):

    db_name = db_name + '.db'

    print 'Resetting', db_name
    conn = sqlite3.connect(db_name)
    
    c = conn.cursor()
    
    c.execute(\
    '''DROP TABLE IF EXISTS sensor_data;''')
   
    c.execute(\
    '''CREATE TABLE sensor_data(
        timestamp INTEGER,
        sensor_id INTEGER,
        sensor_data TEXT
    );''')
    
    conn.commit()
    
    c.close()
    
    conn.close()

if __name__ == "__main__":
 
    if len(sys.argv) > 1:
        default_name = sys.argv[1] + '.db'

    print 'running reset on db ' + default_name
    reset_db(default_name)
