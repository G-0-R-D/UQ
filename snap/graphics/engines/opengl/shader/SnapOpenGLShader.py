
from OpenGL.GL import *

def build(ENV):

	SnapShader = ENV.SnapShader

	ENGINE = ENV.graphics.__current_graphics_build__

	SnapOpenGLShaderComponent = ENGINE.SnapOpenGLShaderComponent

	def _as_component(SOURCE, TYPE):
		if SOURCE is not None:
			if not isinstance(SOURCE, SnapOpenGLShaderComponent):
				SOURCE = SnapOpenGLShaderComponent(SOURCE, TYPE)
			else:
				assert SOURCE['type'] == TYPE, 'wrong component type! {} != {}'.format(repr(SOURCE['type']), repr(TYPE))
		return SOURCE

	class SnapOpenGLShader(SnapShader):

		# uniforms must be re-bound after calling glUseProgram()

		# TODO organize all the settings and config, then call compile() and then flush() unnecessary data...

		__slots__ = []

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapOpenGLEngine"""
				return ENGINE

		@ENV.SnapProperty
		class __engine_data__:
			def get(self, MSG):
				"()->int"
				return self['program']

			set = None

		@ENV.SnapProperty
		class program:
			def get(self, MSG):
				"()->int"
				program = self.__snap_data__['__program__']
				if program is None:
					program = self.__snap_data__['__program__'] = glCreateProgram()

					ENV.snap_out('new program', program, self.__snap_data__['__program__'])

					for name in ('vertex_shader', 'geometry_shader', 'fragment_shader'):
						component = self.__getitem__(name)
						if component is None:
							continue
						glAttachShader(program, component['__engine_data__'])
					glLinkProgram(program)
					if not (self['valid'] and self['linked']):
						raise Exception('OpenGL program error', glGetProgramInfoLog(program))

			
					# TODO control over attribute locations (try to use shader vars themselves...)
					"""
					attrlocations = SETTINGS.get('attrs')
					if attrlocations:
						ENV.snap_debug('attrs', attrlocations)
						for idx,name in attrlocations.items():
							glBindAttribLocation(program, idx, name)
					"""

					'update vars?'
				return program or 0

			set = None

		@ENV.SnapProperty
		class attributes:
			def get(self, MSG):
				"()->dict(str:int)"
				attrs = self.__snap_data__['__attributes__']
				if attrs is None:
					attrs = self.__snap_data__['__attributes__'] = {}
					# TODO
					raise NotImplementedError()
				return attrs

			def set(self, MSG):
				"(dict(str:SnapNode))"
				# TODO this is user assignment of the variables to use?  or should that be done strictly through SnapProperties?
				raise NotImplementedError()
				

		@ENV.SnapProperty
		class valid:

			def get(self, MSG):
				"()->bool"
				program = self.__snap_data__['__program__']
				if not program:
					return False
				glValidateProgram(program)
				return glGetProgramiv(program, GL_VALIDATE_STATUS) != GL_FALSE


		@ENV.SnapProperty
		class linked:

			def get(self, MSG):
				"()->bool"
				program = self.__snap_data__['__program__']
				if not program:
					return False
				return glGetProgramiv(program, GL_LINK_STATUS) != GL_FALSE

		@ENV.SnapProperty
		class status:

			def get(self, MSG):
				"()->str"
				program = self.__snap_data__['__program__']
				if program is not None:
					return glGetProgramInfoLog(program)
				return '<no program>'



		@ENV.SnapProperty
		class vertex_shader:
			def get(self, MSG):
				"()->SnapOpenGLShaderComponent"
				return self.__snap_data__['vertex_shader']

			def set(self, MSG):
				"(str|bytes|SnapOpenGLShaderComponent!)"
				source = MSG.args[0]
				self.__snap_data__['vertex_shader'] = _as_component(source, 'VERTEX')
				self.changed(vertex_shader=source)

		@ENV.SnapProperty
		class geometry_shader:
			def get(self, MSG):
				"()->SnapOpenGLShaderComponent"
				return self.__snap_data__['geometry_shader']

			def set(self, MSG):
				"(str|bytes|SnapOpenGLShaderComponent!)"
				source = MSG.args[0]
				self.__snap_data__['geometry_shader'] = _as_component(source, 'GEOMETRY')
				self.changed(geometry_shader=source)

		@ENV.SnapProperty
		class fragment_shader:
			def get(self, MSG):
				"()->SnapOpenGLShaderComponent"
				return self.__snap_data__['fragment_shader']

			def set(self, MSG):
				"(str|bytes|SnapOpenGLShaderComponent!)"
				source = MSG.args[0]
				self.__snap_data__['fragment_shader'] = _as_component(source, 'FRAGMENT')
				self.changed(fragment_shader=source)


		@ENV.SnapChannel
		def changed(self, MSG):
			"()"

			program = self.__snap_data__['__program__']
			if program is not None:
				glDeleteProgram(program)
				del self.__snap_data__['__program__']
				del self.__snap_data__['__attributes__']
			return SnapShader.changed(self, MSG)

		# TODO retrievable binary?
		#	glProgramParameteri( program, separate_shader_objects.GL_PROGRAM_SEPARABLE, GL_TRUE )
		#	glProgramParameteri( program, get_program_binary.GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE )


		"""
		def attributes(self):

			# TODO store program as dict, assign 'variables' field for vars...

			num_attributes = glGetProgramiv(self._GLid, GL_ACTIVE_ATTRIBUTES)
			
			for idx in range(num_attributes):
				
				name_length = 64
				glNameSize = constants.GLsizei()
				glSize = constants.GLint()
				glType = constants.GLenum()
				glName = (constants.GLchar * name_length)()
				glGetActiveAttrib(self._GLid, idx, name_length, glNameSize, glSize, glType, glName)

				print(idx, glName.value, glSize.value, glType.value)

				self.vars[glName.value] = glGetAttribLocation(self._GLid, glName)
		"""



		def draw(self, CTX):
			''
			# get the current CTX['program'], set self as new program (if different?), then set back...

		def lookup(self, CTX):
			''


		def __init__(self, **SETTINGS):
			SnapShader.__init__(self, **SETTINGS)

		def __del__(self):
			program = self.__snap_data__['__program__']
			if program is not None:
				glDeleteProgram(program)
				del self.__snap_data__['__program__']

	ENGINE.SnapOpenGLShader = SnapOpenGLShader
	return SnapOpenGLShader


def main(ENV):


	VERTEX_SHADER_SOURCE = """# version 330 core

in vec3 position;
in vec3 normal;
in vec2 uv;

out vec2 UV;
out vec4 NORMAL;

uniform mat4 OFFSET;

void main(){
	UV = uv;
	NORMAL = vec4(position, 1.0);

	gl_Position = vec4(position, 1.0) * OFFSET;
}
	"""

	FRAGMENT_SHADER_SOURCE = """# version 330 core

in vec4 NORMAL;
in vec2 UV;

out vec4 COLOR;

void main(){
	COLOR = vec4(1.0, 1.0, 1.0, 1.0) * NORMAL;
	//gl_FragColor = vec4(0.0, 0.6, 0.8, 1.0);// * vec4(NORMAL + .2, 1.0);
	//gl_FragColor = vec4(NORMAL + .2, 1.0);
}
	"""

