from math import atan2, pi

ACC_SENSITIVITY = 8192
GYRO_SENSITIVITY = 65.536
dt = 0.1

def get_new_heading(angle, accData, gyroData):
    angle += gyroData[2] * dt / GYRO_SENSITIVITY
    forceMagnitudeApprox = sum([abs(x) for x in accData])
    if ACC_SENSITIVITY < forceMagnitudeApprox < (4 * ACC_SENSITIVITY):
        heading_acc = atan2(accData[1], accData[0]) * 180.0 / pi
        angle = 0.98 * angle + 0.02 * heading_acc
    return angle
