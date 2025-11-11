
# this is a user-level module to test the engine works, can be run as a gui widget or run directly to save the output to an image

# test and demonstrate all standard capabilities of any engine in one collage...

import os, random

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

	class SnapGraphicsDemo(SnapContainer):

		#@snap_incoming
		#def DEVICE(self, SOURCE, *args, **kwargs):
		#	's key to save'

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"

			action, device, source = MSG.unpack('action', None, 'device', None, 'source', None)

			if isinstance(device, ENV.SnapDevicePointer):

				if action == 'press' and source in (device.get('buttons') or []) and source['name'] == 'left':

					local_position = MSG.kwargs['local_position']

					x,y = local_position

					self.animated_block_at(x,y)

					#ENV.snap_out('middle button!', action, local_delta)

			

		def animated_block_at(self, X, Y):

			# this is just one option you have for doing an animation (there are many)
			# this one allows the animation process itself to control it's own rate and change actions

			timer = ENV.SnapTimer(None)
			self.__snap_data__['timers'] = (self.__snap_data__['timers'] or []) + [timer]

			def anim():

				block_size = 50

				block = GFX.Spline(description=['L',0,0, block_size,0, block_size,block_size, 0,block_size, 'C'],
					fill=GFX.Color(*[random.random() for i in range(4)]))
				#block = SnapContainer(children=[self]) # just checking :)
				block.translate(X, Y)

				self['children'] = self['children'] + [block]

				timer['interval'] = 1
				yield

				timer['interval'] = .05
				yield

				for i in range(150):
					block.rotate(i*.5, z=1, parent=block)
					yield

				self['children'] = [c for c in self['children'] if c is not block]
				self.__snap_data__['timers'] = [t for t in self.__snap_data__['timers'] if t is not timer]

			timer.start(anim(), seconds=0, repeat=True)

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			text = GFX.Text('hello world!  click with the mouse...') # TODO demonstrate everything that can be done with text rendering

			self.set(items=[text])

			# TODO add graphics to demonstrate all basic rendering (and hook into animation system to test it out too...)

			# create a container for each renderable example

			# also do a batch render as a series of context commands queued directly into a shader...

			# also render something directly in a draw method

			self['extents'] = ENV.snap_extents_t(0,0,0, 640,480,0) # TODO assign extents of gui window when toplevel

			self.animated_block_at(self['width']/2, self['height']/2)

			# TODO ENGINE = ENV.GFX

			# TODO show off interaction and animation systems too

	return SnapGraphicsDemo

	# TODO init EngineTest and assign to GUI, and start gui loop if not already going?

def main(ENV):

	#ENV.graphics.load('QT5')
	ENV.__run_gui__(build(ENV))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

