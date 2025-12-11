
def build(ENV):

	class SnapAnimationCurve(object):

		__slots__ = []

		# strictly 2D points (x = time, y = value)
		# x must keep getting bigger (cannot move left, or even to same position without overwrite)
		
		# support from description to pull from a Spline: self['description'] = Spline()['description'] and just ignore 3D elements and unsupported types?
			# -- but ignore 3rd axis if present, and disallow x < last x (clamp + remove overlapping)

		# points are linear, bezier, constant...
