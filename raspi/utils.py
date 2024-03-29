import time
import argparse
import logging as log
from math import sqrt, atan2, degrees
from logging.handlers import TimedRotatingFileHandler
from Queue import PriorityQueue


class CommonLogger(object):

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != '':
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        for h in self.logger.handlers:
            h.flush()


def init_logger(logger, logfile):
    p = argparse.ArgumentParser()
    p.add_argument("-l", "--log", help="log file (default: " + logfile + ")")
    args = p.parse_args()
    logfile = args.log if args.log else logfile

    handler = TimedRotatingFileHandler(logfile, when='H', backupCount=3)
    log_format = '%(asctime)s %(levelname)-8s %(message)s'
    handler.setFormatter(log.Formatter(log_format))
    logger.setLevel(log.INFO)
    logger.addHandler(handler)
    return logger


def euclidean_dist(x1, y1, x2, y2):
    return sqrt((int(x1) - int(x2)) ** 2 + (int(y1) - int(y2)) ** 2)


def now():
    return int(round(time.time() * 1000))


def normalize_360(heading):
    while heading > 180:
        heading -= 360
    while heading < -180:
        heading += 360
    return heading


def angle_bw_vectors(v_a, v_b):
    angle_v_a = degrees(atan2(v_a[1], v_a[0]))
    angle_v_b = degrees(atan2(v_b[1], v_b[0]))
    return normalize_360(angle_v_b - angle_v_a)


def dijkstra(graph, source, target):
    """Dijkstra's shortest path algorithm"""
    queue = PriorityQueue()
    dist = {source: 0}
    prev = {}

    for vertex in graph:
        if vertex != source:
            dist[vertex] = float("inf")
        queue.put((dist[vertex], vertex))

    while queue.qsize() != 0:
        u_dist, u = queue.get()
        u_node = graph[u]

        if u == target:
            break

        for v in u_node['linkTo']:
            alt = dist[u] + euclidean_dist(u_node['x'], u_node['y'],
                                           graph[v]['x'], graph[v]['y'])
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                queue.put((alt, v))

    path = []
    curr = target
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    path.append(source)
    return path[::-1]
