
from OpenGL.GL import *

def build(ENV):

	SnapShader = ENV.SnapShader

	ENGINE = ENV.graphics.__current_graphics_build__


	def SnapOpenGLShaderProgram_compile_component(SOURCE, GL_SHADER_TYPE):

		if not isinstance(SOURCE, bytes):
			SOURCE = SOURCE.encode() # to bytes

		shader = glCreateShader(GL_SHADER_TYPE)
		glShaderSource(shader, SOURCE)
		glCompileShader(shader)
		status = glGetShaderiv(shader, GL_COMPILE_STATUS)
		assert status != 0, 'opengl shader compile failure ({}): {}'.format(status, glGetShaderInfoLog(shader))
		#return shader
		return shader

	ENV.SnapOpenGLShaderProgram_compile_component = SnapOpenGLShaderProgram_compile_component


	class SnapOpenGLShaderProgram(SnapShader):

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
				program = self.__snap_data__['__engine_data__']
				if program is None:
					program = self.__snap_data__['__engine_data__'] = glCreateProgram()
					assert program != 0, 'error creating program'
				return program

		@ENV.SnapProperty
		class valid:

			def get(self, MSG):
				"()->bool"
				program = self['__engine_data__']
				glValidateProgram(program)
				return glGetProgramiv(program, GL_VALIDATE_STATUS) != GL_FALSE


		@ENV.SnapProperty
		class linked:

			def get(self, MSG):
				"()->bool"

				program = self['__engine_data__']
				return glGetProgramiv(program, GL_LINK_STATUS) != GL_FALSE

		@ENV.SnapProperty
		class status:

			def get(self, MSG):
				"()->str"
				program = self.__snap_data__['__engine_data__']
				if program is not None:
					return glGetProgramInfoLog(program)
				return '<no program>'



		@ENV.SnapProperty
		class vertex_shader:
			def set(self, MSG):
				"(str|SnapOpenGLShaderComponent!)"
				''
				self.__snap_data__['__needs_update__'] = True

		@ENV.SnapProperty
		class fragment_shader:
			def set(self, MSG):
				"(str|SnapOpenGLShaderComponent!)"
				self.__snap_data__['__needs_update__'] = True
				#self.changed(fragment_shader) # TODO



		@ENV.SnapChannel
		def update(self, MSG):
			"()"

		def retrieve(self):
			"""Attempt to retrieve binary for this compiled shader

			Note that binaries for a program are *not* generally portable,
			they should be used solely for caching compiled programs for 
			local use; i.e. to reduce compilation overhead.

			returns (format,binaryData) for the shader program
			"""
			from OpenGL.constants import GLint,GLenum 
			from OpenGL.arrays import GLbyteArray
			size = GLint()
			glGetProgramiv( self, get_program_binary.GL_PROGRAM_BINARY_LENGTH, size )
			result = GLbyteArray.zeros( (size.value,))
			size2 = GLint()
			format = GLenum()
			get_program_binary.glGetProgramBinary( self, size.value, size2, format, result )
			return format.value, result

		def load( self, format, binary ):
			"""Attempt to load binary-format for a pre-compiled shader

			See notes in retrieve
			"""
			get_program_binary.glProgramBinary( self, format, binary, len(binary))
			assert self['valid'] and self['linked']


		def compile(self, **SETTINGS):

			program = self['__engine_data__']
			if not program:
				'create new'
			else:
				'delete?  or just unlink?  can it be re-used'
				# TODO glDetachShader()...

			#if SETTINGS.get('separable'):
			#	glProgramParameteri( program, separate_shader_objects.GL_PROGRAM_SEPARABLE, GL_TRUE )
			#if SETTINGS.get('retrievable'):
			#	glProgramParameteri( program, get_program_binary.GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE )

	
			# TODO control over attribute locations
			attrlocations = SETTINGS.get('attrs')
			if attrlocations:
				ENV.snap_debug('attrs', attrlocations)
				for idx,name in attrlocations.items():
				    glBindAttribLocation(program, idx, name)

			for shader in shaders:
				glAttachShader(program, shader)
			program = ShaderProgram( program )
			glLinkProgram(program)
			assert self['valid'] and self['linked']
			for shader in shaders:
				glDeleteShader(shader) # XXX hang onto the shader components?  we'll delete them after...  then we can detach them too...


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



		def draw(self, CTX):
			''

		def lookup(self, CTX):
			''


		def __init__(self, **SETTINGS):
			SnapShader.__init__(self, **SETTINGS)

	ENGINE.SnapOpenGLShaderProgram = SnapOpenGLShaderProgram
	return SnapOpenGLShaderProgram


def main(ENV):

	VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec3 aPos;
void main() {
	gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
	"""

	FRAGMENT_SHADER_SOURCE = """
#version 330 core
out vec4 FragColor;
void main() {
	FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
	"""


