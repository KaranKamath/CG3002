from math import sqrt, atan2, pi
import sys

m_min = [32767, 32767, 32767]
m_max = [-32768, -32768, -32768]


def vector_dot(a, b):
    if len(a) == 3 and len(b) == 3:
        return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])
    return None


def vector_cross(a, b):
    if len(a) == 3 and len(b) == 3:
        return ((a[1] * b[2]) - (a[2] * b[1]),
                (a[2] * b[0]) - (a[0] * b[2]),
                (a[0] * b[1]) - (a[1] * b[0]))
    return None


def vector_normalize(a):
    n = sqrt(vector_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def heading(a, m, f):
    m = (m[0] - (m_min[0] + m_max[0]) / 2,
         m[1] - (m_min[1] + m_max[1]) / 2,
         m[2] - (m_min[2] + m_max[2]) / 2)

    e = vector_normalize(vector_cross(m, a))
    n = vector_normalize(vector_cross(a, e))

    heading = atan2(vector_dot(e, f), vector_dot(n, f)) * 180 / pi
    return (heading + 360) if heading < 0 else heading


def calibrate(db):
    global m_min, m_max
    counter = 1000
    current = int(time.time()*1000)
    while counter > 0:
        counter -= 1
        data = db.fetch(since=current, sid=1)
        if data:
            current = data[-1][0]
            data = data[-1][2]
            for i in range(3):
                if data[i + 3] < m_min[i]:
                    m_min[i] = data[i + 3]
                if data[i + 3] > m_max[i]:
                    m_max[i] = data[i + 3]

if __name__ == '__main__':
    import time
    from db import DB
    foo = DB()
    # calibrate(foo)
    current = int(time.time()*1000)
    while True:
        data = foo.fetch(since=current, sid=1)
        if data:
            data = data[-1]
            heading_v = heading(data[2][:3], data[2][3:], [0, 0, 1])
            sys.stdout.flush()
            sys.stdout.write("Heading: %s deg   \r" % (heading_v,))
            current = data[0]
