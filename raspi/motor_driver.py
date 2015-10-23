import RPi.GPIO as GPIO
from prompts_enum import PromptDirn


class MotorDriver(object):
    GPIO_PIN_LEFT = 16
    GPIO_PIN_RIGHT = 18

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.GPIO_PIN_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_RIGHT, GPIO.OUT)
        GPIO.output(self.GPIO_PIN_LEFT, False)
        GPIO.output(self.GPIO_PIN_RIGHT, False)

    def _left_motor(self, val):
        GPIO.output(self.GPIO_PIN_LEFT, val)

    def _right_motor(self, val):
        GPIO.output(self.GPIO_PIN_RIGHT, val)

    def prompt(self, val):
        self._left_motor(False)
        self._right_motor(False)
        if val == PromptDirn.left:
            self._left_motor(True)
        elif val == PromptDirn.right:
            self._right_motor(True)

if __name__ == '__main__':
    import time
    f = MotorDriver()
    f._left_motor(True)
    time.sleep(5)
    f._left_motor(False)
