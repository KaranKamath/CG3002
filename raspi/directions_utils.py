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


def calc_directions(x, y, heading, node_x, node_y, map_north, threshold=0):
    """
        Input: user's x, y and heading along with target's x and y and
               map north
        Return: distance and angle to turn for target
    """
    distance = euclidean_dist(node_x, node_y, x, y)
    if distance <= threshold:
        return (0, 0)

    x_diff = node_x - x
    y_diff = node_y - y
    heading = convert_heading_to_horizontal_axis(heading, map_north)
    turn_to_angle = normalize(heading - degrees(atan2(y_diff, x_diff)))
    return (int(round(distance)), int(round(turn_to_angle)))
