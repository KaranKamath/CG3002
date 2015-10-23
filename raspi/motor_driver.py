import RPi.GPIO as GPIO
from prompts_enum import PromptDirn


class MotorDriver(object):
    GPIO_PIN_CENTER = 12
    GPIO_PIN_LEFT = 16
    GPIO_PIN_RIGHT = 18

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.GPIO_PIN_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_RIGHT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_CENTER, GPIO.OUT)
        GPIO.output(self.GPIO_PIN_LEFT, False)
        GPIO.output(self.GPIO_PIN_RIGHT, False)
        GPIO.output(self.GPIO_PIN_CENTER, False)

    def left_motor(self, val):
        GPIO.output(self.GPIO_PIN_LEFT, val)

    def right_motor(self, val):
        GPIO.output(self.GPIO_PIN_RIGHT, val)

    def center_motor(self, val):
        GPIO.output(self.GPIO_PIN_CENTER, val)

if __name__ == '__main__':
    import time
    f = MotorDriver()
    f.left_motor(True)
    time.sleep(5)
    f.left_motor(False)
