#!/usr/bin/python3
from threading import Thread
from sense_hat import SenseHat
from connection import connectivity
import i2cSensors
import time
import datetime
import socket
import os


##Camera IP address
##Not how you use global
#global cam01_addr
#global cam02_addr
cam01_addr = None
cam02_addr = None

with open("/var/lib/misc/dnsmasq.leases","r") as lease_file:
	for line in lease_file.readlines():
		if "cameraPi01" in line:
			cam01_addr = line.split(" ")[2]
		if "cameraPi02" in line:
			cam02_addr = line.split(" ")[2]

##UDP sockets
#global s
#global s2
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.bind(("192.168.0.1",5007))
sense = SenseHat()
sense.clear()

##Log file stuff
#global LOGFILE
LOGFILE = open("/home/pi/RHAB2/MainPi/Log.txt", "a")

def take_measurments():
	logName = "Log-{:02d}-{:02d}-{:04d}.txt".format(log_time.month, log_time.day, log_time.year)
	try:
		with open("/home/pi/RHAB2/MainPi/measurments/" + logName,"a+") as main:
			if main.read() == "":
				main.write("{0:s},{1:s},{2:.04f},{3:2s},{4:4s},{5:4s},{6:4s}\n".format("date", "time", "humidity", "temperature", "pressure","altitude","ozone"))
	except:
		LOGFILE.write(str(log_time)+"[!]Log file is locked.")
	while True:
		with open("/home/pi/RHAB2/MainPi/measurments/" + logName,"a") as main:
			humidity = sense.get_humidity()
			temperature = sense.get_temperature()
			pressure = sense.get_pressure()
			altitude = i2cSensors.get_altitude()
			ozone = i2cSensors.get_ozone()
			date = "{:02d}/{:02d}/{:04d}".format(log_time.month, log_time.day, log_time.year)
			Time = "{:02d}:{:02d}:{:02d}".format(log_time.hour, log_time.minute, log_time.second)

			string = "{0:s},{1:s},{2:.04f},{3:.02f},{4:.04f},{5:.04f},{6:.04f}\n".format(date, Time, humidity, temperature, pressure, altitude, ozone)
			main.write(string)
			##TEST THIS
			s.sendto(('ALT:'+altitude).encode(),(cam02_addr, 5005))

		LOGFILE.write(str(log_time)+"[]File has been written")
		time.sleep(6)


def start_cameras():
#	s.sendto("Run".encode(),(cam01_addr,5005))
	s.sendto('Run'.encode(),(cam02_addr, 5005))


	LOGFILE.write(str(log_time)+"[=]Sending 'run' command...")

	data, addr= s2.recvfrom(1024)
	if data:
		sense.show_message(data.decode())

		LOGFILE.write(str(log_time)+"[+]Cameras have started")

		##Also start the mainPi camera
	else:
		LOGFILE.write(str(log_time)+"[!]Error cameras not started")
		start_cameras()

def joystick_input():
	runningList = []
	while True:
		event = sense.stick.wait_for_event()
		if event.action == "released" and event.direction == "middle":
			if "take_measurments" not in runningList:
				#what
				Thread(target=take_measurments()).start()
				print("TEST")
				sense.show_message("Taking measurments")

				LOGFILE.write(str(log_time)+"[+]Measurments have started")

				runningList.append("take_measurments")
			else:
				continue

		if event.action == "released" and event.direction == "left":
			if "start_cameras" not in runningList:
				start_cameras()

				LOGFILE.write(str(log_time)+"[+]Cameras started")

				runningList.append("start_cameras")
			else:
				continue

def keep_time():
	global log_time
	while True:
		log_time = datetime.datetime.now()
		#Need to sleep
		time.sleep(0.0000000000000000001)

def main():
	print("[=]Waiting on joystick input")
	joystick_input()


if __name__ == "__main__":
	thread_connectivity = Thread(target=connectivity)
	thread_connectivity.start()

	thread_time = Thread(target=keep_time)
	thread_time.start()
	LOGFILE.write(str(log_time)+"[+]Script started")

	main()
