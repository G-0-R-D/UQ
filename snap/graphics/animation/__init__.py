
# animation is done by registering next time callback in global timeline?  so we calculate the display time and then set it for callback at that time in ANIMATION, so we can support multiple framerates and lots of callbacks efficiently...

def build(ENV):

	ENV.__build__('snap.graphics.animation.SnapAnimationChannel')

	class SnapAnimationModule(object):

		__slots__ = []

		def animate(self, NODE, TARGET_MATRIX, interpolation=None):
			'' # TODO create an animation for node, register with timers, default to linear interpolation, return the animation node (if the reference is lost then animation jumps to completed position)

		def __init__(self):

			'' # TODO


	ENV.ANIMATION = SnapAnimationModule()


def main(ENV):

	SnapContainer = ENV.SnapContainer

	class SnapAnimationTest(SnapContainer):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			'' # TODO do an animation test with gui and scubbable timeline...

	ENV.__run_gui__(SnapAnimationTest)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())
