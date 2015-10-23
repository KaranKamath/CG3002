import time
import argparse
import logging as log
from math import sqrt
from logging.handlers import TimedRotatingFileHandler

from pq import PriorityQueue
import db


class CommonLogger(object):

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != '':
            self.logger.log(self.level, message.rstrip())


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


def dijkstra(graph, source, target):
    """Dijkstra's shortest path algorithm"""
    queue = PriorityQueue()
    dist = {source: 0}
    prev = {}

    for vertex in graph:
        if vertex != source:
            dist[vertex] = float("inf")
        queue.insert(vertex, dist[vertex])

    while not queue.is_empty():
        u_dist, u = queue.pop()
        u_node = graph[u]

        if u == target:
            break

        for v in u_node['linkTo']:
            if queue.is_node_in_queue(v):
                alt = dist[u] + euclidean_dist(u_node['x'], u_node['y'],
                                               graph[v]['x'], graph[v]['y'])
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    queue.insert(v, alt)

    path = []
    curr = target
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    if path:
        path.append(source)
    return path[::-1]
