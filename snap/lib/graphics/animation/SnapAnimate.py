
# TODO this is a tweener class, user can init with source matrix, target matrix, and interpolation curve and then it will start animating (like how SnapTimer works)
#	-- if the reference to this instance is lost then animation will jump to completed point, user has to hang onto the nodes until they are finished

def build(ENV):

	class SnapAnimate(SnapNode):

		__slots__ = []

		# TODO user can change the rate while it's running, like the timers ("interval")

		# TODO can animate matrix, float or int...?
		#	-- maybe it's more that this drives the time/value with a curve and then we can map that separately?  but this makes it easy to quickly animate a transformable?

		def __init__(self, SOURCE, TARGET, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

	ENV.SnapAnimate = SnapAnimate
