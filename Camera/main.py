#!/usr/bin/python3
import socket
import time
from threading import Thread
from Connectivity import connectivity
from picamera import PiCamera, Color
import datetime

camera = PiCamera()
camera.resolution = (1920, 1080)

##import picamera SHIT
doneVideos = []
hostname = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


s.bind(('0.0.0.0',5005))

def confirmation():
	s2.sendto((hostname+" Started").encode(), ("192.168.0.1",5007))

def record(filename, location, video, amount=120):
	camera.resolution = (1920, 1080)
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
		time.sleep(10)
		##CHANGE
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
	if oldAlt > (alt + 10):
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
			break
		else:
			pass
		print('loop:'+pic)
		if connectivity():
			print("[+]Conenction: Picture saved on server")
			##Make server file and change date
			camera.resolution = (3280, 2464)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(alt)
			camera.annotate_text_size = 25
			camera.annotate_foreground = Color('white')
			##Take picture then save it on the file server
			camera.capture('/home/pi/serverPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic))
		else:
			print("[!]No Connection: Picture saved locally")
			camera.resolution = (3280, 2464)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(alt)
			camera.annotate_text_size = 25
			camera.annotate_foreground = Color('white')
			##Change the path to the local folder
			camera.capture('/home/pi/localPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic))
		pic += 1
		time.sleep(6)

	camera.close()

def main():
	global alt
	global oldAlt
	alt = 0
	print("[=]Waiting for command")
	while True:
		data, addr = s.recvfrom(1024)
		if data.decode() == "Run":
			print("Sending ACK")
			Thread(target=confirmation).start()
			Thread(target=take_picture).start()
		##TEST THIS
		if 'ALT' in data.decode():
			print("Altitude has been set")

			oldAlt = alt
			alt = float(data.decode()[4:])
			print("Altitude: ", alt)

		else:
			continue

if __name__ == "__main__":
	main()
