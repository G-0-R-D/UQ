
from weakref import ref as weakref_ref

def build(ENV):

	SnapContainer = ENV.SnapContainer
	SnapProjectTasks = ENV.SnapProjectTasks

	class SnapProjectLayout(SnapContainer):

		__slots__ = ['__project__', '__tasks__']

		task_decorator = SnapProjectTasks.task_decorator

		@task_decorator
		def update(self, PROJECT, TIMER, from_layout=None):

			if from_layout:
				'animate previous positions to new positions'

			'update the rest'

			yield

		@task_decorator
		def dismiss(self, PROJECT, TIMER, *DISMISS):
			''

			yield

		def cancel(self):
			'stop loading, set all animations to their final positions'


# / tasks ############################################################

		@ENV.SnapProperty
		class modules:

			# NOTE: this is the interface for project modules, but internally they are wrapped so that
			# layout specific render and config can be stored...

			def get(self, MSG):
				"()->dict[]"
				return [m['__src__'] for m in (self.__snap_data__['modules'] or [])]

			#def set(self, MSG):
			#	"(dict[])"
			#	# TODO find existing wrapper, XXX don't make this settable, layout should internally create the modules it needs from the project...
			set = None
 

		@ENV.SnapProperty
		class render_items:

			def get(self, MSG):
				"()->SnapProjectFileShader[]"
				# TODO [m['shader'] for m in self.__project__()['modules'] if 'shader' in m] XXX will have local copies of modules that are renderable...
				return []

		def __init__(self, PROJECT, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			assert PROJECT is not None
			self.__project__ = weakref_ref(PROJECT)
			self.__tasks__ = {
				#'name':[SnapTimer, ...], ...
			}

			self.update()


	ENV.SnapProjectLayout = SnapProjectLayout
