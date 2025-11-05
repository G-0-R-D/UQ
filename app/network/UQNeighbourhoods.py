
def build(ENV):

	SnapNode = ENV.SnapNode

	class UQNeighbourhoods(SnapNode):

		__slots__ = []

		# TODO connect with other UQ sessions / devices, and communities (based on torrent files)

	ENV.UQNeighbourhoods = UQNeighbourhoods

	# TODO ENV.NETWORK = own() which wraps the existing ENV.NETWORK for non-neighbourhood requests...

