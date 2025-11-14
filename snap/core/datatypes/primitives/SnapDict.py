
def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	class SnapDict(SnapPrimitive):

		__slots__ = []

		def __compare__(self, OTHER):
			raise NotImplementedError('__compare__')

		def __init__(self, **ENTRIES):
			SnapPrimitive.__init__(self)

			# TODO
			self['data'] = ENTRIES

			# TODO compose events for add/remove/...?


		def __bool__(self):
			return bool(self['data'])


	ENV.SnapDict = SnapDict
