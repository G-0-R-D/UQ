
def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage

	#SnapEvent = ENV.SnapEvent
	#SnapOutput = ENV.SnapOutput

	class SnapBool(SnapPrimitive):

		__slots__ = []

		def __compare__(self, OTHER):

			data = bool(self['data'])

			if data == OTHER:
				return 0
			elif data is False:
				return -1
			else:
				return 1

		#@property
		#def data(self):
		#	return bool(SnapPrimitive.data(self))

		#def set(self, MSG):

		#	data = bool(MSG.unpack('data', None)[0])

		#	return SnapPrimitive.set(self, SnapMessage(data=data))


		def __bool__(self):
			return bool(self['data'])


		def __init__(self, data=False):
			SnapPrimitive.__init__(self, data=data)


	ENV.SnapBool = SnapBool

