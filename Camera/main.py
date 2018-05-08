#!/usr/bin/python3
import socket
import time
from threading import Thread
from Connectivity import connectivity

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
		break
	else:
		continue

def take_picture():
	while True:
		if connectivity():
			print("[+]Conenction: Picture saved on server")
		##Take picture then save it on the file server
		else:
			print("[!]No Connection: Picture saved locally")
		time.sleep(1)

thread_picture = Thread(target=take_picture)
thread_picture.start()
