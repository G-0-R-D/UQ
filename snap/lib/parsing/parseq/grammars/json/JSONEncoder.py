
def build(ENV):

	ParseqEncoder = ENV.ParseqEncoder

	class JSONEncoder(ParseqEncoder):

		def encode_to_strings(self, OBJECT, **SETTINGS):


			indent = SETTINGS.get('indent', None)
			indent_level = SETTINGS.get('indent_level', 0)

			if indent is None:
				INDENT = lambda : ''
				NEWLINE = lambda : ''
			else:
				INDENT = lambda : indent_level * indent
				NEWLINE = lambda : '\n'

			# TODO recursive call, and yield string

			if isinstance(OBJECT, (list, tuple)):

				if isinstance(OBJECT, tuple) and 'strict':
					'' # TODO raise?

				yield '[' + NEWLINE()

				yield ']' + NEWLINE()

			elif isinstance(OBJECT, dict):
				yield '{'

				# TODO object entries
				for key,value in OBJECT.items():
					# TODO raise if key is number (can only be string?)
					'encode key'
					yield ':'
					'encode value'
			
				yield '}'

			elif isinstance(OBJECT, (str, bytes)):
				raise NotImplementedError(type(OBJECT))

			elif isinstance(OBJECT, (int, float)):
				raise NotImplementedError(type(OBJECT))

			elif OBJECT is True:
				yield 'true'
			elif OBJECT is False:
				yield 'false'

			elif OBJECT is None:
				yield 'null'

			else:
				raise TypeError(type(OBJECT))

		def __init__(self, *args, **kwargs):
			ParseqEncoder.__init__(self, *args, **kwargs)


			# TODO take a dict tree and turns it into string, write to passed IO, if no IO provided (NULL) then simply reports the required size to write
			# TODO this would require SnapList to have event_handler for instance checking, and all types would have to be instance checkable...


			# TODO make it possible to "SET_PRETTY" to default formatting to add spacing and indentation (it just adds it to some formatting dict...
			# encoders should use callbacks to do special formatting (maybe just internal method that subclass can override?)

def main(ENV):

	build(ENV)

	raise NotImplementedError()

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

