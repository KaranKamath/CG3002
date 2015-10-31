import os
from sys import platform as _platform
from subprocess import Popen, call
from prompts_enum import PromptDirn

BASE_AUDIO_DIR = '/home/pi/cg3002/audio/'


class AudioDriver(object):

    PROMPTS = {
        PromptDirn.left: 'left.wav',
        PromptDirn.right: 'right.wav',
        PromptDirn.straight: 'straight.wav',
        PromptDirn.end: 'dest_reached.wav'
    }
    PLAYER = 'afplay' if _platform == 'darwin' else 'aplay'

    def __init__(self):
        self.devnull = open(os.devnull, 'w')

    def prompt(self, prompt_type, val=None):
        if val is None or prompt_type == PromptDirn.straight:
            call([self.PLAYER, BASE_AUDIO_DIR + self.PROMPTS[prompt_type]],
                 stdout=self.devnull, stderr=self.devnull)
        else:
            args = [self.PLAYER, BASE_AUDIO_DIR + self.PROMPTS[prompt_type]]
            for digit in str(val):
                args.append(BASE_AUDIO_DIR + digit + '.wav')
            call(args, stdout=self.devnull, stderr=self.devnull)

    def prompt_node_reached(self, node_id):
        args = [self.PLAYER, BASE_AUDIO_DIR + 'node_reached.wav']
        for digit in str(node_id):
            args.append(BASE_AUDIO_DIR + digit + '.wav')
        call(args, stdout=self.devnull, stderr=self.devnull)

    def prompt_enter_info(self):
        call([self.PLAYER, BASE_AUDIO_DIR + 'enter_info.wav'],
             stdout=self.devnull, stderr=self.devnull)

    def prompt_begin(self):
        call([self.PLAYER, BASE_AUDIO_DIR + 'begin.wav'],
             stdout=self.devnull, stderr=self.devnull)

if __name__ == '__main__':
    from time import sleep
    obj = AudioDriver()
    obj.prompt(PromptDirn.left)
    sleep(0.5)
    obj.prompt(PromptDirn.end)
    sleep(1)
    obj.prompt(PromptDirn.right)
    obj.prompt_node_reached(123)
