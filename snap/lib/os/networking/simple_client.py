
import sys, socket, select

HOST = 'localhost'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

#client.setblocking(False)

while 1:
	
	r,w,err = select.select([client], [], [])

	for s in r:
		print('client connected, recieved:', client.recv(4096))
		client.close()
		sys.exit()


