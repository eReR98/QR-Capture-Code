# This is the start of the security system code. Currently only captures an image

import cv2

cam = cv2.VideoCapture(0)

ret, frame = cam.read()

if not ret:
    print("error capturing image")

cv2.imwrite("I_am_a_test_image.png", frame)

cam.release()


