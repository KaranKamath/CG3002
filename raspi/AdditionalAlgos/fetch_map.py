import argparse
import json
import requests

MAP_URL = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'\
          'Building={building}&Level={level}'


def fetch_raw_map(building, level):
    r = requests.get(MAP_URL.format(building=building, level=level))
    return r.json()


def process_raw_map(raw_map):
    processed_map = raw_map
    return processed_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fetch latest map for given building and level'
    )
    parser.add_argument('building', help='building name')
    parser.add_argument('level', help='level name')

    args = parser.parse_args()
    raw_map_data = fetch_raw_map(args.building, args.level)
    print json.dumps(raw_map_data, indent=2)
