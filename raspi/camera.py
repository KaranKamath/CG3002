import time
import picamera
import cv2
import zbar
from PIL import Image
from picamera.array import PiRGBArray

DIR_PATH = 'images/'
RES_HEIGHT = 720
RES_WIDTH = 1280
counter = 1
TIME_PERIOD = 0.1


def detect_qr(image):
    # create a reader
    scanner = zbar.ImageScanner()
    scanner.parse_config('disable')
    scanner.parse_config('upca.enable')
    # configure the reader
    # scanner.parse_config('enable')

    # obtain image data
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, dstCn=0)

    cv2.imwrite(DIR_PATH + str(counter) + '-gray.jpg', gray)

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
        return symbol.data


def process_img(img):
    global counter

    # crop_img = img[(RES_HEIGHT / 2):, (RES_WIDTH / 4):(3 * RES_WIDTH / 4)]
    # blur = cv2.blur(crop_img, (5, 5))
    # canny = cv2.Canny(blur, 33, 100)

    # cv2.imwrite(DIR_PATH + str(counter) + '-blurred.jpg', blur)
    # cv2.imwrite(DIR_PATH + str(counter) + '-original.jpg', img)
    # cv2.imwrite(DIR_PATH + str(counter) + '-canny.jpg', canny)

    counter += 1

with picamera.PiCamera() as camera:
    camera.resolution = (RES_WIDTH, RES_HEIGHT)
    rawCapture = PiRGBArray(camera)

    # allow the camera to warmup
    time.sleep(0.1)

    while True:
        # grab an image from the camera
        camera.capture(rawCapture, format="bgr")
        img = rawCapture.array
        output = detect_qr(img)
        print output, counter
        process_img(img)
        rawCapture.truncate(0)
        time.sleep(TIME_PERIOD)
