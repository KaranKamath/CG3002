#!/usr/bin/env python
import argparse
import logging
import sys
import time
from math import atan2, degrees
from collections import deque

from db import DB
from maps_repo import MapsRepo
from prompts_enum import PromptDirn
from directions_utils import normalize
from audio_driver import AudioDriver
from utils import CommonLogger, dijkstra, euclidean_dist, init_logger


LOG_FILENAME = '/home/pi/logs/navi.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)


class Navigator(object):

    ANGLE_THRESHOLD = 20
    RELAXED_ANGLE_THRESHOLD = 10
    DISTANCE_THRESHOLD = 150
    location_tstmp = 0
    audio_delay = 6  # 0.5s * 6 = 3s
    audio_offset = 0

    def __init__(self, logger):
        self.log = logger
        self.log.info('Starting navigator...')
        self.db = DB(logger)
        self.maps = MapsRepo()
        self.audio = AudioDriver()
        self.current_prompt = None
        self.navigation_finished = False

    @property
    def next_node(self):
        return self.graph[self.next_node_id]

    @property
    def next_node_id(self):
        return self.path[self.next_node_idx]

    @property
    def user_location(self):
        ts, x, y, h, alt, is_reset = self.db.fetch_location(allow_reset=False)
        return (x, y, h, alt)

    def _wait_for_origin_and_destination(self):
        self.log.info('Waiting for origin and destination...')
        data = self.db.fetch_origin_and_destination()
        self.o_bldg, self.o_level, self.o_node = data[0], data[1], data[2]
        self.d_bldg, self.d_level, self.d_node = data[3], data[4], data[5]
        self.log.info('Got %s-%s-%s to %s-%s-%s',
                      self.o_bldg, self.o_level, self.o_node,
                      self.d_bldg, self.d_level, self.d_node)

    def _generate_chunks(self):
        if self.o_bldg != self.d_bldg or self.o_level != self.d_level:
            self.log.info('Creating multiple navi chunks')
            maps_to_visit = self._find_maps_to_visit()
            self.log.info('Will visit maps: ' + str(maps_to_visit))
            self.navi_chunks = []
            navi_chunk = [(self.o_bldg, self.o_level, self.o_node)]
            for i in range(len(maps_to_visit[:-1])):
                curr_bldg, curr_lvl = maps_to_visit[i]
                n_bldg, n_lvl = maps_to_visit[i + 1]
                conns = self.maps.connectors(curr_bldg, curr_lvl)
                n_conns = self.maps.connectors(n_bldg, n_lvl)
                navi_chunk.append((curr_bldg, curr_lvl, conns[n_bldg][n_lvl]))
                self.navi_chunks.append(navi_chunk)
                navi_chunk = [(n_bldg, n_lvl, n_conns[curr_bldg][curr_lvl])]
            dst_map_conns = self.maps.connectors(self.d_bldg, self.d_level)
            last_dst = self.navi_chunks[-1][-1]
            dst_map_start_node = dst_map_conns[last_dst[0]][last_dst[1]]
            self.navi_chunks.append([
                (self.d_bldg, self.d_level, dst_map_start_node),
                (self.d_bldg, self.d_level, self.d_node)
            ])
            self.log.info("Generated chunks: " + str(self.navi_chunks))
        else:
            self.log.info('Creating single navi chunk')
            self.navi_chunks = [(
                (self.o_bldg, self.o_level, self.o_node),
                (self.d_bldg, self.d_level, self.d_node)
            )]

    def _find_maps_to_visit(self):
        dist = {(self.o_bldg, self.o_level): 0}
        parent = {}
        to_visit = deque()
        to_visit.append((self.o_bldg, self.o_level))
        ended = False
        while len(to_visit) != 0:
            bldg, level = to_visit.popleft()
            if (bldg, level) == (self.d_bldg, self.d_level):
                break
            connections = self.maps.connectors(bldg, level)
            for b in connections:
                for l in connections[b]:
                    if (b, l) not in dist:
                        dist[(b, l)] = dist[(bldg, level)] + 1
                        parent[(b, l)] = (bldg, level)
                        to_visit.append((b, l))
        if (self.d_bldg, self.d_level) not in parent:
            raise RuntimeError("No path from origin to destination! :O")

        curr = (self.d_bldg, self.d_level)
        maps_to_visit = [curr]
        while curr != (self.o_bldg, self.o_level):
            curr = parent[curr]
            maps_to_visit.append(curr)
        return maps_to_visit[::-1]

    def _prepare_for_next_navi_chunk(self):
        current_chunk = self.navi_chunks[0]
        self.building = current_chunk[0][0]
        self.level = current_chunk[0][1]
        self.origin = current_chunk[0][2]
        self.destination = current_chunk[1][2]
        self.log.info("Switching to %s-%s", self.building, self.level)
        self.log.info("Endpoints %s-%s", self.origin, self.destination)

    def _get_map(self):
        self.graph = self.maps.map(self.building, self.level)
        self.north = self.maps.north_heading(self.building, self.level)
        self.db.insert_location(self.graph[self.origin]['x'],
                                self.graph[self.origin]['y'],
                                self.north, 0, is_reset=True)

    def _generate_path(self):
        self.log.info('Generating path...')
        self.path = dijkstra(self.graph, self.origin, self.destination)
        self.log.info('Got path: %s', str(self.path))

    def _acquire_next_node(self):
        x, y, heading, alt = self.user_location
        min_dist = sys.maxint
        min_dist_node_idx = 0
        for i in range(len(self.path)):
            node = self.path[i]
            node_x = self.graph[node]['x']
            node_y = self.graph[node]['y']
            dist = euclidean_dist(node_x, node_y, x, y)
            if dist < min_dist and dist > self.DISTANCE_THRESHOLD:
                min_dist = dist
                min_dist_node_idx = i
        self.next_node_idx = min_dist_node_idx

    def _navigate_to_next_node(self):
        x, y, heading, alt = self.user_location
        dist, angle = self._calc_directions(x, y, self.next_node['x'],
                                            self.next_node['y'], heading)

        self.log.info('Next node %s @[%scm, %sdeg]', self.next_node_id,
                      dist, angle)
        if self._node_reached(dist, angle):
            self.audio.prompt_node_reached(self.next_node_id)
            self.log.info('Reached node %s', self.next_node_id)
            self.next_node_idx += 1
            if self.next_node_idx == len(self.path):
                self.log.info('Reached destination node')
                self.stop()
            else:
                self.log.info('Navigating to node %s', self.next_node_id)
                self._navigate_to_next_node()
        else:
            new_prompt = self._generate_prompt(angle)
            self._play_prompt(new_prompt, angle)
            self.current_prompt = new_prompt

    def _node_reached(self, dist, angle):
        node_reached = (dist < self.DISTANCE_THRESHOLD)
        return node_reached

    def _calc_directions(self, x, y, node_x, node_y, heading):
        distance = int(round(euclidean_dist(node_x, node_y, x, y)))
        if distance < self.DISTANCE_THRESHOLD:
            return (distance, 0)
        turn_to_angle = degrees(atan2(node_y - y, node_x - x)) - heading
        return (distance, int(round(normalize(turn_to_angle))))

    def _generate_prompt(self, angle):
        if abs(angle) < self.ANGLE_THRESHOLD:
            if self.current_prompt is None or \
                    (abs(angle) <= self.RELAXED_ANGLE_THRESHOLD and
                     (self.current_prompt == PromptDirn.right or
                      self.current_prompt == PromptDirn.left)):
                new_prompt = PromptDirn.straight
            else:
                new_prompt = self.current_prompt
        elif angle > 0:
            new_prompt = PromptDirn.left
        else:
            new_prompt = PromptDirn.right
        return new_prompt

    def _play_prompt(self, prompt, angle):
        if self.current_prompt is None or self.current_prompt != prompt:
            self.audio.prompt(prompt, angle)
            self.audio_offset = 0
        elif prompt == PromptDirn.left or prompt == PromptDirn.right:
            self.audio_offset += 1
            if self.audio_offset == self.audio_delay:
                self.audio_offset = 0
                self.audio.prompt(prompt, angle)

    def start(self):
        self._wait_for_origin_and_destination()
        self._generate_chunks()
        while len(self.navi_chunks) != 0:
            self._prepare_for_next_navi_chunk()
            self._get_map()
            self._generate_path()
            self._acquire_next_node()
            while not self.navigation_finished:
                self._navigate_to_next_node()
                time.sleep(0.5)
            self.navi_chunks.pop(0)

    def stop(self):
        self.navigation_finished = True
        self.current_prompt = PromptDirn.end
        self.audio.prompt(self.current_prompt)


nav = Navigator(logger)
nav.start()
