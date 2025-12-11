
from snap.lib.parsing.parseq import *

# ~/Android/Sdk/sources/android-25/android/util/JsonReader.java
# https://www.ietf.org/rfc/rfc4627.txt

#JSON can represent four primitive types (strings, numbers, booleans, and null) and two structured types (objects and arrays).


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

	class JSONDecoder(ParseqDecoder):


		def decode_result(self, RESULT):

			assert RESULT, 'no result'

			SEQUENCE = RESULT.sequence()
			assert SEQUENCE, 'no sequence in result'

			name = RESULT.name()

			_return = None
			
			if name == '{':
				# DECODE OBJECT ({})

				OBJECT = dict() # new dict

				result = None
				last_was_comma = False
				key = None
				message = "unable to decode object"
				while 1:

					# inside of an object must be a series of object members (separated with commas) or closing brace, anything else is an error

					result = self.match_with_result(SEQUENCE)
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
						if not key:
							message = "unable to decode string for object member key!"
							break

						# next is colon or error
						result = self.match_with_result(SEQUENCE)
						name = next_result.name()
						if name != ':':
							# error if next isn't colon
							message = "expected colon (:)"
							break

						# next is value or error
						result = self.match_with_result(SEQUENCE)

						value = self.decode_result(result)
						if not value:
							#if (snap_event_noargs(self, "errored") != (any)"TRUE"){
							#	message = "unable to decode object value";
							#}
							# otherwise assume result has been assigned to errors in "DECODE_RESULT" call...
							break

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

				return None

			elif name == '[':
				# DECODE ARRAY ([])
				#_return = _snap_event(self, (any)"DECODE_ARRAY", MSG);

				ARRAY = [] # init even if empty

				result = None
				message = "unable to decode array"
				last_was_comma = False
				while 1:

					result = self.match_with_result(SEQUENCE)
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
						"""
						snap_event_noargs(&result, "DELETE");

						result = (SnapNode)snap_event(self, "MATCH_WITH_RESULT", "sequence", SEQUENCE);

						SnapNode value = (SnapNode)snap_event(self, "DECODE_RESULT", "result", result);
						if (!value){
							if (snap_event_noargs(self, "errored") == (any)"TRUE"){
								message = "unable to decode array value";
							}
							break;
						}
						if (snap_event(&ARRAY, "APPEND", value) == (any)"ERROR"){
							message = "unable to append item to array";
							break;
						}
						"""
					last_was_comma = False

				#snap_event_noargs(self, "SET_ERROR", "result", RESULT, "message", "unable to decode array");

				#if (result)
				#	snap_event(self, "SET_ERROR", "result", result, "message", message);

				return None
				
			"""
			else if (snap_strsame(name, "string")){
				// TODO return SnapString with sequence source
				snap_warning("string decode not implemented");
			}
			else if (snap_strsame(name, "number")){
				// TODO return number type for format...  basically int or double (how to handle exponent?  just double?)
				snap_warning("number decode not implemented");
			}
			else if (snap_strsame(name, "true")){
				_return = (any)SnapNode_create(SNAP_ENV, SnapBoolean_event, "value", "TRUE");
			}
			else if (snap_strsame(name, "false")){
				_return = (any)SnapNode_create(SNAP_ENV, SnapBoolean_event, "value", "FALSE");
			}
			else if (snap_strsame(name, "null")){
				_return = (any)SnapNode_create(SNAP_ENV, ParseqJSONnull_event);
			}

			else {
				// error
				snap_event_noargs(self, "SET_ERROR", "result", RESULT, "message", "unknown result"); // TODO pass in "result" and "message"
			}
			"""

			return _return

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
			integer = OR('0', AND(digit1to9, REPEAT(digit))) # zero on it's own, or number not starting with zero
			fraction = AND(decimal, REPEAT(digit, min=1, capture=True))
			exponent = AND(ANY('e','E'), OPTIONAL(sign), REPEAT(digit, min=1, capture=True))
			number = AND(OPTIONAL(sign), integer, OPTIONAL(fraction), OPTIONAL(exponent))

			#ignore = REPEAT(ANY(' ', '\t', '\n', '\r'), min=1,
			#	name='ignore', capture=False, suppress=True)
			ignore = ANY(' ', '\t', '\n', '\r',
				name='ignore', capture=False, suppress=True)


			# TODO recognize full terms, but not full array and objects, so we can just consume the terms and validate they are correct for the current context (so we don't have to match grammar to the end)

			self.set(items=[

				string,

				symbol,
				keyword,
				number,

				ignore,

				ERROR
				])

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

	ENV.JSONDecoder = JSONDecoder


def main(ENV):

	build(ENV)

	with open('test.json', 'rb') as openfile:
		sequence = ENV.ParseqSequence(openfile.read().decode('utf8'))

	decoder = ENV.JSONDecoder()
	while 1:
		#result = decoder.search(sequence)
		result = decoder.search_with_result(sequence)
		if not result:
			break
		elif result.name() == 'ERROR':
			#ENV.snap_error(result, result.line_info())
			#print('closest', ENV.parseq_debug_closest_match())
			#break
			print(result, repr(result.value()))
		else:
			print(result, repr(result.value()))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


