import json
import re
import requests
import pickle
import os.path as osp

CACHE = osp.join(osp.dirname(osp.realpath(__file__)), 'cache', '{0}-{1}.map')
MAP_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'\
          'Building={building}&Level={level}'
SPLIT_RE = re.compile('\s*,\s*')
CONNECT_RE = re.compile('TO (?P<bldg>\d+)-(?P<level>\d+)-(?P<node>\d+)')


class MapsRepo(object):

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

    def connectors(self, building, level):
        key = self._key_generator(building, level)
        if key in self._maps:
            return self._maps[key]['connectors']
        self._fetch_map(building, level)
        return self._maps[key]['connectors']

    def _fetch_map(self, building, level):
        key = self._key_generator(building, level)
        raw_map = self._get_raw_map(building, level)
        processed_map = self._process_raw_map(raw_map)
        connectors = self._find_connectors(processed_map)
        self._maps[key] = {
            'map': processed_map,
            'north': int(raw_map['info']['northAt']) if raw_map['info'] else 0,
            'connectors': connectors
        }

    def _get_raw_map(self, building, level):
        cache_file = CACHE.format(building, level)
        if osp.exists(cache_file):
            with open(cache_file) as f:
                map_data = pickle.load(f)
            return map_data
        r = requests.get(MAP_URL.format(building=building, level=level))
        map_data = r.json()
        with open(cache_file, 'w') as f:
            pickle.dump(map_data, f)
        return map_data

    def _process_raw_map(self, raw_map):
        graph = {}
        for node in raw_map['map']:
            graph[str(node['nodeId'])] = {
                'linkTo': SPLIT_RE.split(str(node['linkTo']).strip()),
                'x': int(node['x']),
                'y': int(node['y']),
                'name': node['nodeName']
            }
        return graph

    def _find_connectors(self, graph):
        connectors = {}
        for node_id, node in graph.items():
            is_connector = CONNECT_RE.match(node['name'])
            if is_connector:
                bldg = is_connector.group('bldg')
                level = is_connector.group('level')
                if bldg not in connectors:
                    connectors[bldg] = {}
                connectors[bldg][level] = node_id
        return connectors

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Fetch latest map for given building and level'
    )
    parser.add_argument('building', help='building name')
    parser.add_argument('level', help='level name')
    args = parser.parse_args()

    mr = MapsRepo()
    print json.dumps(mr.connectors(args.building, args.level), indent=2)
