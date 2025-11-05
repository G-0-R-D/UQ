
import random

def build(ENV):

	SnapContainer = ENV.SnapContainer

	GFX = ENV.GRAPHICS

	def random_color():
		return GFX.Color(*[random.random() for i in range(3)] + [1.0])

	class InteractiveNode(SnapContainer):

		__slots__ = []

		def draw(self, CTX):
			CTX.cmd_fill_path(self['color'], self['rect'])
			#CTX.cmd_stroke_path(self['rect'], self['color'])

		def lookup(self, CTX):
			''#print('lookup')

		def __init__(self):
			SnapContainer.__init__(self)

			self['color'] = random_color()
			ENV.snap_out('color', self['color']['data'])
			rect = self['rect'] = GFX.Spline(description=['S',0.0,0.0, 'L',20.0,0.0, 20.0,20.0, 0.0,20.0, 'C'])
			self['direction'] = [random.random() * 3 for i in range(2)]

		

	class SnapDevicesTest(SnapContainer):

		__slots__ = []

		@ENV.SnapChannel
		def device_event(self, MSG):
			ENV.snap_out('received device_event:', MSG)

		@ENV.SnapChannel
		def allocateXXX(self, MSG):

			extents = MSG.unpack('extents', None)
			if extents:
				ENV.snap_out('realloc', extents[:])

			return SnapContainer.allocate(self, MSG)

		def draw(self, CTX):
			return SnapContainer.draw(self, CTX)

		def lookup(self, CTX):
			return SnapContainer.lookup(self, CTX)

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self)

			r = random.random
			for i in range(10):
				e = InteractiveNode()
				e.scale(r()*20,r()*20)
				#e.translate(r()*25,r()*25)#(random.random() * 30), (random.random() * 30))
				e['position'] = [r()*640, r()*480, 0]
				self['children'] += [e]

			ENV.snap_out('size', self['size'])

			ENV.snap_out(self.__class__.__name__, '__init__')

			# TODO add some graphics to the scene to test interaction


	return SnapDevicesTest

def main(ENV):

	ENV.graphics.load('QT5')

	test = build(ENV)
	ENV.__run_gui__(test)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

