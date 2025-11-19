
from OpenGL.GL import *

def build(ENV):

	SnapNode = ENV.SnapNode

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLShaderComponent(SnapNode):

		# this is the fragment shader, the pieces of which are combined into a shader program

		__slots__ = []

		@ENV.SnapProperty
		class __engine_data__:

			def get(self, MSG):
				"()->int"
				return self.__snap_data__['__engine_data__']

		@ENV.SnapProperty
		class source:
			def set(self, MSG):
				"(str!)"
				''

		@ENV.SnapProperty
		class shader:
			def get(self, MSG):
				"()->int"

		@ENV.SnapChannel
		def recompile(self, MSG):
			''

		def __init__(self, source=None, type_name=None, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if not isinstance(SOURCE, bytes):
				SOURCE = SOURCE.encode() # to bytes

			# TODO use str for TYPE, map to gl type internally...

			shader = glCreateShader(TYPE) # TODO support reading from file and get type from the name in there?
			glShaderSource(shader, SOURCE)
			glCompileShader(shader)
			status = glGetShaderiv(shader, GL_COMPILE_STATUS)
			assert status != 0, '{} compile failure {}: {}'.format(self.__class__.__name__, status, glGetShaderInfoLog(shader))
			#return shader
			self.__snap_data__['__engine_data__'] = shader

		def __del__(self):
			shader = self.__snap_data__['__engine_data__']
			if shader is not None:
				glDeleteShader(shader)
				del self.__snap_data__['__engine_data__']


	ENGINE.SnapOpenGLShaderComponent = SnapOpenGLShaderComponent
	return SnapOpenGLShaderComponent
