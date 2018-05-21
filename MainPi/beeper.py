import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)

def beep():
    while True:
        GPIO.output(22, True)
        time.sleep(5)
        GPIO.output(22, False)

