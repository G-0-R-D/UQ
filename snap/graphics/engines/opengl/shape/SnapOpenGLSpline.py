
# TODO splines?

def build(ENV):

	SnapSpline = ENV.SnapSpline

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLSpline(SnapSpline):
		__slots__ = []


		# TODO NURBS?

	ENGINE.SnapOpenGLSpline = SnapOpenGLSpline
	return SnapOpenGLSpline

