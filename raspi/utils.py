import time
from math import sqrt

import db


def euclidean_distance(x1, y1, x2, y2):
    return sqrt((int(x1) - int(x2)) ** 2 + (int(y1) - int(y2)) ** 2)


def vector_dot_3d(self, a, b):
    if len(a) == 3 and len(b) == 3:
        return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])
    return None


def vector_cross_3d(self, a, b):
    if len(a) == 3 and len(b) == 3:
        return ((a[1] * b[2]) - (a[2] * b[1]),
                (a[2] * b[0]) - (a[0] * b[2]),
                (a[0] * b[1]) - (a[1] * b[0]))
    return None


def vector_normalize_3d(self, a):
    n = sqrt(vector_dot_3d(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def stream_data(sid):
    t_stmp = int(round(time.time() * 1000))
    db_conn = db.DB()
    while True:
        data = db_conn.fetch_data(sid=sid, since=t_stmp)
        if data:
            t_stmp = data[-1][0]
        for d in data:
            yield d
