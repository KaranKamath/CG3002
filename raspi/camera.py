import time
import picamera
import cv2


def process(i):
    id = str(i)
    if int(i) < 10:
        id = '0' + str(id)

    img = cv2.imread('image'+id+'.jpg', 0)
    cv2.imwrite('grayscale' + id, img)

with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.start_preview()
    time.sleep(1)
    for i, filename in enumerate(camera.capture_continuous('image{counter:02d}.jpg')):
        print('Captured image %s' % filename)
        if i == 100:
            break

        process(i)
        time.sleep(60)
    camera.stop_preview()
