import json
import re
import requests


class MapsRepo(object):

    MAP_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'\
              'Building={building}&Level={level}'
    SPLIT_RE = re.compile('\s*,\s*')

    def __init__(self):
        self._maps = {}

    def _key_generator(self, building, level):
        return building + '-' + level

    def map(self, building, level, force_refetch=False):
        key = self._key_generator(building, level)
        if not force_refetch and key in self._maps:
            return self._maps[key]['map']
        self._fetch_map(building, level)
        return self._maps[key]['map']

    def north_heading(self, building, level):
        key = self._key_generator(building, level)
        if key in self._maps:
            return self._maps[key]['north']
        self._fetch_map(building, level)
        return self._maps[key]['north']

    def _fetch_map(self, building, level):
        key = self._key_generator(building, level)
        raw_map = self._get_raw_map(building, level)
        processed_map = self._process_raw_map(raw_map)
        self._maps[key] = {
            'map': processed_map,
            'north': int(raw_map['info']['northAt'])
        }

    def _get_raw_map(self, building, level):
        r = requests.get(self.MAP_URL.format(building=building, level=level))
        return r.json()

    def _process_raw_map(self, raw_map):
        graph = {}
        for node in raw_map['map']:
            graph[str(node['nodeId'])] = {
                'linkTo': self.SPLIT_RE.split(str(node['linkTo']).strip()),
                'x': int(node['x']),
                'y': int(node['y']),
                'name': node['nodeName']
            }
        return graph

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Fetch latest map for given building and level'
    )
    parser.add_argument('building', help='building name')
    parser.add_argument('level', help='level name')
    args = parser.parse_args()

    mr = MapsRepo()
    print json.dumps(mr.map(args.building, args.level), indent=2)
