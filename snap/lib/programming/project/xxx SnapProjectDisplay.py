
def build(ENV):

	SnapProjectInfo = ENV.SnapProjectInfo

	class SnapProjectDisplay(SnapProjectInfo):

		# the renderable aspect of a project

		__slots__ = []



		@ENV.SnapProperty
		class visible_extents:

			'' # TODO


		@ENV.SnapChannel
		def device_event(self, MSG):
			""

			ENV.snap_out('device event', MSG.kwargs.keys())


		@ENV.SnapChannel
		def update(self, MSG):

			for _ in SnapProjectInfo.update(self, MSG):

				print('update a render display') # TODO

				yield

			yield

		def draw(self, CTX):
			return SnapProjectInfo.draw(self, CTX)

		def lookup(self, CTX):
			return SnapProjectInfo.lookup(self, CTX)

		def __init__(self, **SETTINGS):
			SnapProjectInfo.__init__(self, **SETTINGS)

	ENV.SnapProjectDisplay = SnapProjectDisplay
