
# this is a user-level module to test the engine works, can be run as a gui widget or run directly to save the output to an image

# test and demonstrate all standard capabilities of any engine in one collage...

import os

IMG_SAVE = os.path.realpath(__file__) + '.png'

def build(ENV):

	# TODO this needs to be inside task and assigned to gui...

	SnapContainer = ENV.SnapContainer

	#ENGINE = ENV.snap_preferred_engine()

	#snap_incoming = ENV.snap_incoming

	#PATH = ENGINE.Path()

	# TODO simple,complex, and animated for shapes (path, mesh)
	# use text, image as well as shapes and not
	# color, texture, gradient
	# masking
	# composite, particle shaders

	GFX = ENV.GRAPHICS

	class SnapEngineTest(SnapContainer):

		#@snap_incoming
		#def DEVICE(self, SOURCE, *args, **kwargs):
		#	's key to save'

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			text = GFX.Text('hello world')

			self.set(items=[text])

			# TODO add graphics to demonstrate all basic rendering (and hook into animation system to test it out too...)

			# create a container for each renderable example

			# also do a batch render as a series of context commands queued directly into a shader...

			# also render something directly in a draw method

			# TODO ENGINE = ENV.GFX

	return SnapEngineTest

	# TODO init EngineTest and assign to GUI, and start gui loop if not already going?

def main(ENV):

	ENV.graphics.load('QT5')
	ENV.__run_gui__(build(ENV))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

