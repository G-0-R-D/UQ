
def build(ENV):

	class SnapAnimationCurve(object):

		__slots__ = []

		# separate from spline because it is strictly 2D, and keys can't overlap in x
		# plus we can make it very lowlevel...
