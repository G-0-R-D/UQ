
def build(ENV):

	ENV.__build__('snap.lib.programming.project.SnapProjectSettings')
	ENV.__build__('snap.lib.programming.project.SnapProjectTasks')

	ENV.__build__('snap.lib.programming.project.shaders')
	ENV.__build__('snap.lib.programming.project.layouts')

	ENV.__build__('snap.lib.programming.project.SnapProject')

