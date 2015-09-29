from math import sqrt, atan2, pi

m_min = (2468, -417, -1658)
m_max = (2581, -277, -1574)


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
