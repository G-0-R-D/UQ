
def build(ENV):

	SnapContainer = ENV.SnapContainer

	class SnapParticleSystem(SnapContainer):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			# TODO assign particle graphics...
			# TODO control the rate, motion, etc... of the system


	ENV.SnapParticleSystem = SnapParticleSystem


