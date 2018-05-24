#!/usr/bin/python3
from threading import Thread
from sense_hat import SenseHat
from connection import connectivity
import mainCameraScript
import i2cSensors
import time
import datetime
import socket
import share
import os


##Camera IP address
cam01_addr = None
cam02_addr = None

# Dynamically grab ip leases for the cameras
with open("/var/lib/misc/dnsmasq.leases","r") as lease_file:
	for line in lease_file.readlines():
		if "cameraPi01" in line:
			cam01_addr = line.split(" ")[2]
		if "cameraPi02" in line:
			cam02_addr = line.split(" ")[2]

##UDP sockets to send run command and recieve ack
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.bind(("192.168.1.1",5007))
##init of the sensehat
sense = SenseHat()
sense.clear()


hostname = socket.gethostname()
share.init()


breakNow1 = False
breakNow2 = False
##Log file stuff
#global LOGFILE
LOGFILE = open("/home/pi/RHAB2/MainPi/Log.txt", "a")


def log_measurments():
	##Create a log name for the log.
	logName = "Log-{:02d}-{:02d}-{:04d}.txt".format(log_time.month, log_time.day, log_time.year)
	try:
		if not os.path.exists("/home/pi/RHAB2/MainPi/measurements/" + logName):
			with open("/home/pi/RHAB2/MainPi/measurements/" + logName,"a+") as main:
				main.write("{0:s},{1:s},{2:.04f},{3:2s},{4:4s},{5:4s},{6:4s},{7:4s},{8:4s}\n".format("date", "time", "humidity", "temperature", "pressure","altitude","ozone","ext press", "ext temp"))
	except:
		LOGFILE.write(str(log_time)+"[!]Log file is locked.\n")

	##Open the log and get the measurments from the sensehat and the other sensors (oxone, altimeter)
	with open("/home/pi/RHAB2/MainPi/measurements/" + logName,"a") as main:
		humidity = sense.get_humidity()
		temperature = sense.get_temperature()
		pressure = sense.get_pressure()
		altitude, exTemp, exPressure = i2cSensors.get_externals()

		##If the altitude has jumped over 600 meters since the last measuement then ignore it and grab another one
		if abs(share.alt - altitude) > 600 and share.alt != 0:
			altitude = i2cSensors.get_altitude()
		##Round the altitude to a whole number
		altitude = round(altitude)

		##Create 2 buffers for error checking
		share.oldOldAlt = share.oldAlt
		share.oldAlt = share.alt
		share.alt = altitude
		ozone = i2cSensors.get_ozone()
		date = "{:02d}/{:02d}/{:04d}".format(log_time.month, log_time.day, log_time.year)
		Time = "{:02d}:{:02d}:{:02d}".format(log_time.hour, log_time.minute, log_time.second)

		string = "{0:s},{1:s},{2:.04f},{3:.02f},{4:.04f},{5:6d},{6:.04f},{7:.04f},{8:.02f}\n".format(date, Time, humidity, temperature, pressure, altitude, ozone, exPressure, exTemp)
		main.write(string)

		##Blink a red light on the sensehat
		Thread(target=measurement_blink, kwargs={'justOnce':True}).start()

		##Send the altitude to the other cameras over sockets
		s.sendto(('ALT:'+str(altitude)).encode(),(cam01_addr, 5005))
		s.sendto(('ALT:'+str(altitude)).encode(),(cam02_addr, 5005))
		#print("Altitude:", altitude)

	LOGFILE.write(str(log_time)+"[]File has been written.\n")

##Handles the measurment thread
def measurement_thread():
	while True:
		Thread(target=log_measurments).start()
		time.sleep(6)

##Starts the cameras
def camera_thread():
	LOGFILE.write(str(log_time)+"[=]Sending 'run' command...\n")

	##Send a Run command to the camera and wait for ack from the camera and start LEDs on the sense hat to blink
	s.sendto("Run".encode(),(cam01_addr,5005))
	data, addr= s2.recvfrom(1024)
	global camera1_blink_thread
	camera1_blink_thread = Thread(target=camera1_blink).start()
	Thread(target=parse_camera_data, args=(data,)).start()

	s.sendto('Run'.encode(),(cam02_addr, 5005))
	data, addr= s2.recvfrom(1024)
	global camera2_blink_thread
	camera2_blink_thread = Thread(target=camera2_blink).start()
	Thread(target=parse_camera_data, args=(data,)).start()

	Thread(target=receive_break).start()

##Incase the cameras stop this will stop the LEDS from blinking
def receive_break():
	while True:
		data, addr= s2.recvfrom(1024)
		if data.decode() == "BREAK" and addr == cam01_addr:
			global breakNow1
			breakNow1 = True
		if data.decode() == "BREAK" and addr == cam02_addr:
			global breakNow2
			breakNow2 = True

def parse_camera_data(data):
	if data:
		sense.clear()
		#sense.show_message(data.decode())

		LOGFILE.write(str(log_time)+"[+]Cameras have started.\n")

		##Also start the mainPi camera
	else:
		LOGFILE.write(str(log_time)+"[!]Error cameras not started.\n")
		start_cameras()

def measurement_blink(sleepTime=0.5, justOnce=False):
	def stop():
		stop = True
	stop = False
	on = False
	while not stop and not justOnce:
		if on:
			sense.set_pixel(7,7,[0,0,0])
			on = False
		else:
			sense.set_pixel(7,7,[255,0,0])
			on = True
		time.sleep(sleepTime)
	sense.set_pixel(7,7,[255,0,0])
	time.sleep(sleepTime)
	sense.set_pixel(7,7,[0,0,0])

def camera1_blink(sleepTime=0.5, justOnce=False):
	def stop():
		stop = True
	stop = False
	on = False
	while not stop and not justOnce:
		if on:
			sense.set_pixel(7,0,[0,0,0])
			on = False
			if breakNow1:
				return
		else:
			sense.set_pixel(7,0,[0,0,255])
			on = True
		time.sleep(sleepTime)
	sense.set_pixel(7,0,[0,0,255])
	time.sleep(sleepTime)
	sense.set_pixel(7,0,[0,0,0])

def camera2_blink(sleepTime=0.5, justOnce=False):
	def stop():
		stop = True
	stop = False
	on = False
	while not stop and not justOnce:
		if on:
			sense.set_pixel(5,0,[0,0,0])
			on = False
			if breakNow2:
				return
		else:
			sense.set_pixel(5,0,[0,0,255])
			on = True
		time.sleep(sleepTime)
	sense.set_pixel(5,0,[0,0,255])
	time.sleep(sleepTime)
	sense.set_pixel(5,0,[0,0,0])

def cameraMain_blink(sleepTime=0.5, justOnce=False):
	def stop():
		stop = True
	stop = False
	on = False
	while not stop and not justOnce and not share.done:
		if on:
			sense.set_pixel(3,0,[0,0,0])
			on = False
		else:
			sense.set_pixel(3,0,[0,0,255])
			on = True
		time.sleep(sleepTime)
	sense.set_pixel(3,0,[0,0,255])
	time.sleep(sleepTime)
	sense.set_pixel(3,0,[0,0,0])

##Thread to keep the time for the whole script
def keep_time():
	global log_time
	while True:
		log_time = datetime.datetime.now()
		#Need to sleep
		time.sleep(0.00001)

def main_camera():
	Thread(target=cameraMain_blink).start()
	mainCameraScript.take_picture()

def main():
	thread_connectivity = Thread(target=connectivity)
	thread_connectivity.start()

	thread_time = Thread(target=keep_time)
	thread_time.start()

	LOGFILE.write(str(log_time)+"[+]Script started.\n")

	print("[=]Starting joystick input")

	runningList = []
	while True:
		event = sense.stick.wait_for_event()
		if event.action == "released" and event.direction == "middle":
			if "take_measurments" not in runningList:
				Thread(target=measurement_thread).start()
				print("Take measuements")
				#sense.show_message("Taking measurments")
				LOGFILE.write(str(log_time)+"[+]Measurments have started.\n")
				runningList.append("take_measurments")
			else:
				continue

		if event.action == "released" and event.direction == "left":
			if "start_cameras" not in runningList:
				Thread(target=camera_thread).start()
				Thread(target=main_camera).start()

				LOGFILE.write(str(log_time)+"[+]Cameras have started.\n")
				runningList.append("start_cameras")
			else:
				continue


if __name__ == "__main__":
	main()
