
from OpenGL.GL import *

import os

def build(ENV):

	obj_open = ENV.__build__('snap.graphics.engines.opengl.shape.obj_loader')

	SnapMesh = ENV.SnapMesh

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

		@ENV.SnapChannel
		def open(self, MSG):
			"(str objpath)"

			objpath = MSG.unpack('objpath', None)

			if not os.path.exists(objpath):
				raise OSError('not an obj file?', repr(objpath))

			# TODO
			obj_data = obj_open(objpath)

			ENV.snap_out('obj data', obj_data)

			
			

		@ENV.SnapChannel
		def close(self, MSG):
			"()"
			engine_data = self.__snap_data__['__engine_data__']
			if engine_data:
				for t,ID in engine_data.items():
					if ID is not None:
						glDeleteBuffers(1, ID)
				del self.__snap_data__['__engine_data__']

		def _assign(self, VERTICES, INDICES, *a, **k):
			# TODO VERTICES and INDICES are SnapBytes?  TODO groups?

			#MESH = self._ref
			#vertices = MESH._vertices
			#indices = MESH._indices

			data = self['__engine_data__']
			VBO = data['vertices']
			EBO = data['indices']

			#VAO = glGenVertexArrays(1)
			#glBindVertexArray(VAO)

			# TODO: if self._engine_data: edit existing, delete and create new, ... ?

			# TODO: buffer subdata?

			glBindBuffer(GL_ARRAY_BUFFER, VBO)
			glBufferData(GL_ARRAY_BUFFER, VERTICES.nbytes, VERTICES, GL_STATIC_DRAW)
			# TODO: mark normal, texture, etc... axes and step in api, and use that to bind shader config!

			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
			glBufferData(GL_ELEMENT_ARRAY_BUFFER, VERTICES.nbytes, VERTICES, GL_STATIC_DRAW)
			


		def __del__(self):
			self.close()

	ENGINE.SnapOpenGLMesh = SnapOpenGLMesh
	return SnapOpenGLMesh

def main(ENV):

	''

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OPENGL'))

