import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)

def beep(status):
	if status:
		GPIO.output(22, True)
	if not status:
		GPIO.output(22, False)

