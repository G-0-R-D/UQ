
def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage

	class SnapString(SnapPrimitive):

		__slots__ = []
	
		def __compare__(self, OTHER):
			return NotImplementedError()

		#@property
		#def data(self):
		#	return SnapPrimitive.data(self) or ''

		def __setitem__(self, KEY, VALUE):
			if isinstance(KEY, str) and KEY == 'data':
				if VALUE is not None:
					assert isinstance(VALUE, str), 'must be string type'

			return SnapPrimitive.__setitem__(self, KEY, VALUE)

		def __init__(self, data=None):
			SnapPrimitive.__init__(self, data=data)

			#self.__snap_input__(SnapMessage(value))


	ENV.SnapString = SnapString

