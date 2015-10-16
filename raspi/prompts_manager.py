import os
from sys import platform as _platform
from subprocess import Popen

BASE_AUDIO_DIR = '/home/pi/cg3002/audio/'


class PromptsManager():

    PROMPTS = {
        'left': 'left.wav',
        'right': 'right.wav',
        'straight': 'straight.wav',
        'finish': 'dest_reached.wav'
    }
    PLAYER = 'afplay' if _platform == 'darwin' else 'aplay'

    def __init__(self):
        self.devnull = open(os.devnull, 'w')
        self.proc = None

    def prompt(self, prompt_type):
        if self.proc:
            self.proc.kill()
        self.proc = Popen(
            [self.PLAYER, BASE_AUDIO_DIR + self.PROMPTS[prompt_type]],
            stdout=self.devnull, stderr=self.devnull
        )

if __name__ == '__main__':
    from time import sleep
    obj = PromptsManager()
    obj.prompt('left')
    sleep(0.5)
    obj.prompt('finish')
    sleep(1)
    obj.prompt('right')
