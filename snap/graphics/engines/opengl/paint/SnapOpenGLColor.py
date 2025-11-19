
def build(ENV):

	SnapColor = ENV.SnapColor

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLColor(SnapColor):

		__slots__ = []

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapOpenGLEngine"""
				return ENGINE


	ENGINE.SnapOpenGLColor = SnapOpenGLColor
	return SnapOpenGLColor
