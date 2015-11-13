from db import DB
import logging
database = DB(logging.getLogger(__name__), 'uart.08-39-40.db')

vals = [ x[2][-3] for x in database.fetch_data(sid=0) ]

import matplotlib.pyplot as plt

def plot(label, vals):
    plt.plot(range(len(vals)), vals)
    plt.ylabel(label)
    plt.draw()

plot('X', vals)

plt.show()

print vals
