

def build(ENV):
	
	SnapGradient = ENV.SnapGradient

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapQt5Gradient(SnapGradient):

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQtEngine"""
				return ENGINE

		def __init__(self, *args, **kwargs):
			SnapGradient.__init__(self, *args, **kwargs)

			# TODO
			ENV.snap_warning("not implemented")


	ENGINE.SnapQt5Gradient = SnapQt5Gradient
	return SnapQt5Gradient
