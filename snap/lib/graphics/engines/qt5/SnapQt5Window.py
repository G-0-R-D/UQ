
def build(ENV):

	SnapWindow = ENV.SnapWindow

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapQt5Window(SnapWindow):

		__slots__ = []

		def engine(self, MSG):
			return ENGINE

		def __init__(self, *a, **k):
			SnapWindow.__init__(self, *a, **k)

	ENGINE.SnapQt5Window = SnapQt5Window
