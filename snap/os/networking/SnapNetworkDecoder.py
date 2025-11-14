

def build(ENV):

	ParseqResult = ENV.ParseqResult
	ParseqSequence = ENV.ParseqSequence
	ParseqDecoder = ENV.ParseqDecoder

	snap_binary_search = ENV.snap_binary_search

	PARSEQ_MATCH_FAIL = ENV.PARSEQ_MATCH_FAIL

	snap_out = ENV.snap_out
	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error
	snap_debug = ENV.snap_debug

	ITEM = ENV.ParseqITEM
	REPEAT = ENV.ParseqREPEAT
	AND = ENV.ParseqAND
	OR = ENV.ParseqOR
	NOT = ENV.ParseqNOT
	ANY = ENV.ParseqANY
	NOTANY = ENV.ParseqNOTANY
	AHEAD = ENV.ParseqAHEAD
	BEHIND = ENV.ParseqBEHIND
	OPTIONAL = ENV.ParseqOPTIONAL
	POSITION = ENV.ParseqPOSITION
	RANGE = ENV.ParseqRANGE
	UNDEFINED = ENV.ParseqUNDEFINED

	ERROR = ENV.PARSEQ_ERROR

	ParseqLayer = ENV.ParseqLayer
	ParseqLayerITEM = ENV.ParseqLayerITEM

	class SnapNetworkDecoder(ParseqDecoder):

		__slots__ = ['header_parser', '_current_mode_']

		# TODO
		def _decode(self, RESULT, ITER_NEXT, INFO):
			'' # TODO this just needs to get a stream of results, then handle each one...  so make a generator to just yield results?  then branch on what they are?

			assert RESULT, 'no result'

			name = RESULT.name()

			if name == '{':
				# decode OBJECT

				OBJECT = dict() # new

				key = None
				last_was_comma = False
				message = "unable to decode object"
				while 1:

					# inside of an object must be a series of object members (separated with commas) or closing brace, anything else is an error

					result = next(ITER_NEXT)
					if not result:
						break
					name = result.name()

					if name == '}':
						# object complete
						# TODO if last_was_comma then error?  if strict...
						return OBJECT

					elif name == ',':
						if last_was_comma: # TODO only if set to strict?
							message = "expecting string delimited property name; empty comma field"
							break
						last_was_comma = True
						continue

					elif name == 'string':
						# decode member:
						# member must be "string":value (followed by comma or brace_close)

						# result is key
						key = result.value()
						if isinstance(key, bytes):
							key = key.decode()
						key = key[1:-1] # trim quotes
						if not key:
							message = "unable to decode string for object member key!"
							break

						# next is colon or error
						result = next(ITER_NEXT)
						name = result.name()
						if name != ':':
							# error if next isn't colon
							message = "expected colon (:)"
							break

						# next is value or error
						result = next(ITER_NEXT)
						value = self._decode(result, ITER_NEXT, INFO)
						#if not value: # XXX None, False would trip this
							#if (snap_event_noargs(self, "errored") != (any)"TRUE"){
							#	message = "unable to decode object value";
							#}
							# otherwise assume result has been assigned to errors in "DECODE_RESULT" call...
							#break

						if key in OBJECT:
							message = "duplicate keyname: \"{}\"".format(key)
							break

						OBJECT[key] = value
						key = None

					else:
						break

					last_was_comma = False

				#snap_event_noargs(self, "SET_ERROR", "result", RESULT, "message", "unable to decode object");

				#if (result)
				#	snap_event(self, "SET_ERROR", "result", result, "message", message);

				#return None

			elif name == '[':
				# decode ARRAY

				ARRAY = list() # new

				message = "unable to decode array"
				last_was_comma = False
				while 1:

					result = next(ITER_NEXT)
					if not result:
						break
					name = result.name()

					if name == ']':
						# TODO strict json does not allow trailing commas
						# array complete
						if last_was_comma:
							message = "trailing comma"
							break
						return ARRAY

					elif name == ',':
						# this will gobble up blank commas too like :,,, which is probably preferable...
						if last_was_comma:
							message = "empty comma field"
							break
						last_was_comma = True
						continue

					else:

						value = self._decode(result, ITER_NEXT, INFO)

						ARRAY.append(value)

					last_was_comma = False


			elif name == 'number':

				if RESULT.find('exponent'):
					raise Exception('exponents not yet supported')

				elif RESULT.find('fraction'):
					return float(RESULT.value())

				elif RESULT.find('integer'):
					return int(RESULT.value())

				else:
					raise TypeError('unknown number format', RESULT.value(), RESULT)

			elif name == 'string':
				#print(RESULT.value())
				s = RESULT.value()
				if isinstance(s, bytes):
					s = s.decode()
				#return s[1:-1].replace('\\"', '"') # trim quotes
				return s[1:-1] # trim quotes

			elif name == 'B':
				length = int(RESULT.subs()[0].value())
				current = INFO['byte_index']
				INFO['byte_index'] += length
				get = INFO['bytes'][current:current+length]
				return get

			elif name == 'S':
				length = int(RESULT.subs()[0].value())
				current = INFO['byte_index']
				INFO['byte_index'] += length
				get = INFO['bytes'][current:current+length]
				return get.decode()

			elif name == 'null':
				return None

			elif name == 'true':
				return True

			elif name == 'false':
				return False

			else:
				pass

			raise Exception('missed', RESULT)


		def decode(self, BYTES):

			SEQUENCE = ParseqSequence(BYTES)

			if not isinstance(BYTES, self._current_mode_):
					
				if isinstance(BYTES, bytes):
					
					def toggle(ITEMS):
						for item in ITEMS:
							if isinstance(item, ENV.ParseqITEM) and isinstance(item._value_, str):
								#print(item, type(item._value_.encode()))
								item._value_ = item._value_.encode()
						return ITEMS

					self._current_mode_ = bytes

				elif isinstance(BYTES, str):

					def toggle(ITEMS):
						for item in ITEMS:
							if isinstance(item, ENV.ParseqITEM) and isinstance(item._value_, bytes):
								item._value_ = item._value_.decode()
						return ITEMS

					self._current_mode_ = str

				else:
					raise TypeError(type(BYTES))

				self.filter_for(toggle)
				self.header_parser.filter_for(toggle)
			

			result = self.header_parser.match_with_result(SEQUENCE)

			byte_start = 0
			if result:
				subs = result.subs()
				#print('has header', subs[0].value(), subs[1].value())
				byte_start = result.end() + int(subs[0].value()) # starts after json, first is size of json, second is size of bytes
				SEQUENCE = ParseqSequence(BYTES[:byte_start])
				SEQUENCE.set(position=result.end())
			else:
				'scan for json component' # determine if byte trailer or not by extra at end?
				byte_start = len(BYTES) # assume no bytes for now?  this is just a normal json decode (TODO remove extras?)

			info = {
				'bytes':BYTES,
				'byte_index':byte_start, # start index of current decode position
			}

			def iter_next():

				while 1:

					result = self.match_with_result(SEQUENCE)
					if not result:
						break

					#print('next:', result, result.value())
					yield result

			n = iter_next()
			result = next(n)

			assert result, 'nothing to decode?'

			return self._decode(result, n, info)



		def __init__(self, *args, **kwargs):
			ParseqDecoder.__init__(self, *args, **kwargs)

			# TODO comments?  comments are not defined in the spec... probably because there would be no end to them since there is no newline consideration... (newline is simply ignored)

			# TODO if strict: no trailing commas, no comments, no alternate quotes (single quoted)

			"""
			match entries in their entirety, and then validate them in the current context...  (object must be key:value pairs, lists can be single entries)
			"""
			

			# TODO escape sequences?
			string = AND('"', OR(AND(REPEAT(NOTANY('"', '\n'), min=0), '"'), ERROR),
				name='string')

			symbols = [ITEM(value=v, name=v) for v in ('[',']','{','}',':',',')]
			symbol = ANY(items=symbols,
				name='symbol', capture=False)

			keywords = [ITEM(value=v, name=v) for v in ('false', 'true', 'null')]
			keyword = ANY(items=keywords, # TODO NOT(name_continue)?
				name='keyword', capture=False)

			sign = ANY('-','+')
			decimal = AND('.', capture=False)
			digit = RANGE('0','9', capture=False)
			digit1to9 = RANGE('1','9', capture=False)
			integer = OR('0', AND(digit1to9, REPEAT(digit, min=0)),
				name='integer', capture=True) # zero on it's own, or number not starting with zero
			fraction = AND(decimal, REPEAT(digit, min=1, capture=True),
				name='fraction', capture=True)
			exponent = AND(ANY('e','E'), OPTIONAL(sign), REPEAT(digit, min=1, capture=True),
				name='exponent', capture=True)
			number = AND(OPTIONAL(sign), integer, OPTIONAL(fraction), OPTIONAL(exponent),
				name='number', capture=True)

			B = AND('B', integer,
				name='B', capture=True) # TODO
			# TODO 'T', integer, ':', NAME) # for a custom type decode...

			# if a string has a quote inside it then it will be stored in bytes section
			S = AND('S', integer,
				name='S', capture=True)

			#ignore = REPEAT(ANY(' ', '\t', '\n', '\r'), min=1,
			#	name='ignore', capture=False, suppress=True)
			ignore = ANY(' ', '\t', '\n', '\r',
				name='ignore', capture=False, suppress=True)

			
			self.header_parser = AND('<SNAP>', integer, ' ', integer, '</SNAP>',
				name='header', capture=True)

			# TODO recognize full terms, but not full array and objects, so we can just consume the terms and validate they are correct for the current context (so we don't have to match grammar to the end)

			self.set(items=[

				string,

				symbol,
				keyword,
				number,

				B, # 'B'
				S, # 'S'
				# TODO class instance 'C' for any ENV type?  use save/load api...

				ignore,

				ERROR
				])

			self._current_mode_ = str



			#** because json can be quite large, it's better to decode each structure as it is encountered to minimize footprint, otherwise we could parse with this:
			"""
			value = OR(object, array, number, string, false, null, true)

			array = AND(bracket_open, OR(AND(OPTIONAL(value, REPEAT(comma, value)), bracket_close), ERROR2))

			object_member = AND(string, colon, OR(value, ERROR2))
			object = AND(brace_open, OR(AND(OPTIONAL(object_member, REPEAT(comma, object_member)), brace_close), ERROR2))

			LAYER(

				object,
				array,

				ERROR
			)
			"""

	ENV.SnapNetworkDecoder = SnapNetworkDecoder


def test(ENV):

	#ENV.parseq_debug_set_debug_level(1)

	#data = '<SNAP>66 36</SNAP>{"kwargs":{"width":100,"height":100,"format":"RGBA","pixels":X36}}123412341234123412341234123412341234'

	#data = '{"kwargs":{"width":100,"height":100,"format":"RGBA","pixels":"X"}}'

	data = b'<SNAP>156 56</SNAP>{"kwargs":{"width":100,"height":100,"format":"RGBA","pixels":B36,"extra":null,"true":true,"false":false,"decimal":199.2,"list":[1,2,3,B20,"just a string"]}}123412341234123412341234123412341234more bytes to encode'

	data = b'<SNAP>190 152</SNAP>{"kwargs":{"width":100,"height":100,"format":S4,"pixels":B36,"extra":null,"true":true,"false":false,"decimal":199.2,"list":[1,2,3,B20,S13],"naughty_string":S45,"another_naughty_string":S34}}RGBA123412341234123412341234123412341234more bytes to encodejust a stringthis is a """" SUPER """"""""" naughty string"this is also a """ naughty string'



	dec = ENV.SnapNetworkDecoder()

	msg = dec.decode(data)

	#print('closest', ENV.parseq_debug_closest_match())

	print(msg)
