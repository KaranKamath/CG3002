import time
import logging
from scipy.signal import medfilt
from db import DB
from utils import CommonLogger, init_logger


LOG_FILENAME = '/home/pi/logs/localizer.log'
logger = init_logger(logging.getLogger(__name__), LOG_FILENAME)
sys.stdout = CommonLogger(logger, logging.INFO)
sys.stderr = CommonLogger(logger, logging.ERROR)

DELTA_TIME = 1000  # 1 second
LEFT = 90
RIGHT = -90
AROUND_LEFT = 180
AROUND_RIGHT = -180
STRAIGHT = 0

THRESHOLD_STRAIGHT_LEFT = 20
THRESHOLD_STRAIGHT_RIGHT = -20
THRESHOLD_LEFT = 160
THRESHOLD_RIGHT = -160
THRESHOLD_MID_LEFT = 90
THRESHOLD_MID_RIGHT = -90

MEDIAN_WINDOW = 5
MAX_SENSOR_VAL = 301


class ObstacleDetector(object):

    def __init__(self, db, logger):
        self.past_vals = []
        self.db = db
        self.logger = logger

    def get_current_data(self):
        one_second_ago = int(round(time.time() * 1000) - DELTA_TIME)
        fetched_data = self.db.fetch_data(sid=1, since=one_second_ago)

        if not fetched_data:
            self.logger.info('No data fetched by obstacle detector')
            return []

        fetched_data = sorted(fetched_data, key=lambda x: x[0])

        latest_data = [x[2] for x in fetched_data][-1]

        # clean up 0s
        for i in range(len(latest_data)):
            if latest_data[i] == 0:
                latest_data[i] = MAX_SENSOR_VAL

        self.past_vals.append(latest_data)

        if len(self.past_vals) > MEDIAN_WINDOW:
            self.past_vals = self.past_vals[(-1 * MEDIAN_WINDOW):]
        else:
            self.logger.info(
                'Not enough data to filter, returning raw: %s', latest_data)
            return latest_data

        self.logger.info('Selecting latest data: %s', latest_data)

        filtered_vals = []
        filtered_vals.append(medfilt(
            [x[0] for x in self.past_vals], MEDIAN_WINDOW)[2])
        filtered_vals.append(medfilt(
            [x[1] for x in self.past_vals], MEDIAN_WINDOW)[2])
        filtered_vals.append(medfilt(
            [x[2] for x in self.past_vals], MEDIAN_WINDOW)[2])
        filtered_vals.append(medfilt(
            [x[3] for x in self.past_vals], MEDIAN_WINDOW)[2])

        self.logger.info('Filtered Values: %s', filtered_vals)

        return filtered_vals

    def has_crossed_threshold(self, value):
        if 0 < value < 100:
            return True
        return False

    def get_obstacle_map(self, vals):
        if len(vals) == 0:
            self.logger.info('Cannot create map due to data missing')
            return None

        obstacle_map = {}

        obstacle_map['up'] = self.has_crossed_threshold(vals[0])
        obstacle_map['left'] = self.has_crossed_threshold(vals[1])
        obstacle_map['right'] = self.has_crossed_threshold(vals[2])
        obstacle_map['bottom'] = self.has_crossed_threshold(vals[3])

        self.logger.info('Obstacle map: %s', obstacle_map)

        return obstacle_map

    def turn(self, current_angle, delta):
        raw_final_angle = current_angle + (delta % 360)

        if raw_final_angle > 180:
            return -180 + (raw_final_angle - 180)

        if raw_final_angle < -180:
            return 180 + (180 + raw_final_angle)

        return raw_final_angle

    def apply_straight_policy(self, current_angle_recommendation, obstacle_map):
        # No obstacle in front
        if not obstacle_map['up']:
            return current_angle_recommendation

        # Obstacles all around
        if obstacle_map['left'] and obstacle_map['right']:
            return AROUND_LEFT

        # Obstacle on the front and left but not right
        if obstacle_map['left']:
            return RIGHT

        # Obstacle on the front and right but not left
        if obstacle_map['right']:
            return LEFT

        # No obstacles on the side, but on the front
        if current_angle_recommendation >= 0:
            return LEFT
        return RIGHT

    def apply_left_turn_policy(self, current_angle_recommendation, obstacle_map):
        # No obstacle on the left
        if not obstacle_map['left']:
            return current_angle_recommendation

        # Obstacles all around
        if obstacle_map['up'] and obstacle_map['right']:
            return AROUND_LEFT

        # Obstacle up front and left
        if obstacle_map['up']:
            return RIGHT

        # Obstacle right and left, but not straight, or just the left
        if current_angle_recommendation >= THRESHOLD_MID_LEFT:
            return AROUND_LEFT

        return STRAIGHT

    def apply_right_turn_policy(self, current_angle_recommendation,
                                obstacle_map):
        # No obstacle on the right
        if not obstacle_map['right']:
            return current_angle_recommendation

        # Obstacles all around
        if obstacle_map['up'] and obstacle_map['left']:
            return AROUND_RIGHT

        # Obstacle up front and right, but not left
        if obstacle_map['up']:
            return LEFT

        # Obstacle left and right, but not straight, or just the right
        if current_angle_recommendation <= THRESHOLD_MID_RIGHT:
            return AROUND_RIGHT

        return STRAIGHT

    def apply_turn_around_policy(self, current_angle_recommendation,
                                 obstacle_map):
        if current_angle_recommendation >= 0:
            return AROUND_LEFT
        return AROUND_RIGHT

    def recommend(self, current_angle_recommendation):
        obstacle_map = self.get_obstacle_map(self.get_current_data())

        if obstacle_map is None:
            self.logger.info(
                'Defaulting to return without changing recommendation')
            return current_angle_recommendation

        self.logger.info('Angle to modify: %s', current_angle_recommendation)

        if THRESHOLD_STRAIGHT_RIGHT <= current_angle_recommendation <= THRESHOLD_STRAIGHT_LEFT:
            self.logger.info('Applying straight policy...')
            return self.apply_straight_policy(current_angle_recommendation, obstacle_map)
        elif THRESHOLD_RIGHT <= current_angle_recommendation < THRESHOLD_STRAIGHT_RIGHT:
            self.logger.info('Applying right policy...')
            return self.apply_right_turn_policy(current_angle_recommendation, obstacle_map)
        elif THRESHOLD_STRAIGHT_LEFT < current_angle_recommendation <= THRESHOLD_LEFT:
            self.logger.info('Applying left policy...')
            return self.apply_left_turn_policy(current_angle_recommendation, obstacle_map)

        self.logger.info('Applying turn around policy...')

        return self.apply_turn_around_policy(current_angle_recommendation, obstacle_map)

    def start(self):
        """ This runs in the daemon """
        while True:
            pass

obsdet = ObstacleDetector(logger)
obsdet.start()
