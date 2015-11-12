import io
import time
import threading
import picamera
import cv2
import numpy as np
import zbar
from PIL import Image

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []
DIR_PATH = '/home/pi/cg3002/images/'
RES_WIDTH = 800
RES_HEIGHT = 600


def detect_qr(image):
    # create a reader
    scanner = zbar.ImageScanner()

    # configure the reader
    scanner.parse_config('disable')
    scanner.parse_config('upca.enable')
    scanner.parse_config('epn13.enable')

    # obtain image data
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, dstCn=0)

    pil = Image.fromarray(gray)
    width, height = pil.size
    raw = pil.tobytes()

    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    scanner.scan(image)

    # extract results
    for symbol in image:
        # do something useful with results
        print symbol.type
        print symbol.quality
        return symbol.data


class ImageProcessor(threading.Thread):

    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    np_arr = np.fromstring(self.stream.read(), np.uint8)
                    img = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)
                    qrData = detect_qr(img)
                    print qrData

                    # done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)


def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(2)]
    camera.resolution = (RES_WIDTH, RES_HEIGHT)
    camera.framerate = 5
    camera.start_preview()
    time.sleep(2)
    camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
