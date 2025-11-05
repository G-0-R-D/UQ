
import socket, select

# TODO https://protobuf.dev/
# how to setup vpn https://forums.linuxmint.com/viewtopic.php?t=429980

# TODO we could write a wrapper server in curl, so we can send our bytes through the c api and the rest of the connections are handled there

# TODO
"""
Network is opened for the UQ application as a whole, and listens for incoming
	-- incoming can ask for list of connectible nodes and their descriptions and identities

all comms via json
other networks/devices/UQ instances are visible with node that displays connectible network nodes, and they connect as if they are local...  task input could connect to application network explicitly

once a connection is made, then it's just a json decode and the json is the msg that is then sent directly to the connected __snap_send__ (input)

"""

def build(ENV):

	SnapNode = ENV.SnapNode

	# TODO make a SnapNetworkMessage which can be supported in nodes that connect to the internet, as a way to organize headers and bytes...  then the protocol doesn't matter!

	# TODO how to make it easy to just send json messages over network efficiently?
	#	-- like for image: with=int, height=int, format=string, pixels=bytes if the bytes are in the json then it needs to be scanned to decode the json!  but that's wasteful!
	#	-- we need to list the values separately?
	#	-- what about listing the indices in the <SNAP> header?  size of json (with elements removed)

	# TODO the networks can communicate to eachother to do the query (rather than nodes) and then the message protocol can be used, first connection is expected to be a network/UQ instance, nodes can then find available nodes on other side of the network through local api...  once queried or accessed?  UQ should always try to find instances on same network?  network setup could be saved?


	class SnapNetwork(SnapNode):

		__slots__ = [
			'server', 'clients', 'incoming', 'outgoing',
			'refresh',]

		class Refresh(SnapEvent):

			def __snap_description__(self):
				return {
					'inputs':['()'],
					'outputs':['()'],
				}

			def __snap_input__(self, MSG):

				network = self.parent()

				r,w,err = select.select(network.incoming, network.outgoing, [], .001)

				for x in r:

					if x is network.server:

						client,address = s.accept()
						print('connection from:', client, address)

						#client.send(b'hello there!')
						#client.close()

						# TODO this should actually be a json request to auth and negotiate which node to connect to...
						#	-- auth, report list of available (network visible) nodes, then create connection to that node (list it in the client info)
						network.clients[client] = {'address':address}#, 'output':None, 'input':None}
						network.incoming.append(client)

					else:
						# client
						if 'more to load based on <SNAP> header':
							'continue loading message' # client.recv(4096)
						else:
							'check type, could be DESCRIPTION where we describe our setup and what nodes are connectable'
							'do auth via json with password or question or something'
							'or could be anything else that gets sent to connected node'

				print('cycle')

		def decode(self, CLIENT, JSON):
			'attempt to read a full message and if so send it on'

		def encode(self, CLIENT, DICT):
			'<SNAP>'

			# TODO if json data then json.dumps(DICT)?

			# TODO what if it's just size and then json?  and then the json values are indices into the trailing data...
			#	-- so we have size of json component, and size of whole message (or second part), and then the second part is the byte values of the json values clumped all together, and json values are then indices into that...  in order?

		def register(self, NODE, **SETTINGS):
			'make node visible to outside world'
			# TODO how to make sure messages are serializable?
			#	-- require messages to be strings/bytes?  if there is some kind of save/load mechanism that is the responsibility of the client node!


		def __snap_description__(self):
			'' # ?

		def __snap_input__(self, MSG):
			''

		def __snap_send__(self, MSG):
			''

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self)

			self.refresh = SnapNetwork.Refresh(self)

			# TODO use a protocol of json
			# CODE (<SNAP> <SIZE OF JSON> <SIZE OF TRAILING BYTE PAYLOAD (if applicable)>)
			#	-- both numbers always present, and not 0 padded, just scan for numbers until space or limit.  (or use ! or special char to mark end of header?  maybe </SNAP>)
			#	like: <SNAP>1000 0</SNAP>...

			# first message should auth?

			# each network represents one UQ instance, so there is a server listening for other UQ instances to connect
			# nodes can register with the network to make themselves visible to other UQ sessions for cross-network connectivity

			# need a protocol to serialize json messages...  __save__?  just assume everything is already strings for now?  argspec could have one that handles network protocols by having a special field...?  'from_network=True' or something like that?


			HOST = 'localhost'
			PORT = 5000

			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.bind((HOST, PORT))


			#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#client.connect((HOST, PORT))

			server.listen(2)

			server.setblocking(False)

			server.setsockopt(socket.SOL_SOCKET,
				socket.SO_REUSEADDR, 1) # so we can reconnect to same address

			self.server = server
			self.clients = {} # {client:{<info>}, ...}
			self.incoming = [server]
			self.outgoing = []



	ENV.SnapNetwork = SnapNetwork

