
import os, numpy

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glGenBuffers = OpenGL.glGenBuffers
	glDeleteBuffers = OpenGL.glDeleteBuffers
	glBindBuffer = OpenGL.glBindBuffer
	glBufferData = OpenGL.glBufferData
	glBindVertexArray = OpenGL.glBindVertexArray
	glGenVertexArrays = OpenGL.glGenVertexArrays
	glDeleteVertexArrays = OpenGL.glDeleteVertexArrays
	glEnableVertexAttribArray = OpenGL.glEnableVertexAttribArray
	glVertexAttribPointer = OpenGL.glVertexAttribPointer

	GL_STATIC_DRAW = OpenGL.GL_STATIC_DRAW
	GL_ARRAY_BUFFER = OpenGL.GL_ARRAY_BUFFER
	GL_ELEMENT_ARRAY_BUFFER = OpenGL.GL_ELEMENT_ARRAY_BUFFER
	GL_FLOAT = OpenGL.GL_FLOAT
	GL_FALSE = OpenGL.GL_FALSE

	SnapMesh = ENV.SnapMesh

	obj_reader = ENV.__build__('snap.graphics.engines.opengl.shape.obj_reader')

	ENGINE = ENV.graphics.__current_graphics_build__

	

	class SnapOpenGLMesh(SnapMesh):

		__slots__ = []


		# these are triangulated geometries for convenience
		# use them like: self._assign(*self.TRIANGLE_DATA)
		TRIANGLE_POINT_DATA = (
			# vertex data: position.xy
			numpy.array([
				# CCW
				-1.0, -1.0, # bottom left
				1.0, -1.0, # bottom right
				0.0, 1.0, # top
				], dtype=numpy.float32),
			# indices
			numpy.array([
				0,1,2,
				],dtype=numpy.uint32),
			(('position',2),)
		)

		RECT_POINT_DATA = (
			# vertices: position.xy
			numpy.array([
				# CCW
				-1.0, -1.0, # bottom left
				1.0, -1.0, # bottom right
				1.0, 1.0, # top right
				-1.0, 1.0, # top left
				], dtype=numpy.float32),
			numpy.array([
				0,1,2,
				2,3,0,
				], dtype=numpy.uint32),
			(('position',2),)
		)

		QUAD_POINT_DATA = RECT_POINT_DATA

		# TODO CUBE_POINT_DATA = ()
		# TODO pyramid? icosphere? star?


		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapOpenGLEngine"""
				return ENGINE

		@ENV.SnapProperty
		class __engine_data__:

			def get(self, MSG):
				"()->dict"

				d = self.__snap_data__['__engine_data__']
				if d is None:
					d = self.__snap_data__['__engine_data__'] = {
						'vertices':glGenBuffers(1),
						'indices':glGenBuffers(1),
						'__vao__':glGenVertexArrays(1),
					}
					v = d['vertices']
					i = d['indices']
					vao = d['__vao__']

					glBindVertexArray(vao)

					glBindBuffer(GL_ARRAY_BUFFER, v)
					glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, i)

					glBindVertexArray(0)

				return d


		@ENV.SnapProperty
		class groups:
			# TODO vertices are given a weighting of 0.0 -> 1.0 for group membership, and assigned by index?
			def get(self, MSG):
				''
			def set(self, MSG):
				''

		def get_attributes(self, *NAMES):
			'create array of just the vertices required for the names...'

		def remove_attributes(self, *NAMES):
			''

		def add_attribute(self, NAME, BYTES):
			''

		# TODO insert/remove vertices?  when adding vertices we also need to add indices for the faces...
		# XXX for now we'll keep this strictly .obj file i/o -- editing will come later...
		#	-- TODO also do something similar with splines, load from svg?

		@ENV.SnapChannel
		def load_object(self, MSG):
			"(str filepath!, SnapMatrix|snap_matrix_t matrix?)"
			# TODO load a obj file, possibly by basename like 'cube', and transform it by the matrix if assigned, then add it to the local vertices...

		@ENV.SnapChannel
		def clear(self, MSG):
			"()"
			self._assign(None, None, None)
			

		@ENV.SnapChannel
		def close(self, MSG):
			"()"
			engine_data = self.__snap_data__['__engine_data__']
			if engine_data:
				for t,ID in engine_data.items():
					if ID is not None:
						if t == '__vao__':
							glDeleteVertexArrays(1, [ID])
						else:
							glDeleteBuffers(1, ID)
				del self.__snap_data__['__engine_data__']

		def reformat(self, FORMAT):
			# pad with 0s, calculate normals, and uvs?
			raise NotImplementedError()

		def _assign(self, VERTICES, INDICES, FORMAT, *a, **k):
			# TODO VERTICES and INDICES are SnapBytes?  TODO groups?

			# TODO store all vertices and indices together, but also allow adding them to a vertex group?
			#	-- when opening meshes from obj file add each object into it's own group?

			# TODO kind of like how image is always RGBA, mesh vertices will always be (position(x,y,z), normal(x,y,z), texture(u,v), ...)

			# TODO this represents per-vertex information (position, normal, uv, color, ...) so we will always pack it in per-vertex format...
			#	-- then we can list and attach/detach 'attributes' in a batch operation...

			# TODO support multiple channels per-attribute using auto-naming with numbers?
			#	uv, uv2, uv3, ...  and then shader can generate code automatically?
			#	-- maybe mesh can prep it's shader fragment code?  and that fragment is then added into whatever else...?

			data = self['__engine_data__']
			# TODO format! (('vertices',3), ('normals',3), ('uv',2))
			VBO = data['vertices']
			EBO = data['indices']
			VAO = data['__vao__']

			#VAO = glGenVertexArrays(1)

			# TODO: if self._engine_data: edit existing, delete and create new, ... ?

			# TODO: buffer subdata?

			data = [VERTICES.nbytes, VERTICES] if VERTICES is not None else [0, None]

			glBindBuffer(GL_ARRAY_BUFFER, VBO)
			glBufferData(GL_ARRAY_BUFFER, data[0], data[1], GL_STATIC_DRAW)
			
			# TODO: mark normal, texture, etc... axes and step in api, and use that to bind shader config!

			data = [INDICES.nbytes, INDICES] if INDICES is not None else [0, None]

			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
			glBufferData(GL_ELEMENT_ARRAY_BUFFER, data[0], data[1], GL_STATIC_DRAW)

			glBindVertexArray(VAO)

			position_input = 0 # TODO standardize...
			glVertexAttribPointer(position_input, 2, GL_FLOAT, GL_FALSE, 0, None)#ctypes.c_void_p(0))
			glEnableVertexAttribArray(position_input)

			glBindVertexArray(0)
			

		@classmethod
		def from_objfile(CLASS, FILEPATH, matrix=None):
			M = CLASS()
			M.load_objfile(FILEPATH, matrix=matrix)
			return M

		def __del__(self):
			self.close()

	ENGINE.SnapOpenGLMesh = SnapOpenGLMesh
	return SnapOpenGLMesh

def main(ENV):

	SnapContainer = ENV.SnapContainer

	OGL = ENV.extern.OpenGL
	GFX = ENV.graphics['OpenGL']

	VERTEX_SOURCE = """# version 330 core

uniform mat4 OFFSET_MATRIX;

layout (location=0) in vec2 position;

void main(){
	gl_Position = vec4(position, 0.0, 1.0);// * OFFSET_MATRIX;
}
	"""
	FRAGMENT_SOURCE = """# version 330 core

out vec4 RGBA;

void main(){
	RGBA = vec4(gl_FragCoord.x / 640, gl_FragCoord.y / 480, .8, 1.);
}
	"""

	class Test(SnapContainer):

		# TODO make a camera and connect keyboard to move it around

		def draw(self, CTX):
			
			OGL.glUseProgram(self.shader['program'])

			OGL.glBindVertexArray(self.mesh['__engine_data__']['__vao__'])

			#OGL.glDisable(OGL.GL_CULL_FACE)

			#OGL.glDrawArrays(OGL.GL_TRIANGLES, 0, 3)
			OGL.glDrawElements(OGL.GL_TRIANGLES, 6, OGL.GL_UNSIGNED_INT, None)

			OGL.glBindVertexArray(0)
			OGL.glUseProgram(0)

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			self.vao = OGL.glGenVertexArrays(1)

			self.shader = GFX.Shader(vertex_source=VERTEX_SOURCE, fragment_source=FRAGMENT_SOURCE)

			self.matrix = GFX.Matrix()

			self.mesh = GFX.Mesh()
			self.mesh._assign(*GFX.Mesh.QUAD_POINT_DATA)
			


	ENV.__run_gui__(Test)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OPENGL'))

