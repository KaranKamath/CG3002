from math import sqrt
from pq import PriorityQueue


def calc_distance(x1, y1, x2, y2):
    return sqrt((int(x1) - int(x2)) ** 2 + (int(y1) - int(y2)) ** 2)


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
                alt = dist[u] + calc_distance(u_node['x'], u_node['y'],
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


if __name__ == '__main__':
    import argparse
    from fetch_map import fetch_map

    parser = argparse.ArgumentParser(
        description='Get path from start to end node for building and level'
    )
    parser.add_argument('building', help='building name')
    parser.add_argument('level', help='level name')
    parser.add_argument('start', help='start node')
    parser.add_argument('end', help='end node')

    args = parser.parse_args()
    
    def find_path(building, level, start_node, end_node):
        graph = fetch_map(building, level)
        return run_dijkstra(graph, start_node, end_node)

    print find_path(args.building, args.level, args.start, args.end)
