#!/usr/bin/python3
import socket
import time
from threading import Thread
from Connectivity import connectivity
from picamera import PiCamera, Color
import datetime
import beeper

camera = PiCamera()
camera.resolution = (1920, 1080)

##import picamera
doneVideos = []
hostname = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


s.bind(('0.0.0.0',5005))

def confirmation():
	s2.sendto((hostname+" Started").encode(), ("192.168.1.1",5007))

def record(filename, location, video, amount=1800):##CHANGE
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
		#while not alt == oldAlt == oldOldAlt and 3 not in doneVideos and 2 in doneVideos:
		#	time.sleep(6)
		time.sleep(1800)
		camera.stop_recording()
		doneVideos.append(3)
	if video == 4:
		camera.start_recording(location+filename)
		time.sleep(14400)
		camera.stop_recording()

def is_falling():
	if oldAlt > alt and oldOldAlt > oldAlt:
		return True
	else:
		return False

def tp(picture, nowDate, nowTime):
	##Make server file and change date
	camera.resolution = (3280, 2464)
	camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + str(alt)
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
		#if alt > 25000 and oldAlt > 25000 and 2 not in doneVideos:
		if time.time() > startTime + 9000 and 2 not in doneVideos:
			print('Pop start')
			record(hostname+'-balloonPop.h264', '/home/pi/localVideos/',2)
			print('Pop stop')
		##CHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANGE
		#elif alt < endAlt and 3 not in doneVideos and 2 in doneVideos:
		elif time.time() > startTime + 14400 and 3 not in doneVideos:
			print('End start')
			record(hostname+'-balloonEnd.h264', '/home/pi/localVideos/',3)
			print('End stop')
			s2.sendto(("BREAK").encode(), ("192.168.1.1",5007))
			beeper.beep(True)
			break
		elif time.time() > startTime + 14400 and 2 not in doneVideos:
			record('Failsafe.h264', '/home/pi/localVideos/',4)
			s2.sendto(("BREAK").encode(), ("192.168.1.1",5007))
			beeper.beep(True)
			break
		else:
			pass
		if connectivity():
			print("[+]Conenction: Picture saved on server")
			Thread(target=tp, args=('/home/pi/serverPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic), nowDate, nowTime)).start()
		else:
			print("[!]No Connection: Picture saved locally")
			Thread(target=tp, args=('/home/pi/localPictures/'+hostname+'_{0:s}_{1:d}.jpg'.format(nowTime.replace(":","-"), pic), nowDate, nowTime)).start()
		pic += 1
		
		try:
			time.sleep(6)
		except KeyboardInterrupt:
			camera.close()
			s2.sendto(("BREAK").encode(), ("192.168.1.1",5007))
			exit()

	camera.close()

def main():
	global alt
	global oldAlt
	global oldOldAlt
	alt = 0
	oldAlt = 0
	oldOldAlt = 0
	print("[=]Waiting for command")
	while True:
		data, addr = s.recvfrom(1024)
		if data.decode() == "Run":
			print("Sending ACK")
			Thread(target=confirmation).start()
			Thread(target=take_picture).start()
		##TEST THIS
		if 'ALT' in data.decode():

			oldOldAlt = oldAlt
			oldAlt = alt
			alt = int(data.decode()[4:])

		else:
			continue

if __name__ == "__main__":
	main()
