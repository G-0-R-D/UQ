
# https://en.wikibooks.org/wiki/OpenGL_Programming/Modern_OpenGL_Tutorial_Text_Rendering_02

def build(ENV):

	SnapText = ENV.SnapText

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLText(SnapText):

		__slots__ = []

		# TODO!
		# https://www.youtube.com/watch?v=CGZRHJvJYIg


	ENGINE.SnapOpenGLText = SnapOpenGLText
	return SnapOpenGLText
