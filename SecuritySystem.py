# This is the start of the security system code. Currently only captures an image

import cv2
import atexit
import time


# Define control variables here
PrintFrameTime = False
PrintQRVal = True

prevTime = time.time()
currTime = time.time()

# Setup Code
cam = cv2.VideoCapture(0) # camera object
detector = cv2.QRCodeDetector() # QR code detector for the captured frame

# Handles keyboard interrupts and other exit signals
def exitHandler():
    print("exit command detected. Exiting...")
    cam.release()

atexit.register(exitHandler)

# Program Loop
while(True):

    # captures a frame from the camera
    ret, frame = cam.read()

    if not ret:
        print("error capturing image")
        break

    # Timing code for checking frametime and timestamp creation
    currTime=time.time()

    if PrintFrameTime:
        outstr = "Frame time is {0:.2f} ms, about {1:.2f} fps".format((currTime-prevTime)*1000, 1.0/(currTime-prevTime))
        print(outstr)

    prevTime=currTime


    ret, decodeInfo, points, qrcodeInfo = detector.detectAndDecodeMulti(frame)

    if PrintQRVal and ret:

        outstr = "QR code(s) detected. Num Found: {0}, Decoded vals: ".format(len(decodeInfo))

        if len(decodeInfo[0]) == 0:
            print("QR code(s) found. Could not decode")
        else:
            for decodedString in decodeInfo:
                outstr = outstr + decodedString + " "
            print(outstr)


    


cam.release()
    #cv2.imwrite("I_am_a_test_image.png", frame)

    


