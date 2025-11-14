
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapAnimationMatrix(SnapNode):

		__slots__ = []

		# TODO rotation x,y,z, scale x,y,z, location x,y,z, euler/quaternion...  also x,y,z rotation orders...
		# TODO maybe assign attrs to rotation,scale,location, and then assign the properties there?  which re-directs to the matrix here?  or the local data is disassembled, so we can change the channels individually...  and then turn it back into matrix with the scale * rotate * translate formula or whatever it is...

		def __init__(self, target=None, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			# TODO target is SnapMatrix instance to be animated (as this changes it will forward the changes to the target)
			# this class just breaks the matrix representation down into individual channels and formats for animation (which is expensive!  so we don't use it unless we want it!)
			#	-- TODO you could also drive a matrix animation by just connecting an animation channel for a matrix type to a channel or property that accepts a matrix as it's input type...


	ENV.SnapAnimationMatrix = SnapAnimationMatrix
