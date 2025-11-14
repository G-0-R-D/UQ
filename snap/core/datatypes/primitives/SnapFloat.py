
def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage

	class SnapFloat(SnapPrimitive):

		__slots__ = []

		def __compare__(self, OTHER):

			raise NotImplementedError('__compare__')

			# TODO all types?  including raw int/float/...?

			self_data = self['data']

			if OTHER is None:
				if self_data is None:
					return 0
				return 1

			other_data = OTHER['data']
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
		#	return SnapPrimitive.data(self) or 0.

		def __setitem__(self, KEY, VALUE):

			if isinstance(KEY, str) and KEY == 'data':
				VALUE = float(VALUE or 0.0)

			return SnapPrimitive.__setitem__(self, KEY, VALUE)


		def __bool__(self):
			return bool(self['data'])

		def __init__(self, data=0.):
			SnapPrimitive.__init__(self, data=data)


			#if not isinstance(value, (float,int)) and isinstance(value, (ENV.SnapFloat, ENV.SnapInt)):
			#	value = value.__snap_bytes__

		# TODO compare, eq, lt, gt, etc...



	ENV.SnapFloat = SnapFloat
