# Security system code, written in Python. 
# 
# Aaron
# Github username: eReR98
# for ECEA 5307 
# 
# LCD code used from Matt Hawkins and Leon Anavi for interfacing with i2c display. 
# Reference code here (https://github.com/leon-anavi/raspberrypi-lcd/blob/master/raspberrypi-lcd.py)

import cv2
import atexit
import time
import syslog
import pigpio
import RPi.GPIO as GPIO
import logging
import datetime
import hashlib


# Define control variables here
PrintFrameTime = False
PrintQRVal = True
PrintSyslog = False

# Servo Params
servoOpenPos = 2300
servoClosePos = 600
servoPin = 12

# Button Params
buttonPin = 17
buttonStatePrev = False
buttonState = False

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

# Dictionary of users. It just stores the sha256 hash of the QR code
approvedUsers = {'cacf45f2f0e7a960070502c0143d98b2f6937a68cd979315eba3019e90def31a' : 'eReR98', '7e033c8aba06c192c441bab89677f7e724310a2c78595411937a601b471a6e13' : 'Dougie'}
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

# turns string into a hash
def getHash(inStr):
   hasher = hashlib.sha256()
   hasher.update((inStr.encode()))
   retHash = hasher.hexdigest()
   del hasher
   return retHash

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

GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)

lcd_init()
resetText()

curr_datetime = datetime.datetime.now()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename="AccessLog-" + curr_datetime.strftime("%d") + "-" + curr_datetime.strftime("%b") + "-" + curr_datetime.strftime("%Y") + "-" + curr_datetime.strftime("%X") + ".txt")
logging.info("**********Security System Startup***************")

# Program Loop
while(True):

    if GPIO.input(buttonPin) and not buttonState:
       printHandler("now accepting new codes")
       lcd_string("Scan new code", LCD_LINE1)
       lcd_string("+++++++++", LCD_LINE2)
       buttonState=True
       logging.info("System entered new user logging mode")
    elif not GPIO.input(buttonPin) and buttonState:
       printHandler("resuming normal operation")
       resetText()
       buttonState=False
       logging.info("System returned to normal operation")

    # captures a frame from the camera
    ret, frame = cam.read()

    if not ret:
        printHandler("error capturing image")
        logging.error("Unable to capture image from cam.read()")
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


        
      # if decodeInfo is empty, then the full QR code was not read, do nothing
      if len(decodeInfo[0]) == 0:
          if PrintQRVal:
              printHandler("QR code(s) found. Could not decode")
              logging.info("Detected partial QR Code")
      else:

          if buttonState:
              for userKey in decodeInfo:
                  
                userKeyHash = getHash(userKey)

                del userKey

                if userKeyHash not in approvedUsers:
                      
                    approvedUsers.update({userKeyHash : "New User"})
                    printHandler("adding user with passcode hash: "+ userKeyHash)
                    logging.info("New User with passcode hash: " + userKeyHash)

          else:

              for userKey in decodeInfo:
                  
                  userKeyHash = getHash(userKey)
                  

                  # Checks if password is in the dictionary
                  if userKeyHash in approvedUsers:
                      del userKey
                      printHandler("Welcome "+approvedUsers[userKeyHash]+", opening door now")

                      logging.info("User: " + approvedUsers[userKeyHash] + " opened the lock")

                      # prints to LCD
                      lcd_string("Welcome", LCD_LINE1)
                      lcd_string(approvedUsers[userKeyHash], LCD_LINE2)

                      openDoor()

                      #time.sleep(openTime)
                      currTime = time.time()
                      stopTime = currTime + openTime

                      while(stopTime > currTime):
                          ret, frame = cam.read()
                          currTime = time.time()
                      
                      resetText()

                      closeDoor()

                      printHandler("Closing Door")
                  else:
                      printHandler("User not authorized")
                      lcd_string("Access Denied", LCD_LINE1)
                      lcd_string("XXXXXXXX", LCD_LINE2)

                      logging.info("Unauthorized code scanned. Decoded userKey: " + userKey)
                      
                      del userKey

                      currTime = time.time()
                      stopTime = currTime + scanDelay

                      while(stopTime > currTime):
                          ret, frame = cam.read()
                          currTime = time.time()

                      resetText()

      del decodeInfo  

cam.release()

    


