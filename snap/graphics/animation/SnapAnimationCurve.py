
def build(ENV):

	class SnapAnimationCurve(object):

		__slots__ = []

		# separate from spline because it is strictly 2D, and keys can't overlap in x
		# plus we can make it very lowlevel...

		# support from description to pull from a Spline: self['description'] = Spline()['description'] and just ignore 3D elements and unsupported types?
