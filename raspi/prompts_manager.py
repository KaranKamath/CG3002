import os
from sys import platform as _platform
from subprocess import Popen

BASE_AUDIO_DIR = '/home/pi/cg3002/audio/'


class PromptsManager():

    PROMPTS = {
        'left': BASE_AUDIO_DIR + 'left.wav',
        'right': BASE_AUDIO_DIR + 'right.wav',
        'straight': BASE_AUDIO_DIR + 'straight.wav',
        'finish': BASE_AUDIO_DIR + 'dest_reached.wav'
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
    obj = PromptsManager()
    obj.prompt('left')
    sleep(0.5)
    obj.prompt('finish')
    sleep(1)
    obj.prompt('right')
