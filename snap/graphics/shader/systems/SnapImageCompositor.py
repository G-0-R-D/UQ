
def build(ENV):

	SnapContainer = ENV.SnapContainer

	class SnapImageCompositor(SnapContainer): # TODO should this even be a SnapWindow?  XXX no, we can composite to another target...

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			# TODO quickly composite a series of images and textures into a target result...

	ENV.SnapImageCompositor = SnapImageCompositor
