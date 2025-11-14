

def build(ENV):

	Qt5 = ENV.extern.Qt5

	SnapMesh = ENV.SnapMesh

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapQt5Mesh(SnapMesh):

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE

		def __init__(self, **SETTINGS):
			SnapMesh.__init__(self)

			raise NotImplementedError()

	ENGINE.SnapQt5Mesh = SnapQt5Mesh
	return SnapQt5Mesh

