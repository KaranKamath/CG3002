from math import atan2, pi
from utils import normalize_360

ACC_SENSITIVITY = 8192
GYRO_SENSITIVITY = 65.536
dt = 0.1


def get_new_heading(angle, accData, gyroData):
    angle += gyroData[0] * dt / GYRO_SENSITIVITY
    forceMagnitudeApprox = sum([abs(x) for x in accData])
    if ACC_SENSITIVITY < forceMagnitudeApprox < (4 * ACC_SENSITIVITY):
        print "inside\n"
        heading_acc = atan2(accData[1], accData[2]) * 180.0 / pi
        angle = 0.98 * angle + 0.02 * heading_acc
    return normalize_360(angle)
