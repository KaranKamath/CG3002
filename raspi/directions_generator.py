from math import atan2, degrees, sqrt


class DirectionsGenerator(object):

    def __init__(self, path, graph, north_heading):
        self.path = path
        self.graph = graph
        self.north_heading = north_heading
        self.next_node_idx = 1

    @property
    def next_node(self):
        return self.path[self.next_node_idx]

    def _convert_heading_from_map(self, heading):
        """
            Input: heading wrt map heading (0 to 359)
            Return: heading wrt horizontal axis (180 to -180)
        """
        heading = 90 - self.north_heading - heading
        while heading > 180:
            heading -= 360
        while heading < -180:
            heading += 360
        return heading

    def get_directions(self, x, y, heading):
        x_diff = self.graph[self.next_node]['x'] - x
        y_diff = self.graph[self.next_node]['y'] - y

        if x_diff == 0 and y_diff == 0:
            self.next_node_idx += 1
            if self.next_node_idx == len(self.next_node):
                return (None, None)
            return self.get_directions(x, y, heading)

        heading = self._convert_heading_from_map(heading)
        turn_to_angle = heading - degrees(atan2(y_diff, x_diff))
        distance = sqrt(x_diff ** 2 + y_diff ** 2)
        return (turn_to_angle, distance)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Get directions for x, y, heading values'
    )
    parser.add_argument('x', type=int, help='x')
    parser.add_argument('y', type=int, help='y')
    parser.add_argument('heading', type=int, help='heading')
    args = parser.parse_args()

    from maps_repo import MapsRepo
    from find_path import run_dijkstra
    m = MapsRepo()
    graph = m.map('COM1', '2')
    north_heading = m.north_heading('COM1', '2')
    path = run_dijkstra(graph, '1', '10')
    d = DirectionsGenerator(path, graph, north_heading)
    print d.get_directions(args.x, args.y, args.heading)
