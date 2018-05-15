#!/usr/bin/python3
import socket
import time
from threading import Thread
from Connectivity import connectivity
from picamera import PiCamera

camera = PiCamera.camera()

##import picamera SHIT
doneVideos = []
hostname = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


s.bind((socket.gethostbyname(hostname),5005))

def confirmation():
	s2.sendto((hostname+" Started").encode(), ("192.168.0.1",5007))

def record(filename, location, video, time=1800):
	##record first 30 minutes of flight
	if video == 1:
		camera.start_recording(location+filename)
		time.sleep(time)
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
		nowDate = "{:02d}/{:02d}/{:04d}".format(log_time.month, log_time.day, log_time.year)
		nowTime = "{:02d}:{:02d}:{:02d}".format(log_time.hour, log_time.minute, log_time.second)
			##Check Altitude to whatever we want
		if 1 not in doneVideos:
			record(hostname+'-beginningVideo.h264', '/localVideos/', 1)
		if alt > 25000 and 2 not in doneVideos:
			record(hostname+'-balloonPop.h264', '/localVideos/',2)
		elif alt < endAlt and 3 not in doneVideos:
			record(hostname+'-balloonEnd.h264', '/localVideos/',3)
			break
		else:
			pass
		if connectivity():
			print("[+]Conenction: Picture saved on server")
			##Make server file and change date
			camera.resolution = (1440, 1080)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + alt
			camera.annotate_text_size = 25
			camera.annotate_foreground = Color('white')
			##Take picture then save it on the file server
			camera.continuous('/serverPicutes/'+hostname+'-{timestamp:%H-%M-%S}-{counter:04d}.jpg'))
		else:
			print("[!]No Connection: Picture saved locally")
			camera.resolution = (1440, 1080)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + alt
			camera.annotate_text_size = 25
			camera.annotate_foreground = Coloe('white')
			##Change the path to the local folder
			camera.continuous('/localPicutes/'+hostname+'-{timestamp:%H-%M-%S}-{counter:04d}.jpg'))
		pic += 1
		time.sleep(6)

	camera.close()

def main():
	alt = 0
	print("[=]Waiting for Run command")
	while True:
		data, addr = s.recvfrom(1024)
		if data.decode() == "Run":
			print("Sending ACK")
			Thread(target=confirmation).start()
			Thread(target=take_picture).start()
		##TEST THIS
		if data.decode()[0:2] == "ALT":
			print("Altitude has been set")

			oldAlt = alt
			alt = float(data.decode()[4:])
			print("Altitude: ", alt)

		else:
			continue

if __name__ == "__main__":
	main()
