from math import sqrt, atan2, degrees
from utils import euclidean_dist


def normalize(h):
    """
        Input: heading
        Return: normalized heading between 180 and -180
    """
    while h > 180:
        h -= 360
    while h < -180:
        h += 360
    return h


def convert_heading_to_horizontal_axis(heading, map_north):
    """
        Input: heading wrt map heading with +ve = clockwise
        Return: heading wrt horizontal axis (180 to -180)
    """
    heading = 90 - map_north - heading
    return normalize(heading)
