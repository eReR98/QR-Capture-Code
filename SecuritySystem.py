# Security system code, written in Python. 

import cv2
import atexit
import time
import syslog


# Define control variables here
PrintFrameTime = False
PrintQRVal = True
PrintSyslog = True

prevTime = time.time()
currTime = time.time()

# Setup Code
cam = cv2.VideoCapture(0) # camera object
detector = cv2.QRCodeDetector() # QR code detector for the captured frame

# Handles keyboard interrupts and other exit signals
def exitHandler():
    printHandler("exit command detected. Exiting...")
    cam.release()

# Handles print commands, and directs them to either syslog or console
def printHandler(inStr):
    if(PrintSyslog):
        syslog.syslog(syslog.LOG_INFO, inStr)
    else:
        print(inStr)

atexit.register(exitHandler)

printHandler("starting security system")

# Program Loop
while(True):

    # captures a frame from the camera
    ret, frame = cam.read()

    if not ret:
        printHandler("error capturing image")
        break

    # Timing code for checking frametime and timestamp creation
    currTime=time.time()

    if PrintFrameTime:
        outstr = "Frame time is {0:.2f} ms, about {1:.2f} fps".format((currTime-prevTime)*1000, 1.0/(currTime-prevTime))
        printHandler(outstr)

    prevTime=currTime

    # Runs frame through QR detector and decodes any detected codes
    ret, decodeInfo, points, qrcodeInfo = detector.detectAndDecodeMulti(frame)

    # prints out QR code data for diagnostic purposes
    if PrintQRVal and ret:
        outstr = "QR code(s) detected. Num Found: {0}, Decoded vals: ".format(len(decodeInfo))

        if len(decodeInfo[0]) == 0:
            printHandler("QR code(s) found. Could not decode")
        else:
            for decodedString in decodeInfo:
                outstr = outstr + decodedString + " "
            printHandler(outstr)


    


cam.release()
    #cv2.imwrite("I_am_a_test_image.png", frame)

    


