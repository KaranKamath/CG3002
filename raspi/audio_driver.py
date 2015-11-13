import os
import os.path as osp
from sys import platform as _platform
from subprocess import Popen, call
from prompts_enum import PromptDirn

BASE_AUDIO_DIR = osp.join(osp.dirname(osp.realpath(__file__)), 'audio')


def get_audio_path(audio):
    return osp.join(BASE_AUDIO_DIR, audio)

PROMPTS = {
    PromptDirn.left: get_audio_path('left.wav'),
    PromptDirn.right: get_audio_path('right.wav'),
    PromptDirn.straight: get_audio_path('straight.wav'),
    PromptDirn.end: get_audio_path('dest_reached.wav')
}
DIGITS = [get_audio_path(str(n) + '.wav') for n in range(10)]
NODE_REACHED = get_audio_path('node_reached.wav')
STAIRS = get_audio_path('stairs.wav')
STEP = get_audio_path('step.wav')
DOOR = get_audio_path('door.wav')
ENTER_INFO = get_audio_path('enter_info.wav')
BEGIN = get_audio_path('begin.wav')
PLAYER = 'afplay' if _platform == 'darwin' else 'play'
SPEED_ARGS = ['-r', '1.3'] if _platform == 'darwin' else ['tempo', '1.3']


class AudioDriver(object):

    def __init__(self):
        self.process = None

    def _play(self, args, async=False):
        if self.process:
            self.process.kill()
        with open(os.devnull, 'w') as null:
            if _platform == 'darwin':
                for arg in args[1:]:
                    if async:
                        self.process = Popen([args[0], arg] + SPEED_ARGS,
                                             stdout=null, stderr=null)
                    else:
                        call([args[0], arg] + SPEED_ARGS,
                             stdout=null, stderr=null)
            elif async:
                self.process = Popen(args + SPEED_ARGS,
                                     stdout=null, stderr=null)
            else:
                call(args + SPEED_ARGS,
                     stdout=null, stderr=null)

    def prompt(self, prompt_type, val=None):
        if val is None:
            self._play([PLAYER, PROMPTS[prompt_type]])
        else:
            args = [PLAYER, PROMPTS[prompt_type]]
            for digit in str(int(abs(val))):
                args.append(DIGITS[int(digit)])
            self._play(args)

    def prompt_step(self, val=None):
        if val is None:
            self._play([PLAYER, STEP])
        else:
            self._play([PLAYER, DIGITS[val]])

    def prompt_node_reached(self, node_id):
        args = [PLAYER, NODE_REACHED]
        for digit in str(int(node_id)):
            args.append(DIGITS[int(digit)])
        self._play(args, async=False)

    def prompt_stairs(self):
        self._play([PLAYER, STAIRS], async=False)

    def prompt_door(self):
        self._play([PLAYER, DOOR], async=False)

    def prompt_enter_info(self):
        self._play([PLAYER, ENTER_INFO], async=False)

    def prompt_begin(self):
        self._play([PLAYER, BEGIN], async=False)

if __name__ == '__main__':
    obj = AudioDriver()
    obj.prompt(PromptDirn.left, 1.234)
    obj.prompt(PromptDirn.end)
    obj.prompt_step()
    obj.prompt_step(1)
    obj.prompt_door()
    obj.prompt(PromptDirn.straight, 12)
    obj.prompt_node_reached(1)
