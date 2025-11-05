
def build(ENV):

	B = ENV.__build__

	B('snap.lib.core.datatypes.primitives.SnapPrimitive')
	B('snap.lib.core.datatypes.primitives.SnapBool')
	B('snap.lib.core.datatypes.primitives.SnapBytes')
	B('snap.lib.core.datatypes.primitives.SnapFloat')
	B('snap.lib.core.datatypes.primitives.SnapInt')
	B('snap.lib.core.datatypes.primitives.SnapString')

	B('snap.lib.core.datatypes.primitives.SnapList')
	B('snap.lib.core.datatypes.primitives.SnapDict')

	B('snap.lib.core.datatypes.primitives.snap_list_ops')

