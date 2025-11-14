
# everything is really implemented in the engine subclass, but adding this class for completeness

def build(ENV):

	SnapPaint = ENV.SnapPaint

	class SnapGradient(SnapPaint):

		__slots__ = []

		#def set(self, MSG):
		#	return SnapPaint.set(self, MSG)

		def __init__(self, **SETTINGS):
			SnapPaint.__init__(self, **SETTINGS)


	ENV.SnapGradient = SnapGradient
