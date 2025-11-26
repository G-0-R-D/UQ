
import os

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glGenBuffers = OpenGL.glGenBuffers
	glDeleteBuffers = OpenGL.glDeleteBuffers
	glBindBuffer = OpenGL.glBindBuffer
	glBufferData = OpenGL.glBufferData

	GL_STATIC_DRAW = OpenGL.GL_STATIC_DRAW
	GL_ARRAY_BUFFER = OpenGL.GL_ARRAY_BUFFER
	GL_ELEMENT_ARRAY_BUFFER = OpenGL.GL_ELEMENT_ARRAY_BUFFER

	SnapMesh = ENV.SnapMesh

	obj_reader = ENV.__build__('snap.graphics.engines.opengl.shape.obj_reader')

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLMesh(SnapMesh):

		__slots__ = []

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
					}

				return d

		@ENV.SnapProperty
		class filepath:

			def set(self, MSG):
				"(str!)"
				path = MSG.args[0]
				self.open(path=path)

			get = None

		@filepath.alias
		class objfilepath: pass

		@filepath.alias
		class objfile: pass

		@ENV.SnapChannel
		def open(self, MSG):
			"(str path)"

			objpath = MSG.unpack('path', None)

			if not os.path.exists(objpath):
				raise OSError('path does not exist:', repr(objpath))

			elif not objpath.endswith('.obj'):
				raise OSError('not an obj file?', repr(objpath))

			# TODO
			#obj_data = obj_open(objpath)

			#ENV.snap_out('obj data', obj_data)
			raise NotImplementedError()


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
						glDeleteBuffers(1, ID)
				del self.__snap_data__['__engine_data__']


		def _assign(self, VERTICES, INDICES, FORMAT, *a, **k):
			# TODO VERTICES and INDICES are SnapBytes?  TODO groups?

			# TODO store all vertices and indices together, but also allow adding them to a vertex group?
			#	-- when opening meshes from obj file add each object into it's own group?

			# TODO kind of like how image is always RGBA, mesh vertices will always be (position(x,y,z), normal(x,y,z), texture(u,v), ...)

			data = self['__engine_data__']
			# TODO format! (('vertices',3), ('normals',3), ('uv',2))
			VBO = data['vertices']
			EBO = data['indices']

			#VAO = glGenVertexArrays(1)
			#glBindVertexArray(VAO)

			# TODO: if self._engine_data: edit existing, delete and create new, ... ?

			# TODO: buffer subdata?

			glBindBuffer(GL_ARRAY_BUFFER, VBO)
			if VERTICES is not None:
				glBufferData(GL_ARRAY_BUFFER, VERTICES.nbytes, VERTICES, GL_STATIC_DRAW)
			else:
				glBufferData(GL_ARRAY_BUFFER, 0, None, GL_STATIC_DRAW)
			
			# TODO: mark normal, texture, etc... axes and step in api, and use that to bind shader config!

			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
			if INDICES is not None:
				glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDICES.nbytes, INDICES, GL_STATIC_DRAW)
			else:
				glBufferData(GL_ELEMENT_ARRAY_BUFFER, 0, None, GL_STATIC_DRAW)
			

		@classmethod
		def from_objfile(CLASS, FILEPATH):
			'where we return a new mesh instance for each mesh object in the file?' # TODO
			#	-- also try to load directly into the mesh, with as little intermediary buffering as possible...


		def __del__(self):
			self.close()

	ENGINE.SnapOpenGLMesh = SnapOpenGLMesh
	return SnapOpenGLMesh

def main(ENV):

	GFX = ENV.GRAPHICS

	# TODO should mesh store multiple 'objects'?  vertex groups?
	#m = GFX.Mesh(filepath='obj/suzanne.obj')
	with open('obj/suzanne.obj', 'r') as openfile:
		for line in openfile:
			print(repr(line))


	

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OPENGL'))

