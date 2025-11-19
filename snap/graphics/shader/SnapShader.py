
def build(ENV):

	SnapEngineData = ENV.SnapEngineData

	class SnapShader(SnapEngineData):

		__slots__ = []

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				#raise NotImplementedError()

			def set(self, MSG):
				"(snap_extents_t!)"
				#raise NotImplementedError()


		@ENV.SnapChannel
		def update(self, MSG):
			"(SnapNode?)"
			pass

		def draw(self, CTX):
			CTX.cmd_render_subitems()

		def lookup(self, CTX):
			CTX.cmd_render_subitems()

		def __init__(self, **SETTINGS):
			SnapEngineData.__init__(self, **SETTINGS)

	ENV.SnapShader = SnapShader

