import time
from math import sqrt
from pq import PriorityQueue
import db


class CommonLogger(object):

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != '':
            self.logger.log(self.level, message.rstrip())


def euclidean_dist(x1, y1, x2, y2):
    return sqrt((int(x1) - int(x2)) ** 2 + (int(y1) - int(y2)) ** 2)


def vector_dot_3d(a, b):
    if len(a) == 3 and len(b) == 3:
        return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])
    return None


def vector_cross_3d(a, b):
    if len(a) == 3 and len(b) == 3:
        return ((a[1] * b[2]) - (a[2] * b[1]),
                (a[2] * b[0]) - (a[0] * b[2]),
                (a[0] * b[1]) - (a[1] * b[0]))
    return None


def vector_normalize_3d(a):
    n = sqrt(vector_dot_3d(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def run_dijkstra(graph, source, target):
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


def stream_data(sid):
    t_stmp = int(round(time.time() * 1000))
    db_conn = db.DB()
    while True:
        data = db_conn.fetch_data(sid=sid, since=t_stmp)
        if data:
            t_stmp = data[-1][0]
        for d in data:
            yield d
