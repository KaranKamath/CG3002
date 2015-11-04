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
DEGREES = get_audio_path('degrees.wav')
NODE_REACHED = get_audio_path('node_reached.wav')
ENTER_INFO = get_audio_path('enter_info.wav')
BEGIN = get_audio_path('begin.wav')
PLAYER = 'afplay' if _platform == 'darwin' else 'aplay'


class AudioDriver(object):

    def _play(self, args):
        with open(os.devnull, 'w') as null:
            if len(args) > 2 and PLAYER == 'afplay':
                for arg in args[1:]:
                    call([args[0], arg], stdout=null, stderr=null)
            else:
                call(args, stdout=null, stderr=null)

    def prompt(self, prompt_type, val=None):
        if val is None or prompt_type == PromptDirn.straight:
            self._play([PLAYER, PROMPTS[prompt_type]])
        else:
            args = [PLAYER, PROMPTS[prompt_type]]
            for digit in str(int(val)):
                args.append(DIGITS[int(digit)])
            args.append(DEGREES)
            self._play(args)

    def prompt_node_reached(self, node_id):
        args = [PLAYER, NODE_REACHED]
        for digit in str(int(node_id)):
            args.append(DIGITS[int(digit)])
        self._play(args)

    def prompt_enter_info(self):
        self._play([PLAYER, ENTER_INFO])

    def prompt_begin(self):
        self._play([PLAYER, BEGIN])

if __name__ == '__main__':
    from time import sleep
    obj = AudioDriver()
    obj.prompt(PromptDirn.left, 1.234)
    obj.prompt(PromptDirn.end)
    obj.prompt(PromptDirn.right, 12)
    obj.prompt_node_reached(1)
