#!/usr/bin/python3
import socket
import time
from threading import Thread
from Connectivity import connectivity

##import picamera SHIT

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
##Dynamically assign this
s.bind(("192.168.0.32",5005))

def confirmation():
	s2.sendto("Camera02 Started".encode(), ("192.168.0.1",5007))

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

		global alt
		alt = data.decode()[4:]
		print("Altitude: ", alt)

	else:
		continue

def take_picture():
	pic = 0
	while True:
		if connectivity():
			print("[+]Conenction: Picture saved on server")
			##Check Altitude to whatever we want
			if alt >= 500:
				##Take videos for 30 minutes
				cameraTakeVideo(30)
			else:
				pass
			##Make server file and change date
			camera.resolution = (1440, 1080)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + alt
			camera.annotate_text_size = 25
			camera.annotate_foreground = Coloe('white')
			##Take picture then save it on the file server
			camera.capture('/DATE'+pic))
		else:
			print("[!]No Connection: Picture saved locally")
			camera.resolution = (1440, 1080)
			camera.annotate_text = "Date: " + nowDate + "\nTime: " + nowTime + "\nAltitude: " + alt
			camera.annotate_text_size = 25
			camera.annotate_foreground = Coloe('white')
			##Change the path to the local folder
			camera.capture('/DATE'+pic))
		pic += 1
		time.sleep(1)
