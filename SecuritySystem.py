import cv2

cam = cv2.VideoCapture(0)

ret, frame = cam.read()

if not ret:
    print("error capturing image")

cv2.imwrite("I_am_a_test_image.png", frame)

cam.release()


