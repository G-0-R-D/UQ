
def build(ENV):

	B = ENV.__build__
	
	#imp('snap.core.SnapWeakref')

	B('snap.core.snap_debugging')
	B('snap.core.snap_core')
	B('snap.core.util.snap_binary_search')

	if 1:
		B('snap.core.new_design.SnapMessage')
		B('snap.core.new_design.snap_lowlevel')
		B('snap.core.new_design.SnapBound')
		B('snap.core.new_design.snap_decorator')
		B('snap.core.new_design.SnapNode')
	else:
		B('snap.core.SnapMessage')
		B('snap.core.SnapBound')
		B('snap.core.snap_decorator')
		B('snap.core.SnapNode')

	B('snap.core.datatypes')

	B('snap.core.SnapTasks')
	B('snap.core.SnapTimers')
	B('snap.core.SnapTimer')


