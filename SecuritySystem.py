# Security system code, written in Python. 

import cv2
import atexit
import time
import syslog
import pigpio


# Define control variables here
PrintFrameTime = False
PrintQRVal = True
PrintSyslog = False

servoOpenPos = 2300
servoClosePos = 600
servoPin = 12

sleepTime = 15.0

prevTime = time.time()
currTime = time.time()

# Dictionary of users
approvedUsers = {'eReR98Password' : 'eReR98', 'Dougie1234' : 'Doug'}

# Setup Code
cam = cv2.VideoCapture(0) # camera object
detector = cv2.QRCodeDetector() # QR code detector for the captured frame
pi_GPIO = pigpio.pi() # pigpio object for handling hardware PWM and servo control
pi_GPIO.set_mode(servoPin, pigpio.OUTPUT) # setting servo pin to output

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

def openDoor():
    pi_GPIO.set_servo_pulsewidth(servoPin, servoOpenPos)

def closeDoor():
    pi_GPIO.set_servo_pulsewidth(servoPin, servoClosePos)

atexit.register(exitHandler)

printHandler("starting security system")

closeDoor()

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
            if PrintQRVal:
                printHandler("QR code(s) found. Could not decode")
        else:
            for userKey in decodeInfo:
                outstr = outstr + userKey + " "

                if userKey in approvedUsers:
                    printHandler("Welcome "+approvedUsers[userKey]+", opening door now")

                    openDoor()

                    time.sleep(sleepTime)

                    closeDoor()

                    printHandler("Closing Door")
                else:
                    printHandler("User not authorized")

            if PrintQRVal:
                printHandler(outstr)



    


cam.release()
    #cv2.imwrite("I_am_a_test_image.png", frame)

    


