
def build(ENV):

	class SnapProjectHUD(SnapContainer):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

	ENV.SnapProjectHUD = SnapProjectHUD
