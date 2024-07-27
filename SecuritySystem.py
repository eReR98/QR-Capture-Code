# This is the start of the security system code. Currently only captures an image

import cv2
import atexit
import time


# Define control variables here
PrintFrameTime = False
PrintQRVal = False

prevTime = time.time()
currTime = time.time()

# Setup Code
cam = cv2.VideoCapture(0)

def exitHandler():
    print("exit command detected. Exiting...")
    cam.release()

atexit.register(exitHandler)

# Program Loop
while(True):

    ret, frame = cam.read()

    currTime=time.time()
    
    if PrintFrameTime:
        print("Frame time is " + str(currTime-prevTime))

    prevTime=currTime

    if not ret:
        print("error capturing image")

    #cv2.imwrite("I_am_a_test_image.png", frame)

    


