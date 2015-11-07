#!/usr/bin/env python
import logging
import sys
import time
from math import atan2, degrees, acos
from collections import deque

from db import DB
from maps_repo import MapsRepo
from prompts_enum import PromptDirn
from audio_driver import AudioDriver
from step_counter import StepCounter
from heading_calculator import HeadingCalculator
from vector_ops import dot_product
from utils import CommonLogger, dijkstra, euclidean_dist, init_logger,\
    normalize_360, now


LOG_FILENAME = '/home/pi/logs/navi.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)

STEP_LENGTH = 40.0
ANGLE_THRESHOLD = 20


class Navigator(object):

    def __init__(self, logger):
        self.log = logger
        self.log.info('Starting navigator...')
        self.db = DB(logger)
        self.maps = MapsRepo()
        self.audio = AudioDriver()
        self.sc = StepCounter(logger)
        self.hc = HeadingCalculator(logger)
        self.current_prompt = None
        self.navigation_finished = False

    @property
    def next_node(self):
        return self.graph[self.next_node_id]

    @property
    def next_node_id(self):
        return self.path[self.next_node_idx]

    @property
    def current_node(self):
        return self.graph[self.current_node_id]

    @property
    def current_node_id(self):
        return self.path[self.next_node_idx - 1]

    @property
    def prev_node(self):
        prev_node_id = self.prev_node_id
        if prev_node_id:
            return self.graph[prev_node_id]
        else:
            return None

    @property
    def prev_node_id(self):
        if self.next_node_idx >= 2:
            return self.path[self.next_node_idx - 2]
        else:
            return None

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
        self.navigation_finished = False
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
        self.next_node_idx = 1

    def _align_to_next_node(self, num_of_steps_to_next_node):
        self.log.info("Aligning...")
        angle_to_turn = self._calc_angle_to_turn(
            self.prev_node['x'], self.prev_node['y'],
            self.current_node['x'], self.current_node['y'],
            self.next_node['x'], self.next_node['y']
        )
        # straight ahead
        if angle_to_turn == 0:
            self.audio.prompt(PromptDirn.straight, num_of_steps_to_next_node)
            return
        # turn needed
        if angle_to_turn > 0:
            self.audio.prompt(PromptDirn.left, angle_to_turn)
        else:
            self.audio.prompt(PromptDirn.right, angle_to_turn)
        self._wait_for_angle_turn(angle_to_turn)
        self.audio.prompt(PromptDirn.straight, num_of_steps_to_next_node)

    def _wait_for_angle_turn(self, angle_to_turn):
        self.log.info("Waiting for turn by %d", angle_to_turn)
        timestamp = now()
        back_data = self.db.fetch_data(sid=0, since=timestamp)
        timestamp = back_data[-1][0]
        self.hc.clear_filter()
        current_heading = self.hc.get_heading(back_data)
        turned_angle = 0
        while abs(turned_angle - angle_to_turn) > ANGLE_THRESHOLD:
            back_data = self.db.fetch_data(sid=0, since=timestamp)
            timestamp = back_data[-1][0]
            heading = self.hc.get_heading(back_data)
            turned_angle = abs(current_heading - heading)
            self.log.info("Turned angle: %d", turned_angle)
        self.log.info("Completed turn")

    def _wait_for_steps(self, num_of_steps_to_wait):
        self.log.info("Waiting for %d steps", num_of_steps_to_wait)
        counted_steps = 0
        timestamp = now()
        while counted_steps != num_of_steps_to_wait:
            foot_data = self.db.fetch_data(sid=1, since=timestamp)
            timestamp = foot_data[-1][0]
            for d in [d[2] for d in foot_data]:
                is_step_detected = self.sc.detect_step(d)
                if is_step_detected:
                    self.audio.prompt_step()
                    counted_steps += 1
                    self.log.info("Counted steps: %d", counted_steps)
                if counted_steps == num_of_steps_to_wait:
                    break
        self.log.info("Completed steps")

    def _calc_num_steps_to_next_node(self):
        distance = euclidean_dist(
            self.current_node['x'], self.current_node['y'],
            self.next_node['x'], self.next_node['y']
        )
        num_of_steps_to_next_node = int(round(distance / STEP_LENGTH))
        self.log.info("Steps to walk: " + str(num_of_steps_to_next_node))
        return num_of_steps_to_next_node

    def _navigate_to_next_node(self):
        num_of_steps_to_next_node = self._calc_num_steps_to_next_node()
        self._align_to_next_node(num_of_steps_to_next_node)
        self._wait_for_steps(num_of_steps_to_next_node)
        self._node_reached()

    def _node_reached(self):
        self.audio.prompt_node_reached(self.next_node_id)
        self.current_prompt = None
        self.log.info('Reached node %s', self.next_node_id)
        if self.current_node['name'] == 'Stairwell':
            self.audio.prompt_stairs()
        self.next_node_idx += 1
        if self.next_node_idx == len(self.path):
            self.log.info('Reached destination node')
            self.stop()
        else:
            self.log.info('Navigating to node %s', self.next_node_id)

    def _calc_angle_to_turn(x1, y1, x2, y2, x3, y3):
        if x1 is None or y1 is None:
            true_angle = self._calc_true_angle()
            v_a = [(x1 - x2), (y1 - y2)]
            v_b = [1, 0]
            angle_to_turn_to = self._angle_bw_vectors(v_a, v_b)
            return angle_to_turn_to - true_angle
        v_a = [(x1 - x2), (y1 - y2)]
        v_b = [(x2 - x3), (y2, - y3)]
        return self._angle_bw_vectors(v_a, v_b)

    def _calc_true_angle(self, x1, y1, x2, y2):
        back_data = self.db.fetch_data(sid=0, since=now())
        self.hc.clear_filter()
        self.hc.set_map_north(self.north)
        return self.hc.get_heading(back_data, true_heading=True)

    def _angle_bw_vectors(v_a, v_b):
        d = dot_product(v_a, v_b)
        mag_a = dot_product(v_a, v_a) ** 0.5
        mag_b = dot_product(v_b, v_b) ** 0.5
        cos_val = d / mag_a / mag_b
        return normalize_360(degrees(acos(cos_val)))

    def _play_prompt(self, prompt, angle, dist):
        val = dist if prompt == PromptDirn.straight else angle
        if self.current_prompt is None or self.current_prompt != prompt:
            self.audio.prompt(prompt, val)
            self.audio_offset = 0
        elif prompt == PromptDirn.left or prompt == PromptDirn.right:
            self.audio_offset += 1
        if self.audio_offset == self.audio_delay:
            self.audio_offset = 0
            self.audio.prompt(prompt, val)

    def start(self):
        self._wait_for_origin_and_destination()
        self._generate_chunks()
        while len(self.navi_chunks) != 0:
            self._prepare_for_next_navi_chunk()
            self._get_map()
            self._generate_path()
            while not self.navigation_finished:
                self._navigate_to_next_node()
            self.navi_chunks.pop(0)
        self.audio.prompt(PromptDirn.end)

    def stop(self):
        self.navigation_finished = True


nav = Navigator(logger)
nav.start()
