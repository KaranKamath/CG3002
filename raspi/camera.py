import io
import time

import picamera
import zbar
from PIL import Image

CAM_RES_WIDTH = 800
CAM_RES_HEIGHT = 600
should_terminate = False


def camera(queue):
    scanner = zbar.ImageScanner()
    scanner.parse_config('disable')
    scanner.parse_config('upca.enable')
    # scanner.parse_config('ean13.enable')

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
            scanner.scan(z_image)
            for symbol in z_image:
                print symbol.data
            stream.seek(0)
            stream.truncate()
