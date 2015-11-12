import io
import time

import picamera
import zbar
from PIL import Image
from itertools import izip_longest

CAM_RES_WIDTH = 800
CAM_RES_HEIGHT = 600

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)

def decode(data):
    data = list(str(data))
    data.insert(-2, 0)
    split_data = [ int(''.join([str(x) for x in list(v)])) for v in grouper(3, data) ]
    
    if len(set(split_data)) == 1:
        return split_data[0]

    return None

def camera(queue):
    scanner = zbar.ImageScanner()
    scanner.parse_config('disable')
    scanner.parse_config('upca.enable')
    scanner.parse_config('ean13.enable')

    with picamera.PiCamera() as camera:
        camera.resolution = (CAM_RES_WIDTH, CAM_RES_HEIGHT)
        camera.framerate = 2
        camera.start_preview()
        time.sleep(2)
        stream = io.BytesIO()
        for x in camera.capture_continuous(stream, format="jpeg",
                                           use_video_port=True):
            stream.seek(0)
            image = Image.open(stream).convert('L')
            z_image = zbar.Image(image.size[0], image.size[1],
                                 'Y800', image.tobytes())
            print "Scanning..."
            scanner.scan(z_image)
            for symbol in z_image:
                print symbol.data, symbol.type
                print 'Decoded: ', decode(symbol.data)
            stream.seek(0)
            stream.truncate()
