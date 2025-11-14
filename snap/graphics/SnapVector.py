
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapVector(SnapNode):

		# can be used to represent a vector or point, accordingly

		__slots__ = []

		@ENV.SnapProperty
		class vector_t:

			def get(self, MSG):
				"()->snap_vector_t"
				# TODO

			def set(self, MSG):
				"(snap_vector_t!)"
				# TODO

		def magnitude(self):
			''

		def cross_product(self):
			''

		# ...

		def __init__(self, *points, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if len(points) == 2:
				''

			elif len(points) == 3:
				''

			elif len(points) == 4:
				''

			else:
				raise ValueError('{} takes 4 or less points'.format(self.__class__.__name__))

	ENV.SnapVector = SnapVector
