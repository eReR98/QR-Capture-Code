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
        outstr = "Frame time is {0:.2f} ms, about {1:.2f} fps".format((currTime-prevTime)*1000, 1.0/(currTime-prevTime))
        print("Frame time is " + str(currTime-prevTime))

    prevTime=currTime

    if not ret:
        print("error capturing image")


    #cv2.imwrite("I_am_a_test_image.png", frame)

    


