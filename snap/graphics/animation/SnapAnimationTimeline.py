
def build(ENV):

	class SnapAnimationTimeline(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class frame:
			'' # TODO

		@ENV.SnapProperty
		class time:

			'' # TODO where 0 is start of timeline

		@ENV.SnapProperty
		class time_range:
			'' # TODO limit time range, or not?

		@ENV.SnapProperty
		class channels:

			def get(self, MSG):
				'()->list(*SnapAnimationChannel)"


		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

	ENV.SnapAnimationTimeline = SnapAnimationTimeline
