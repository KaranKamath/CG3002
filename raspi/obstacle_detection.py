import time
from db import DB

DELTA_TIME = 1000 # 1 second

class ObstacleDetector(Object):

    def __init__(self):
        self.past_maps = []
        self.db = DB()

    def get_current_data(self):
        one_second_ago = int(round(time.time() * 1000) - DELTA_TIME)
        fetched_data = self.db.fetch_data(sid=1, since=one_second_ago)

        if not fetched_data:
            return []

        fetched_data = sorted(fetched_data, key = lambda x: x[0])

        return [x[2] for x in fetched_data][-1]

    def has_crossed_threshold(self, value):
        if value < 100:
            return True
        return False
 
    def get_obstacle_map(self, vals):
        obstacle_map = {}

        obstacle_map['up'] = has_crossed_threshold(vals[0])
        obstacle_map['left'] = has_crossed_threshold(vals[1])
        obstacle_map['right'] = has_crossed_threshold(vals[2])
        obstacle_map['bottom'] = has_crossed_threshold(vals[3])

        return obstacle_map

    def turn(self, current_angle, delta):
        raw_final_angle = current_angle + (delta % 360)

        if raw_final_angle > 180:
            return -180 + (raw_final_angle - 180)

        if raw_final_angle < -180:
            return 180 + (180 + raw_final_angle)

        return raw_final_angle
         
    def recommend(self, current_angle_recommendation, ):
        obstacle_map = self.get_obstacle_map(self.get_current_data())

        if not obstacle_map['up']:
            return current_angle_recommendation

        if obstacle_map['left'] and obstacle_map['right']:
            return self.turn(current_angle_recommendation, 180)

        elif obstacle_map['left']:
            return self.turn(current_angle_recommendation, 90)

        else:
            return self.turn(current_angle_recommendation, -90)

            

