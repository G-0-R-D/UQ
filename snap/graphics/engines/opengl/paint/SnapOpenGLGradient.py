

def build(ENV):
	
	SnapGradient = ENV.SnapGradient

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLGradient(SnapGradient):

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQtEngine"""
				return ENGINE

		def __init__(self, *args, **kwargs):
			SnapGradient.__init__(self, *args, **kwargs)

			# TODO
			raise NotImplementedError()


	ENGINE.SnapOpenGLGradient = SnapOpenGLGradient
	return SnapOpenGLGradient
