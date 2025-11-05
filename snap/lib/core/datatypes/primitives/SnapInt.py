
def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage

	class SnapInt(SnapPrimitive):

		__slots__ = []

		def __compare__(self, OTHER):

			raise NotImplementedError()
			
			# TODO all types?  including raw int/float/...?

			other = MSG.unpack('other', None)

			self_data = self.data

			if other is None:
				if self_data is None:
					return 0
				return 1

			other_data = other.data
			if other_data is None:
				if self_data is None:
					return 0
				return 1

			if self_data == other_data:
				return 0
			elif self_data > other_data:
				return 1
			else:
				return -1

		#@property
		#def data(self):
		#	return SnapPrimitive.data(self) or 0

		def __setitem__(self, KEY, VALUE):

			if isinstance(KEY, str) and KEY == 'data':
				VALUE = int(VALUE or 0)

			return SnapPrimitive.__setitem__(self, KEY, VALUE)

		def __init__(self, data=0):
			SnapPrimitive.__init__(self, data=data)

			#self._value_ = int(value)

		def __bool__(self):
			return bool(self['data'])


	ENV.SnapInt = SnapInt
