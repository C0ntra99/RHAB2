#!/usr/bin/python3
import time
from threading import Thread
from picamera import PiCamera, Color
import datetime

camera = PiCamera()

doneVideos = []

hostname = "MainPi"

def record(filename, location, video, amount=1800):
	##record first 30 minutes of flight
	if video == 1:
		camera.start_recording(location+filename)
		time.sleep(amount)
		camera.stop_recording()
		global endAlt
		endAlt = alt
		doneVideos.append(1)
	##try to get the pop at 25000 meter
	if video == 2:
		camera.start_recording(location+filename)
		while not if_falling():
			time.sleep(1)
		camera.stop_recording()
		doneVideos.append(2)
	##get last little bit of the flight
	if video == 3:
		camera.start_recording(location+filename)
		while not alt == oldAlt:
			time.sleep(1)
		camera.stop_recording()
		doneVideos.append(3)

def is_falling(oldAlt):
	if oldAlt > alt:
		return True
	else:
		return False

def take_picture():
	pic = 0
	while True:
		log_time = datetime.datetime.now()
		nowDate = "{:02d}/{:02d}/{:04d}".format(log_time.month, log_time.day, log_time.year)
		nowTime = "{:02d}:{:02d}:{:02d}".format(log_time.hour, log_time.minute, log_time.second)
			##Check Altitude to whatever we want
		if 1 not in doneVideos:
			print('video start')
			record(hostname+'-beginningVideo.h264', '/home/pi/localVideos/', 1)
			print('video stop')
		if alt > 25000 and 2 not in doneVideos:
			record(hostname+'-balloonPop.h264', '/home/pi/localVideos/',2)
		elif alt < endAlt and 3 not in doneVideos:
			record(hostname+'-balloonEnd.h264', '/home/pi/localVideos/',3)
			break
		else:
			pass
		print("[+]Conenction: Picture saved on server")
		##Make server file and change date
		camera.resolution = (1440, 1080)
		camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(alt)
		camera.annotate_text_size = 25
		camera.annotate_foreground = Color('white')
		##Take picture then save it on the file server
		camera.capture('/home/pi/serverPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic))
		pic += 1
		time.sleep(6)

	camera.close()