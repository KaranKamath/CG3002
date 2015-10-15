import argparse
from utils import run_dijkstra
from maps_repo import MapsRepo

parser = argparse.ArgumentParser(
    description='Get path from start to end node for building and level'
)
parser.add_argument('building', help='building name')
parser.add_argument('level', help='level name')
parser.add_argument('start', help='start node')
parser.add_argument('end', help='end node')

args = parser.parse_args()


def find_path(building, level, start_node, end_node):
    m = MapsRepo()
    graph = m.map(building, level)
    return run_dijkstra(graph, start_node, end_node)

print find_path(args.building, args.level, args.start, args.end)
