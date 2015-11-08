import cv2

cv2.namedWindow('original', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('cropped', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('grayscale', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('canny', cv2.WINDOW_AUTOSIZE)

#path = './1446895858/image25.jpg'
path = '1446895956/image33.jpg'
img = cv2.imread(path, 0)

crop_img = img[360:,320:960]
blur = cv2.blur(crop_img, (5,5))
canny = cv2.Canny(blur, 33, 100)

cv2.imwrite('grayscale.jpg', blur)
cv2.imwrite('original.jpg', img)
cv2.imwrite('canny.jpg', canny)

cv2.imshow('original', img)
cv2.imshow('cropped', crop_img)
cv2.imshow('grayscale', blur)
cv2.imshow('canny', canny)

for row in canny[::-1]:
    left,right = False, False
    for leftcol in row[:len(row)/2]:
        if leftcol == 255:
            left=True

    for rightcol in row[len(row)/2:]:
        if rightcol == 255:
            right=True

    if left and not right:
        print 'turn right'
        break
    elif right and not left:
        print 'turn left'
        break

cv2.waitKey(0)
cv2.destroyAllWindows()
