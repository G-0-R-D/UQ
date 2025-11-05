
import os,json

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	SnapProjectBase = ENV.SnapProjectBase

	SnapProjectDisplayFile = ENV.SnapProjectDisplayFile

	# TODO can run headless
	GFX = getattr(ENV, 'GRAPHICS', None)

	if GFX is not None:
		'build shaders...'


	def get_extension(FILEPATH):
		filename = os.path.basename(FILEPATH)
		assert '.' in filename, 'no ext'
		return filename.split('.')[-1]

	class SnapProject(SnapProjectBase):

		__slots__ = []



		# TODO lookup?  just boundary check, draw rect

		@ENV.SnapChannel
		def compile(self, MSG):
			"()"
			return self['info'].compile.__direct__(MSG)

		@ENV.SnapChannel
		def close(self, MSG):
			""
			# TODO

		@ENV.SnapChannel
		def open(self, MSG):
			"(str savefile!)"

			# TODO 

		@open.alias
		def load(self, MSG): pass

		@ENV.SnapChannel
		def save(self, MSG):
			''
			# save json info as project working file
			raise NotImplementedError()


		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			ENV.snap_out('update')

			graphics = []

			x_offset = 0
			for module in self['modules']:
				ENV.snap_debug('add module to scene', module['filepath'])
				d = SnapProjectDisplayFile(module)
				graphics.append(d)
				d['matrix'] = ENV.snap_matrix_t(1,0,0,x_offset, 0,1,0,0, 0,0,1,0, 0,0,0,1)
				x_offset += d['width'] + 100

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



