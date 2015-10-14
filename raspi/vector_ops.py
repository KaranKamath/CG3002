from math import sqrt


def dot_3d(a, b):
    if len(a) == 3 and len(b) == 3:
        return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])
    return None


def cross_3d(a, b):
    if len(a) == 3 and len(b) == 3:
        return ((a[1] * b[2]) - (a[2] * b[1]),
                (a[2] * b[0]) - (a[0] * b[2]),
                (a[0] * b[1]) - (a[1] * b[0]))
    return None


def normalize_3d(a):
    n = sqrt(dot_3d(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)
