
def build(ENV):

	B = ENV.__build__

	B('snap.core.datatypes.primitives.SnapPrimitive')
	B('snap.core.datatypes.primitives.SnapBool')
	B('snap.core.datatypes.primitives.SnapBytes')
	B('snap.core.datatypes.primitives.SnapFloat')
	B('snap.core.datatypes.primitives.SnapInt')
	B('snap.core.datatypes.primitives.SnapString')

	B('snap.core.datatypes.primitives.SnapList')
	B('snap.core.datatypes.primitives.SnapDict')

	B('snap.core.datatypes.primitives.snap_list_ops')

