# Security system code, written in Python. 
# 
# LCD code used from Matt Hawkins and Leon Anavi for interfacing with i2c display. 
# Reference code here (https://github.com/leon-anavi/raspberrypi-lcd/blob/master/raspberrypi-lcd.py)

import cv2
import atexit
import time
import syslog
import pigpio
import RPi.GPIO as GPIO


# Define control variables here
PrintFrameTime = False
PrintQRVal = True
PrintSyslog = False

# Servo Params
servoOpenPos = 2300
servoClosePos = 600
servoPin = 12

# LCD params

LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_E  = 8
LCD_RS = 7

LCD_WIDTH = 16 # Using a 2x16 display
LCD_CHR = True
LCD_CMD = False

LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

openTime = 15.0
scanDelay = 5.0

prevTime = time.time()
currTime = time.time()

# Dictionary of users
approvedUsers = {'eReR98Password' : 'eReR98', 'Dougie1234' : 'Doug'}

# all functions starting with lcd_ are borrowed from the lcd code mentioned
# at the top of this file

def lcd_string(message,line):
  # Cast to string
  message = str(message)
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

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

# Moves servo to open position
def openDoor():
    pi_GPIO.set_servo_pulsewidth(servoPin, servoOpenPos)

# Moves servo to closed position
def closeDoor():
    pi_GPIO.set_servo_pulsewidth(servoPin, servoClosePos)

# Resets text on the lcd to the default
def resetText():
    lcd_string("Door Locked", LCD_LINE1)
    lcd_string("Show code", LCD_LINE2)


# Setup Code
cam = cv2.VideoCapture(0) # camera object
detector = cv2.QRCodeDetector() # QR code detector for the captured frame

pi_GPIO = pigpio.pi() # pigpio object for handling hardware PWM and servo control
pi_GPIO.set_mode(servoPin, pigpio.OUTPUT) # setting servo pin to output

atexit.register(exitHandler)

printHandler("starting security system")

closeDoor()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)

lcd_init()
resetText()

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

    # if the detector finds a QR code
    if ret:

        outstr = "QR code(s) detected. Num Found: {0}, Decoded vals: ".format(len(decodeInfo))

        # if decodeInfo is empty, then the full QR code was not read, do nothing
        if len(decodeInfo[0]) == 0:
            if PrintQRVal:
                printHandler("QR code(s) found. Could not decode")
        else:
            for userKey in decodeInfo:
                outstr = outstr + userKey + " "

                # Checks if password is in the dictionary
                if userKey in approvedUsers:
                    printHandler("Welcome "+approvedUsers[userKey]+", opening door now")

                    # prints to LCD
                    lcd_string("Welcome", LCD_LINE1)
                    lcd_string(approvedUsers[userKey], LCD_LINE2)

                    openDoor()

                    time.sleep(openTime)

                    resetText()

                    closeDoor()

                    printHandler("Closing Door")
                else:
                    printHandler("User not authorized")
                    lcd_string("Access Denied", LCD_LINE1)
                    lcd_string("XXXXXXXX", LCD_LINE2)
                    time.sleep(scanDelay)
                    resetText()

            if PrintQRVal:
                printHandler(outstr)

cam.release()

    


