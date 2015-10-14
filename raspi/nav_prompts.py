import os
from sys import platform as _platform
from subprocess import Popen


class NavPrompts(object):

    PROMPTS = {
        'left': 'audio/left.wav',
        'right': 'audio/right.wav',
        'straight': 'audio/straight.wav',
        'finish': 'audio/dest_reached.wav'
    }
    PLAYER = 'afplay' if _platform == 'darwin' else 'aplay'

    def __init__(self):
        self.devnull = open(os.devnull, 'w')
        self.process = None

    def prompt(self, prompt_type):
        if self.process:
            self.process.kill()
        self.process = Popen([self.PLAYER, self.PROMPTS[prompt_type]],
                             stdout=self.devnull, stderr=self.devnull)

if __name__ == '__main__':
    from time import sleep
    obj = NavPrompts()
    obj.prompt('left')
    sleep(0.5)
    obj.prompt('finish')
    sleep(1)
    obj.prompt('right')
