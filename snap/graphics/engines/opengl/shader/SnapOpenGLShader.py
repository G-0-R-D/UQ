
from collections import namedtuple
SnapOpenGLShaderInput = namedtuple('SnapOpenGLShaderInput', ['location', 'name', 'type', 'size'])
SnapOpenGLShaderUniform = namedtuple('SnapOpenGLShaderUniform', ['location', 'name', 'type', 'size'])

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glCreateProgram = OpenGL.glCreateProgram
	glAttachShader = OpenGL.glAttachShader
	glLinkProgram = OpenGL.glLinkProgram
	glGetProgramInfoLog = OpenGL.glGetProgramInfoLog
	glValidateProgram = OpenGL.glValidateProgram
	glGetProgramiv = OpenGL.glGetProgramiv
	glDeleteProgram = OpenGL.glDeleteProgram
	GLchar = OpenGL.GLchar
	GLenum = OpenGL.GLenum
	GLint = OpenGL.GLint
	GLsizei = OpenGL.GLsizei
	glGetAttribLocation = OpenGL.glGetAttribLocation
	glGetActiveAttrib = OpenGL.glGetActiveAttrib
	glUseProgram = OpenGL.glUseProgram
	glGetActiveUniform = OpenGL.glGetActiveUniform

	GL_VALIDATE_STATUS = OpenGL.GL_VALIDATE_STATUS
	GL_FALSE = OpenGL.GL_FALSE
	GL_LINK_STATUS = OpenGL.GL_LINK_STATUS
	GL_ACTIVE_ATTRIBUTES = OpenGL.GL_ACTIVE_ATTRIBUTES
	GL_ACTIVE_ATTRIBUTES = OpenGL.GL_ACTIVE_ATTRIBUTES
	GL_ACTIVE_ATTRIBUTE_MAX_LENGTH = OpenGL.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH
	GL_ACTIVE_UNIFORM_MAX_LENGTH = OpenGL.GL_ACTIVE_UNIFORM_MAX_LENGTH
	GL_ACTIVE_UNIFORMS = OpenGL.GL_ACTIVE_UNIFORMS

	# https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGetActiveAttrib.xhtml
	# all shader input variable types (as they are written in glsl):
	INPUT_TYPES = {
		OpenGL.GL_FLOAT:'float',
		OpenGL.GL_FLOAT_VEC2:'vec2',
		OpenGL.GL_FLOAT_VEC3:'vec3',
		OpenGL.GL_FLOAT_VEC4:'vec4',
		OpenGL.GL_FLOAT_MAT2:'mat2',
		OpenGL.GL_FLOAT_MAT3:'mat3',
		OpenGL.GL_FLOAT_MAT4:'mat4',
		OpenGL.GL_FLOAT_MAT2x3:'mat2x3',
		OpenGL.GL_FLOAT_MAT2x4:'mat2x4',
		OpenGL.GL_FLOAT_MAT3x2:'mat3x2',
		OpenGL.GL_FLOAT_MAT3x4:'mat3x4',
		OpenGL.GL_FLOAT_MAT4x2:'mat4x2',
		OpenGL.GL_FLOAT_MAT4x3:'mat4x3',
		OpenGL.GL_INT:'int',
		OpenGL.GL_INT_VEC2:'ivec2',
		OpenGL.GL_INT_VEC3:'ivec3',
		OpenGL.GL_INT_VEC4:'ivec4',
		OpenGL.GL_UNSIGNED_INT:'uint',
		OpenGL.GL_UNSIGNED_INT_VEC2:'uvec2',
		OpenGL.GL_UNSIGNED_INT_VEC3:'uvec3',
		OpenGL.GL_UNSIGNED_INT_VEC4:'uvec4',
		OpenGL.GL_DOUBLE:'double',
		OpenGL.GL_DOUBLE_VEC2:'dvec2',
		OpenGL.GL_DOUBLE_VEC3:'dvec3',
		OpenGL.GL_DOUBLE_VEC4:'dvec4',
		OpenGL.GL_DOUBLE_MAT2:'dmat2',
		OpenGL.GL_DOUBLE_MAT3:'dmat3',
		OpenGL.GL_DOUBLE_MAT4:'dmat4',
		OpenGL.GL_DOUBLE_MAT2x3:'dmat2x3',
		OpenGL.GL_DOUBLE_MAT2x4:'dmat2x4',
		OpenGL.GL_DOUBLE_MAT3x2:'dmat3x2',
		OpenGL.GL_DOUBLE_MAT3x4:'dmat3x4',
		OpenGL.GL_DOUBLE_MAT4x2:'dmat4x2',
		OpenGL.GL_DOUBLE_MAT4x3:'dmat4x3',
		}
	# https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGetActiveUniform.xhtml
	UNIFORM_TYPES = {
		OpenGL.GL_BOOL:'bool',
		OpenGL.GL_BOOL_VEC2:'bvec2',
		OpenGL.GL_BOOL_VEC3:'bvec3',
		OpenGL.GL_BOOL_VEC4:'bvec4',
		OpenGL.GL_SAMPLER_1D:'sampler1D',
		OpenGL.GL_SAMPLER_2D:'sampler2D',
		OpenGL.GL_SAMPLER_3D:'sampler3D',
		OpenGL.GL_SAMPLER_CUBE:'samplerCube',
		OpenGL.GL_SAMPLER_1D_SHADOW:'sampler1DShadow',
		OpenGL.GL_SAMPLER_2D_SHADOW:'sampler2DShadow',
		OpenGL.GL_SAMPLER_1D_ARRAY:'sampler1DArray',
		OpenGL.GL_SAMPLER_2D_ARRAY:'sampler2DArray',
		OpenGL.GL_SAMPLER_1D_ARRAY_SHADOW:'sampler1DArrayShadow',
		OpenGL.GL_SAMPLER_2D_ARRAY_SHADOW:'sampler2DArrayShadow',
		OpenGL.GL_SAMPLER_2D_MULTISAMPLE:'sampler2DMS',
		OpenGL.GL_SAMPLER_2D_MULTISAMPLE_ARRAY:'sampler2DMSArray',
		OpenGL.GL_SAMPLER_CUBE_SHADOW:'samplerCubeShadow',
		OpenGL.GL_SAMPLER_BUFFER:'samplerBuffer',
		OpenGL.GL_SAMPLER_2D_RECT:'sampler2DRect',
		OpenGL.GL_SAMPLER_2D_RECT_SHADOW:'sampler2DRectShadow',
		OpenGL.GL_INT_SAMPLER_1D:'isampler1D',
		OpenGL.GL_INT_SAMPLER_2D:'isampler2D',
		OpenGL.GL_INT_SAMPLER_3D:'isampler3D',
		OpenGL.GL_INT_SAMPLER_CUBE:'isamplerCube',
		OpenGL.GL_INT_SAMPLER_1D_ARRAY:'isampler1DArray',
		OpenGL.GL_INT_SAMPLER_2D_ARRAY:'isampler2DArray',
		OpenGL.GL_INT_SAMPLER_2D_MULTISAMPLE:'isampler2DMS',
		OpenGL.GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:'isampler2DMSArray',
		OpenGL.GL_INT_SAMPLER_BUFFER:'isamplerBuffer',
		OpenGL.GL_INT_SAMPLER_2D_RECT:'isampler2DRect',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_1D:'usampler1D',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_2D:'usampler2D',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_3D:'usampler3D',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_CUBE:'usamplerCube',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_1D_ARRAY:'usampler2DArray',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_2D_ARRAY:'usampler2DArray',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE:'usampler2DMS',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:'usampler2DMSArray',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_BUFFER:'usamplerBuffer',
		OpenGL.GL_UNSIGNED_INT_SAMPLER_2D_RECT:'usampler2DRect',
		OpenGL.GL_IMAGE_1D:'image1D',
		OpenGL.GL_IMAGE_2D:'image2D',
		OpenGL.GL_IMAGE_3D:'image3D',
		OpenGL.GL_IMAGE_2D_RECT:'image2DRect',
		OpenGL.GL_IMAGE_CUBE:'imageCube',
		OpenGL.GL_IMAGE_BUFFER:'imageBuffer',
		OpenGL.GL_IMAGE_1D_ARRAY:'image1DArray',
		OpenGL.GL_IMAGE_2D_ARRAY:'image2DArray',
		OpenGL.GL_IMAGE_2D_MULTISAMPLE:'image2DMS',
		OpenGL.GL_IMAGE_2D_MULTISAMPLE_ARRAY:'image2DMSArray',
		OpenGL.GL_INT_IMAGE_1D:'iimage1D',
		OpenGL.GL_INT_IMAGE_2D:'iimage2D',
		OpenGL.GL_INT_IMAGE_3D:'iimage3D',
		OpenGL.GL_INT_IMAGE_2D_RECT:'iimage2DRect',
		OpenGL.GL_INT_IMAGE_CUBE:'iimageCube',
		OpenGL.GL_INT_IMAGE_BUFFER:'iimageBuffer',
		OpenGL.GL_INT_IMAGE_1D_ARRAY:'iimage1DArray',
		OpenGL.GL_INT_IMAGE_2D_ARRAY:'iimage2DArray',
		OpenGL.GL_INT_IMAGE_2D_MULTISAMPLE:'iimage2DMS',
		OpenGL.GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY:'iimage2DMSArray',
		OpenGL.GL_UNSIGNED_INT_IMAGE_1D:'uimage1D',
		OpenGL.GL_UNSIGNED_INT_IMAGE_2D:'uimage2D',
		OpenGL.GL_UNSIGNED_INT_IMAGE_3D:'uimage3D',
		OpenGL.GL_UNSIGNED_INT_IMAGE_2D_RECT:'uimage2DRect',
		OpenGL.GL_UNSIGNED_INT_IMAGE_CUBE:'uimageCube',
		OpenGL.GL_UNSIGNED_INT_IMAGE_BUFFER:'uimageBuffer',
		OpenGL.GL_UNSIGNED_INT_IMAGE_1D_ARRAY:'uimage1DArray',
		OpenGL.GL_UNSIGNED_INT_IMAGE_2D_ARRAY:'uimage2DArray',
		OpenGL.GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE:'uimage2DMS',
		OpenGL.GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY:'uimage2DMSArray',
		OpenGL.GL_UNSIGNED_INT_ATOMIC_COUNTER:'atomic_uint',
	}
	UNIFORM_TYPES.update(INPUT_TYPES) # all the same plus more!

	SnapShader = ENV.SnapShader

	ENGINE = ENV.graphics.__current_graphics_build__

	SnapOpenGLShaderComponent = ENGINE.SnapOpenGLShaderComponent

	ENV.SnapOpenGLShaderInput = SnapOpenGLShaderInput
	ENV.SnapOpenGLShaderUniform = SnapOpenGLShaderUniform

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

					del self.__snap_data__['__inputs__']

					shaders = [self.__getitem__(n) for n in ('vertex_shader', 'geometry_shader', 'fragment_shader')]
					if not any(shaders):
						program = self.__snap_data__['program'] = 0
						return program

					program = self.__snap_data__['__program__'] = glCreateProgram()

					#ENV.snap_out('new program', program, self.__snap_data__['__program__'])

					for TYPE,s in zip(('VERTEX','GEOMETRY','FRAGMENT'), shaders):
						if s is None: continue
						if not isinstance(s, SnapOpenGLShaderComponent):
							s = SnapOpenGLShaderComponent(s, TYPE)
						glAttachShader(program, s['__engine_data__'])
					glLinkProgram(program)
					if not (self['valid'] and self['linked']):
						raise Exception('OpenGL program error', glGetProgramInfoLog(program))

				return program or 0

			set = None

		@ENV.SnapProperty
		class inputs:
			def get(self, MSG):
				"()->dict(str:int|str)"
				inputs = self.__snap_data__['__inputs__']
				if inputs is None:

					program = self['program']
					if not program:
						inputs = self.__snap_data__['__inputs__'] = ()
						return inputs

					inputs = []

					max_name_length = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)

					count = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTES)

					glNameSize = GLsizei()
					glSize = GLint()
					glType = GLenum()
					glName = (GLchar * max_name_length)()

					idx = 0
					while idx < count:
						glGetActiveAttrib(program, idx, max_name_length, glNameSize, glSize, glType, glName)

						inputs.append(SnapOpenGLShaderInput(
							name=glName.value.decode('utf-8'),
							location=idx,
							size=glSize.value,
							type=INPUT_TYPES[glType.value],
							))

						idx += 1

					fixed = namedtuple(self.__class__.__name__+'_inputs', [i.name for i in inputs])
					inputs = self.__snap_data__['__inputs__'] = fixed(*inputs)

				return inputs

			set = None

		@ENV.SnapProperty
		class uniforms:
			def get(self, MSG):
				"()->dict(str:int|str)"

				uniforms = self.__snap_data__['__uniforms__']
				if uniforms is None:

					program = self['program']
					if not program:
						uniforms = self.__snap_data__['__uniforms__'] = ()
						return uniforms

					uniforms = []

					max_name_length = glGetProgramiv(program, GL_ACTIVE_UNIFORM_MAX_LENGTH)

					count = glGetProgramiv(program, GL_ACTIVE_UNIFORMS)

					glNameSize = GLsizei()
					glSize = GLint()
					glType = GLenum()
					glName = (GLchar * max_name_length)()

					idx = 0
					while idx < count:
						glGetActiveUniform(program, idx, max_name_length, glNameSize, glSize, glType, glName)

						uniforms.append(SnapOpenGLShaderUniform(
							name=glName.value.decode('utf-8'),
							location=idx,
							size=glSize.value,
							type=UNIFORM_TYPES[glType.value],
							))

						idx += 1

					fixed = namedtuple(self.__class__.__name__+'_uniforms', [u.name for u in uniforms])
					uniforms = self.__snap_data__['__uniforms__'] = fixed(*uniforms)

				return uniforms

			set = None

		@uniforms.alias
		class globals: pass


		# TODO mesh_format -> generate (position, normal, uv, ...) based on shader inputs?
			

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
				if source is not None:
					assert isinstance(source, (str,bytes,SnapOpenGLShaderComponent)), 'invalid shader type: {}'.format(type(source))
				self.__snap_data__['vertex_shader'] = source
				self.changed(vertex_shader=source)

		@vertex_shader.alias
		class vertex_source: pass

		@ENV.SnapProperty
		class geometry_shader:
			def get(self, MSG):
				"()->SnapOpenGLShaderComponent"
				return self.__snap_data__['geometry_shader']

			def set(self, MSG):
				"(str|bytes|SnapOpenGLShaderComponent!)"
				source = MSG.args[0]
				assert isinstance(source, (str,bytes,SnapOpenGLShaderComponent)), 'invalid shader type: {}'.format(type(source))
				self.__snap_data__['geometry_shader'] = source
				self.changed(geometry_shader=source)

		@geometry_shader.alias
		class geometry_source: pass

		@ENV.SnapProperty
		class fragment_shader:
			def get(self, MSG):
				"()->SnapOpenGLShaderComponent"
				return self.__snap_data__['fragment_shader']

			def set(self, MSG):
				"(str|bytes|SnapOpenGLShaderComponent!)"
				source = MSG.args[0]
				assert isinstance(source, (str,bytes,SnapOpenGLShaderComponent)), 'invalid shader type: {}'.format(type(source))
				self.__snap_data__['fragment_shader'] = source
				self.changed(fragment_shader=source)

		@fragment_shader.alias
		class fragment_source: pass


		@ENV.SnapChannel
		def changed(self, MSG):
			"()"

			program = self.__snap_data__['__program__']
			if program is not None:
				glDeleteProgram(program)
				del self.__snap_data__['__program__']
				del self.__snap_data__['__inputs__']
				del self.__snap_data__['__uniforms__']
			return SnapShader.changed(self, MSG)

		# TODO retrievable binary?
		#	glProgramParameteri( program, separate_shader_objects.GL_PROGRAM_SEPARABLE, GL_TRUE )
		#	glProgramParameteri( program, get_program_binary.GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE )




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

	SnapContainer = ENV.SnapContainer

	GFX = ENV.graphics['OpenGL']


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
	//COLOR = vec4(1.0, 1.0, 1.0, 1.0) * NORMAL;
	//gl_FragColor = vec4(0.0, 0.6, 0.8, 1.0);// * vec4(NORMAL + .2, 1.0);
	//gl_FragColor = vec4(NORMAL + .2, 1.0);
}
	"""

	class Test(SnapContainer):


		# TODO experiment with different ways of rendering things...
		def draw_image(self, CTX):
			'' # TODO use the ctx quad...  include crop/dimensions and matrix...


		def draw(self, CTX):
			''

		def __init__(self):
			SnapContainer.__init__(self)

			self.shader = GFX.Shader(vertex_source=VERTEX_SHADER_SOURCE, fragment_source=FRAGMENT_SHADER_SOURCE)

			self.triangle = GFX.Mesh()
			self.triangle._assign(*GFX.Mesh.TRIANGLE_DATA)

			program = self.shader['program']

			print(self.shader['inputs'])
			print(self.shader['uniforms'])



	ENV.__run_gui__(Test)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='opengl'))


