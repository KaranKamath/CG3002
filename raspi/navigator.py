#!/usr/bin/env python
import logging
import sys
from collections import deque

from db import DB
from maps_repo import MapsRepo
from prompts_enum import PromptDirn
from audio_driver import AudioDriver
from step_counter import StepCounter
from heading_calculator import HeadingCalculator
import utils
from utils import CommonLogger, init_logger


LOG_FILENAME = '/home/pi/logs/navi.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)

STEP_LENGTH = 40.0
ANGLE_THRESHOLD = 10
FOOT_SENSOR_ID = 0
BACK_SENSOR_ID = 1


class Navigator(object):

    def __init__(self, logger):
        self.log = logger
        self.log.info('Starting navigator...')
        self.db = DB(logger=logger, db_name='uart.db')
        self.maps = MapsRepo()
        self.audio = AudioDriver()
        self.sc = StepCounter(logger)
        self.hc = HeadingCalculator(logger)
        self.current_prompt = None
        self.navi_chunk_finished = False
        self.heading_timestamp = utils.now()

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
            return {'x': None, 'y': None}

    @property
    def prev_node_id(self):
        if self.next_node_idx >= 2:
            return self.path[self.next_node_idx - 2]
        else:
            return None

    def _get_user_heading(self, timestamp=None):
        if timestamp is None:
            timestamp = self.heading_timestamp
        self.hc.clear_filter()
        self.hc.set_map_north(self.north)
        data = self.db.fetch_data(sid=BACK_SENSOR_ID, since=timestamp)
        self.heading_timestamp = data[-1][0]
        return self.hc.get_heading([d[2] for d in data])

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
            self.navi_chunks = self._generate_multiple_chunks(maps_to_visit)
        else:
            self.log.info('Creating single navi chunk')
            self.navi_chunks = [((self.o_bldg, self.o_level, self.o_node),
                                 (self.d_bldg, self.d_level, self.d_node))]
        self.log.info("Generated chunk(s): " + str(self.navi_chunks))

    def _find_maps_to_visit(self):
        dist = {(self.o_bldg, self.o_level): 0}
        parent = {}
        to_visit = deque()
        to_visit.append((self.o_bldg, self.o_level))
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
        maps_to_visit = maps_to_visit[::-1]
        self.log.info('Will visit maps: ' + str(maps_to_visit))
        return maps_to_visit

    def _generate_multiple_chunks(self, maps_to_visit):
        navi_chunks = []
        navi_chunk = [(self.o_bldg, self.o_level, self.o_node)]

        for i in range(len(maps_to_visit[:-1])):
            curr_bldg, curr_lvl = maps_to_visit[i]
            n_bldg, n_lvl = maps_to_visit[i + 1]
            conns = self.maps.connectors(curr_bldg, curr_lvl)
            n_conns = self.maps.connectors(n_bldg, n_lvl)
            navi_chunk.append((curr_bldg, curr_lvl, conns[n_bldg][n_lvl]))
            navi_chunks.append(navi_chunk)
            navi_chunk = [(n_bldg, n_lvl, n_conns[curr_bldg][curr_lvl])]

        dst_map_conns = self.maps.connectors(self.d_bldg, self.d_level)
        last_dst = navi_chunks[-1][-1]
        dst_map_start_node = dst_map_conns[last_dst[0]][last_dst[1]]
        navi_chunks.append([(self.d_bldg, self.d_level, dst_map_start_node),
                            (self.d_bldg, self.d_level, self.d_node)])
        return navi_chunks

    def _prepare_for_next_navi_chunk(self):
        current_chunk = self.navi_chunks[0]
        self.building = current_chunk[0][0]
        self.level = current_chunk[0][1]
        self.origin = current_chunk[0][2]
        self.destination = current_chunk[1][2]
        self.navi_chunk_finished = False
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
        self.path = utils.dijkstra(self.graph, self.origin, self.destination)
        self.next_node_idx = 1
        self.log.info('Got path: %s', str(self.path))

    def _wait_for_chunk_to_finish(self):
        while not self.navi_chunk_finished:
            self._navigate_to_next_node()

    def _navigate_to_next_node(self):
        self._align_to_next_node()
        self._wait_for_steps_to_next_node()
        self._node_reached()

    def _align_to_next_node(self):
        self.log.info("Aligning...")
        angle_to_turn = self._calc_angle_to_turn(
            self.prev_node['x'], self.prev_node['y'],
            self.current_node['x'], self.current_node['y'],
            self.next_node['x'], self.next_node['y']
        )
        if angle_to_turn == 0:
            self.log.info("No alignment needed")
        else:
            if angle_to_turn > 0:
                self.log.info("Left turn by %d", angle_to_turn)
                self.audio.prompt(PromptDirn.left, angle_to_turn)
            else:
                self.log.info("Right turn by %d", angle_to_turn)
                self.audio.prompt(PromptDirn.right, angle_to_turn)
            self._wait_for_angle_turn(angle_to_turn)

    def _calc_angle_to_turn(self, x1, y1, x2, y2, x3, y3):
        if x1 is None or y1 is None:  # No prev node (initial alignment)
            v_a = [1, 0]
            v_b = [(x3 - x2), (y3 - y2)]
            node_heading = utils.angle_bw_vectors(v_a, v_b)
            user_heading = self._get_user_heading(timestamp=utils.now())
            return utils.normalize_360(node_heading - user_heading)
        else:
            v_a = [(x2 - x1), (y2 - y1)]
            v_b = [(x3 - x2), (y3 - y2)]
            return utils.angle_bw_vectors(v_a, v_b)

    def _wait_for_angle_turn(self, angle_to_turn):
        self.log.info("Waiting for turn...")

        initial_heading = self._get_user_heading(timestamp=utils.now())
        self.log.info("Initial heading: %d", initial_heading)

        turned_angle = 0
        while abs(turned_angle - angle_to_turn) > ANGLE_THRESHOLD:
            user_heading = self._get_user_heading()
            turned_angle = user_heading - initial_heading
            self.log.info("Angle turned: %d (= %d - %d)", turned_angle,
                          initial_heading, user_heading)
        self.log.info("Turn complete")

    def _wait_for_steps_to_next_node(self):
        num_of_steps_to_next_node = self._calc_num_steps_to_next_node()
        self.audio.prompt(PromptDirn.straight, num_of_steps_to_next_node)
        self._wait_for_steps(num_of_steps_to_next_node)

    def _calc_num_steps_to_next_node(self):
        dist = utils.euclidean_dist(
            self.current_node['x'], self.current_node['y'],
            self.next_node['x'], self.next_node['y']
        )
        num_of_steps_to_next_node = int(round(dist / STEP_LENGTH))
        self.log.info("%d steps to next node", num_of_steps_to_next_node)
        return num_of_steps_to_next_node

    def _wait_for_steps(self, num_of_steps_to_wait):
        self.log.info("Waiting for steps...")
        counted_steps = 0
        timestamp = utils.now()
        while counted_steps < num_of_steps_to_wait:
            data = self.db.fetch_data(sid=FOOT_SENSOR_ID, since=timestamp)
            timestamp = data[-1][0]
            for data_pt in [x[2] for x in data]:
                if self.sc.detect_step(data_pt):
                    counted_steps += 2
                    self.log.info("Counted steps: %d", counted_steps)
                    self.audio.prompt_step()
                if counted_steps >= num_of_steps_to_wait:
                    break
        self.log.info("Completed steps")

    def _node_reached(self):
        self.current_prompt = None
        self.audio.prompt_node_reached(self.next_node_id)
        self.log.info('Reached node %s', self.next_node_id)
        if self.next_node['name'] == 'Stairwell':
            self.audio.prompt_stairs()
        self.next_node_idx += 1
        if self.next_node_idx == len(self.path):
            self.navi_chunk_finished = True
            self.log.info('Reached destination node')
        else:
            self.log.info('Navigating to node #%d %s',
                          self.next_node_id, self.next_node['name'])

    def start(self):
        self._wait_for_origin_and_destination()
        self._generate_chunks()
        while len(self.navi_chunks) != 0:
            self._prepare_for_next_navi_chunk()
            self._get_map()
            self._generate_path()
            self._wait_for_chunk_to_finish()
            self.navi_chunks.pop(0)
        self.audio.prompt(PromptDirn.end)


nav = Navigator(logger)
nav.start()
