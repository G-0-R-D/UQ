
def build(ENV):

	ParseqEncoder = ENV.ParseqEncoder

	class SnapNetworkEncoder(ParseqEncoder):


		def _encode(self, COMPONENT, INFO):
			# value = OR(object, array, number, string, false, null, true)
			# when value is replaced yield an b'X' and record the position in the bytes to decode later...

			# EXTRACTS is list of all the extracted components (large byte arrays, etc...)
			
			if isinstance(COMPONENT, dict):
				yield b'{'

				remaining = len(COMPONENT)
				for key,value in COMPONENT.items():
					assert isinstance(key, str), 'non-string keys are not permitted'

					yield b'"' + bytes(key, 'ascii') + b'":'

					for _ in self._encode(value, INFO):
						yield _

					remaining -= 1
					if remaining > 0:
						yield b','

				yield b'}'

			elif isinstance(COMPONENT, (tuple, list)):
				yield b'['

				remaining = len(COMPONENT)

				for item in COMPONENT:

					for _ in self._encode(item, INFO):
						yield _

					remaining -= 1
					if remaining > 0:
						yield b','

				yield b']'

			elif isinstance(COMPONENT, str):
				# always pushes strings to bytes section so they don't need any special handling...
				INFO['extracts'].append(COMPONENT.encode())
				yield b'S' + bytes(str(len(COMPONENT)), 'utf8')

			elif isinstance(COMPONENT, bytes):

				INFO['extracts'].append(COMPONENT)
				yield b'B' + bytes(str(len(COMPONENT)), 'utf8')

			# TODO use int for true/false instead?  so it's 1 char/byte?
			elif COMPONENT is True:
				yield b'true'

			elif COMPONENT is False:
				yield b'false'

			elif isinstance(COMPONENT, (int,float)):
				yield bytes(str(COMPONENT), 'utf8')

			elif COMPONENT is None:
				yield b'null'

			else:
				# TODO all ENV types could potentially be supported if they are available on both sides, but __init__ becomes a little tricky (use save/load api?)
				# so if hasattr(ENV, COMPONENT.__class__.__name__) COMPONENT.__snap_save__() ? and if it is saveable then it works?  we'd have to note it's type along with the data...

				# add ClassName:<int> to <SNAP> index, and then send the __save__() json to the bytes (also encode?)

				# T<byte index>:ClassName and then the save data goes into bytes (which could be further encoded as well)

				# use either 'C' for class, or 'N' for Node?

				raise TypeError('unsupported type', type(COMPONENT))

		def encode(self, JSON):

			assert isinstance(JSON, (dict,list,tuple)), 'json root must be list or dict, not: {}'.format(type(JSON))

			info = {
				'extracts':[], # the bytes extracted from message to be appended at the end for efficiency (so json decoding doesn't have to scan the bytes!) # store as (count (index), and byte) info
				'json_byte_count':0, # tally of bytes yielded so far
			}

			json_output = []
			for BYTES in self._encode(JSON, info):
				info['json_byte_count'] += len(BYTES) # keep track here so we don't make a mistake or have to manually do this according to the code structure!
				json_output.append(BYTES) # merge after

			bytestream = b''.join(info['extracts'])

			return b'<SNAP>' + bytes(str(info['json_byte_count']), 'utf8') + \
			b' ' + bytes(str(len(bytestream)), 'utf8') + b'</SNAP>' + \
			b''.join(json_output) + \
			bytestream

		def __init__(self):
			ParseqEncoder.__init__(self)

	ENV.SnapNetworkEncoder = SnapNetworkEncoder


def main(ENV):

	SnapMessage = ENV.SnapMessage
	# TODO to encode message just put the message data into it's own dict {'kwargs':{...}, 'args':[...], 'source':id(...)}
	
	enc = ENV.SnapNetworkEncoder()

	testdata = {
		# fake image
		'width':100,
		'height':100,
		'format':'RGBA',
		'pixels':b'123412341234123412341234123412341234',
		'extra':None,
		'true':True,
		'false':False,
		'decimal':199.2,
		'list':[1,2,3,b'more bytes to encode', "just a string"],

		# TODO
		'naughty_string':'this is a """" SUPER """"""""" naughty string',
		'another_naughty_string':"\"this is also a \"\"\" naughty string",
	}

	data = enc.encode(testdata)

	print(data)




