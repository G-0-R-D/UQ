
# for testing

import socket, select

HOST = 'localhost'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(2)

server.setblocking(False)

server.setsockopt(socket.SOL_SOCKET,
	socket.SO_REUSEADDR, 1) # so we can reconnect to same address


while 1:

	r,w,err = select.select([server], [], []) # NOTE: no timeout argument so this blocks

	for s in r:
		client,address = s.accept()
		print('got', client, address)

		client.send(b'hello there!')
		client.close()

	print('cycle')

