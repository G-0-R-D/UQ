
def build(ENV):

	SnapEngineData = ENV.SnapEngineData

	class SnapPaint(SnapEngineData):

		__slots__ = []

		# TODO fill the painter by calculating an extents that is inverse to the painter current matrix...


		def __init__(self, **SETTINGS):
			SnapEngineData.__init__(self, **SETTINGS)

	ENV.SnapPaint = SnapPaint


