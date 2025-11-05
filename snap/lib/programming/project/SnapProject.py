
import os,json

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	SnapProjectBase = ENV.SnapProjectBase

	SnapProjectFile = ENV.SnapProjectFile

	# TODO can run headless
	GFX = getattr(ENV, 'GRAPHICS', None)

	if GFX is not None:
		'build shaders...'


	class SnapProject(SnapProjectBase):

		__slots__ = []



		# TODO lookup?  just boundary check, draw rect

		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			ENV.snap_out('update')

			graphics = []

			x_offset = 0
			for filepath in self['files']:
				ENV.snap_debug('add module to scene', filepath)
				d = SnapProjectFile(self, filepath=filepath)
				graphics.append(d)
				d['matrix'] = ENV.snap_matrix_t(1,0,0,x_offset, 0,1,0,0, 0,0,1,0, 0,0,0,1)
				x_offset += d['width'] + 100
				ENV.snap_out("step", d['width'], x_offset)

			self['children'] = graphics
				
			


		def __init__(self, **SETTINGS):
			SnapProjectBase.__init__(self, **SETTINGS)

	ENV.SnapProject = SnapProject
	return SnapProject

def main(ENV):
	ENV.__run_gui__(ENV.SnapProject, packages=["../../../../demo/programming/hello_world/project/"])

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())



