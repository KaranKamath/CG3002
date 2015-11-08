from math import sqrt, degrees, atan2, pi
from scipy.signal import medfilt

from vector_ops import dot_3d, cross_3d, normalize_3d
from utils import euclidean_dist, normalize_360


# M_BIAS = [-422.405, -405.466, -453.233]
# M_TRANSFORMATION = [[4.959, 0.327, -0.062],
#                     [-0.27, 6.317, 2.767],
#                     [-0.983, 2.703, 9.556]]

M_BIAS = [-171.524, -261.43, -404.003]
M_TRANSFORMATION = [[9.578, -1.035, -3.597],
                    [-5.67, 6.852, 2.744],
                    [1.82, -0.84, 8.638]]


class HeadingCalculator():

    def __init__(self, logger):
        self.log = logger
        self.median_window = []
        self.map_north = 0

    def set_map_north(self, map_north):
        self.map_north = map_north

    def get_heading(self, imu_data):
        heading = None
        for data in imu_data:
            a = data[1:4]
            m = self._transform_m(data[4:7])
            f = [0, 0, 1]
            heading = self._filter_heading(
                self._calculate_raw_heading(a, m, f))
        if not heading:
            return 0
        return self._convert_heading_to_horizontal_axis(heading)

    def _transform_m(self, m):
        m[0] -= M_BIAS[0]
        m[1] -= M_BIAS[1]
        m[2] -= M_BIAS[2]
        return [dot_3d(M_TRANSFORMATION[0], m),
                dot_3d(M_TRANSFORMATION[1], m),
                dot_3d(M_TRANSFORMATION[2], m)]

    def _calculate_raw_heading(self, a, m, f):
        e = normalize_3d(cross_3d(m, a))
        n = normalize_3d(cross_3d(a, e))
        heading = atan2(dot_3d(e, f), dot_3d(n, f)) * 180 / pi
        return int(round((heading + 360) if heading < 0 else heading))

    def _filter_heading(self, heading):
        self.median_window.append(heading)
        if len(self.median_window) <= 5:
            return heading
        self.median_window = self.median_window[1:]
        filtered_heading = medfilt(self.median_window, 5)[2]
        return filtered_heading

    def _convert_heading_to_horizontal_axis(self, heading):
        return normalize_360(90 - self.map_north - heading)


if __name__ == '__main__':
    import logging
    obj = HeadingCalculator(logging.getLogger(__name__))
    obj.get_heading([])
