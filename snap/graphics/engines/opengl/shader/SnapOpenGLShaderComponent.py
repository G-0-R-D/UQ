

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glCreateShader = OpenGL.glCreateShader
	glShaderSource = OpenGL.glShaderSource
	glCompileShader = OpenGL.glCompileShader
	glGetShaderiv = OpenGL.glGetShaderiv
	glGetShaderInfoLog = OpenGL.glGetShaderInfoLog
	glDeleteShader = OpenGL.glDeleteShader

	GL_COMPILE_STATUS = OpenGL.GL_COMPILE_STATUS
	GL_VERTEX_SHADER = OpenGL.GL_VERTEX_SHADER
	GL_FRAGMENT_SHADER = OpenGL.GL_FRAGMENT_SHADER
	GL_GEOMETRY_SHADER = OpenGL.GL_GEOMETRY_SHADER

	SnapNode = ENV.SnapNode

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLShaderComponent(SnapNode):

		# this is the GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER, ... , the pieces of which are linked into a glProgram

		__slots__ = []

		@ENV.SnapProperty
		class __engine_data__:

			def get(self, MSG):
				"()->int"
				return self.__snap_data__['__engine_data__'] or 0

		@ENV.SnapProperty
		class source:
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['__source__']

			set = None

		@ENV.SnapProperty
		class type:
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['__type__']

			set = None

		def __init__(self, source=None, type_name=None, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			# NOTE: the [source] list is because multiple source pieces can be given (to be concatenated internally)
			if isinstance(source, str):
				source = [source]
			elif isinstance(source, bytes):
				source = [source.encode()]
			else:
				raise TypeError('invalid source type for SnapOpenGLShaderComponent', type(source))

			assert isinstance(type_name, str), 'type_name must be string'

			supported_types = {'VERTEX':GL_VERTEX_SHADER, 'FRAGMENT':GL_FRAGMENT_SHADER, 'GEOMETRY':GL_GEOMETRY_SHADER}
			try:
				GL_TYPE = supported_types[type_name.upper()]
			except KeyError:
				raise TypeError('unsupported OpenGL shader component type:', repr(type_name))

			# TODO use str for TYPE, map to gl type internally...

			shader = glCreateShader(GL_TYPE)
			glShaderSource(shader, source)
			glCompileShader(shader)
			status = glGetShaderiv(shader, GL_COMPILE_STATUS)
			assert status != 0, '{} compile failure {}: {}'.format(self.__class__.__name__, status, glGetShaderInfoLog(shader))
			#return shader
			self.__snap_data__['__engine_data__'] = shader
			self.__snap_data__['__source__'] = source
			self.__snap_data__['__type__'] = type_name.upper()

		def __del__(self):
			shader = self.__snap_data__['__engine_data__']
			if shader is not None:
				glDeleteShader(shader)
				del self.__snap_data__['__engine_data__']


	ENGINE.SnapOpenGLShaderComponent = SnapOpenGLShaderComponent
	return SnapOpenGLShaderComponent
