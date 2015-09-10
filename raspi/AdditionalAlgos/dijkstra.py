import json
import math

from pq import PriorityQueue


def calc_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def process_raw_map(raw_map):
    """Transform raw map into a graph for path finding"""
    graph = {}
    for node in raw_map['map']:
        graph[node['nodeId']] = {
            'linkTo': node['linkTo'].strip().split(', '),
            'x': node['x'],
            'y': node['y'],
            'name': node['nodeName']
        }
    return graph


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
                alt = dist[u] + \
                    calc_distance(int(u_node['x']), int(u_node['y']),
                                  int(graph[v]['x']), int(graph[v]['y']))
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    queue.insert(v, alt)

    path = []
    curr = target
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    path.append(source)
    return path[::-1]


if __name__ == '__main__':
    from fetch_map import fetch_raw_map
    raw_map = fetch_raw_map('COM1', '2')
    graph = process_raw_map(raw_map)
    print run_dijkstra(graph, '1', '10')
    print run_dijkstra(graph, '20', '1')
