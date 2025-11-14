
def build(ENV):

	ENV.__build__('snap.programming.project.SnapProjectSettings')
	ENV.__build__('snap.programming.project.SnapProjectTasks')

	ENV.__build__('snap.programming.project.shaders')
	ENV.__build__('snap.programming.project.layouts')

	ENV.__build__('snap.programming.project.SnapProject')

