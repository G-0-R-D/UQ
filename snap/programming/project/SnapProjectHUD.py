
def build(ENV):

	class SnapProjectHUD(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class loading_graphic:

			def get(self, MSG):
				"()->SnapContainer"
				return self.__snap_data__['loading_graphic']

			def set(self, MSG):
				"(SnapContainer!)"
				load = MSG.args[0]
				# TODO assign loading graphic into the corner or something...

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

	ENV.SnapProjectHUD = SnapProjectHUD
