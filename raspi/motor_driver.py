import RPi.GPIO as GPIO


class MotorDriver():
    GPIO_PIN_LEFT = 23
    GPIO_PIN_RIGHT = 24

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.GPIO_PIN_LEFT, GPIO.OUT)
        GPIO.setup(self.GPIO_PIN_RIGHT, GPIO.OUT)

    def left_motor(self, val=True):
        GPIO.output(self.GPIO_PIN_LEFT, val)

    def right_motor(self, val=True):
        GPIO.output(GPIO_PIN_RIGHT, val)


if __name__ == '__main__':
    f = MotorDriver()
    f.left_motor(True)
