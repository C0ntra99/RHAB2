#!/usr/bin/python3
import time
from threading import Thread
from picamera import PiCamera, Color
import datetime
import share

camera = PiCamera()
camera.resolution = (1920, 1080)

doneVideos = []

hostname = "MainPi"
share.init()

def record(filename, location, video, amount=120):
	camera.resolution = (1920, 1080)
	##record first 30 minutes of flight
	if video == 1:
		camera.start_recording(location+filename)
		time.sleep(amount)
		camera.stop_recording()
		global endAlt
		endAlt = share.alt
		doneVideos.append(1)
	##try to get the pop at 25000 meter
	if video == 2:
		camera.start_recording(location+filename)
		while not is_falling():
			time.sleep(6)
		time.sleep(10)
		##CHANGE
		camera.stop_recording()
		doneVideos.append(2)
	##get last little bit of the flight
	if video == 3:
		camera.start_recording(location+filename)
		while not share.alt == share.oldAlt == share.oldOldAlt and 3 not in doneVideos and 2 in doneVideos:
			time.sleep(6)
		camera.stop_recording()
		doneVideos.append(3)

def is_falling():
	if share.oldAlt > share.alt and share.oldOldAlt > share.oldAlt:
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
		if share.alt > 25000 and 2 not in doneVideos:
			print('Pop start')
			record(hostname+'-balloonPop.h264', '/home/pi/localVideos/',2)
			print('Pop stop')
		elif share.alt < endAlt and 3 not in doneVideos:
			print('End start')
			record(hostname+'-balloonEnd.h264', '/home/pi/localVideos/',3)
			print('End stop')
			share.done = True
			beeper.beep()
			break
		else:
			pass
		print("[+]Conenction: Picture saved on server")
		##Make server file and change date
		camera.resolution = (3280, 2464)
		camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(share.alt)
		camera.annotate_text_size = 25
		camera.annotate_foreground = Color('white')
		##Take picture then save it on the file server
		camera.capture('/home/pi/localPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic))
		pic += 1
		time.sleep(6)

	camera.close()