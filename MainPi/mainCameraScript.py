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

def record(filename, location, video, amount=1800):
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
		##CHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANGE
		#while not is_falling():
		#	time.sleep(6)
		#time.sleep(60)
		time.sleep(1800)
		##CHANGE
		camera.stop_recording()
		doneVideos.append(2)
	##get last little bit of the flight
	if video == 3:
		camera.start_recording(location+filename)
		##CHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANGE
		#while not share.alt == share.oldAlt == share.oldOldAlt and 3 not in doneVideos and 2 in doneVideos:
		#	time.sleep(6)
		time.sleep(1800)
		camera.stop_recording()
		doneVideos.append(3)
	if video == 4:
		camera.start_recording(location+filename)
		time.sleep(14400)
		camera.stop_recording()

def is_falling():
	if share.oldAlt > share.alt and share.oldOldAlt > share.oldAlt:
		return True
	else:
		return False

def tp(picture, nowDate, nowTime):
	##Make server file and change date
	camera.resolution = (3280, 2464)
	camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(share.alt)
	camera.annotate_text_size = 50
	camera.annotate_foreground = Color('white')
	camera.capture(picture)
	##Take picture then save it on the file server

def take_picture():
	pic = 0
	global startTime
	startTime = time.time()
	while True:
		log_time = datetime.datetime.now()
		nowDate = "{:02d}/{:02d}/{:04d}".format(log_time.month, log_time.day, log_time.year)
		nowTime = "{:02d}:{:02d}:{:02d}".format(log_time.hour, log_time.minute, log_time.second)
			##Check Altitude to whatever we want
		if 1 not in doneVideos:
			print('video start')
			record(hostname+'-beginningVideo.h264', '/home/pi/localVideos/', 1)
			print('video stop')
		##CHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANGE
		#if share.alt > 25000 and share.oldAlt > 25000 and 2 not in doneVideos:
		if time.time() > startTime + 9000 and 2 not in doneVideos:
			print('Pop start')
			record(hostname+'-balloonPop.h264', '/home/pi/localVideos/',2)
			print('Pop stop')
		##CHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANGE
		#elif share.alt < endAlt and 3 not in doneVideos and 2 in doneVideos:
		elif time.time() > startTime + 14400 and 3 not in doneVideos:
			print('End start')
			record(hostname+'-balloonEnd.h264', '/home/pi/localVideos/',3)
			print('End stop')
			share.done = True
			break
		elif time.time() > startTime + 14400 and 2 not in doneVideos:
			record('Failsafe.h264', '/home/pi/localVideos/',4)
			share.done = True
			break
		else:
			pass
		print("[+]Conenction: Picture saved on server")
		##Make server file and change date
		Thread(target=tp, args=('/home/pi/localPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic), nowDate, nowTime)).start()
		pic += 1
		try:
			time.sleep(6)
		except KeyboardInterrupt:
			camera.close()
			exit()

	camera.close()