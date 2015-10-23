import RPi.GPIO as GPIO
from prompts_enum import PromptDirn


class MotorDriver(object):
    GPIO_PIN_CENTER = 12
    GPIO_PIN_LEFT = 16
    GPIO_PIN_RIGHT = 18
    PWM_FREQ = 50000
    VALUE_ERROR = "Got invalid value for PWM"

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.GPIO_PIN_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_RIGHT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_CENTER, GPIO.OUT)
        self.left = GPIO.PWM(self.GPIO_PIN_LEFT, self.PWM_FREQ)
        self.right = GPIO.PWM(self.GPIO_PIN_RIGHT, self.PWM_FREQ)
        self.center = GPIO.PWM(self.GPIO_PIN_CENTER, self.PWM_FREQ)
        self.left.start(0)
        self.right.start(0)
        self.center.start(0)

    def left_motor(self, val):
        if val >= 0 and val <= 100:
            self.left.ChangeDutyCycle(val)
        else:
            raise ValueError(self.VALUE_ERROR)

    def right_motor(self, val):
        if val >= 0 and val <= 100:
            self.right.ChangeDutyCycle(val)
        else:
            raise ValueError(self.VALUE_ERROR)

    def center_motor(self, val):
        if val >= 0 and val <= 100:
            self.center.ChangeDutyCycle(val)
        else:
            raise ValueError(self.VALUE_ERROR)

if __name__ == '__main__':
    import time
    f = MotorDriver()
    f.left_motor(50)
    time.sleep(5)
    f.left_motor(100)
