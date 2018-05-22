import socket

def connectivity():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect(("192.168.1.1",5006))
	except:
		return False
	s.close()
	return True


