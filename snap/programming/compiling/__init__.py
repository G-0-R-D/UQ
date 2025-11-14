
def build(ENV):

	ENV.__build__('snap.programming.compiling.SnapInternalCompilerPreprocess')
	ENV.__build__('snap.programming.compiling.SnapInternalCompilerEncode')
	ENV.__build__('snap.programming.compiling.SnapInternalCompiler')


