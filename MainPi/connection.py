import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("192.168.0.1",5006))
s.listen(5)

def connectivity():
	##print("CONNECTIVITY SCRIPT")
	while True:
		conn, client = s.accept()
		try:
			while True:
				try:
					data = conn.recv(1024)
				except:
					continue
				if data:
					conn.sendall(data)
				else:
					break
		finally:
			conn.close()
