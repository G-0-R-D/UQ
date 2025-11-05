
from weakref import ref as weakref_ref

def build(ENV):

	SnapTimer = ENV.SnapTimer

	def task_decorator(FUNC):
		timer = SnapTimer(None)
		def wrapper(self, *a, **k):
			gen = FUNC(self, self.__project__(), timer, *a, **k)
			self.__tasks__[FUNC.__name__] = timer
			timer.start(gen, fps=100, repeat=True)
			return timer#FUNC(self, PROJECT, TIMER)
		return wrapper

	class SnapProjectTasks(object):

		__slots__ = ['__project__', '__tasks__']

		@task_decorator
		def open(self, PROJECT, TIMER):
			# run when packages change, make sure the file structure is loaded (just the basic dict and filepath info)
			# TODO store a list of language files too, check what language supports their extension?

			# we need:
			# filepath
			# os.stat
			# ENV.LANGUAGE for the modules if their ext is a language type

			# start with list of packages, and load the info into the packages
			project = self['project']

			for package in PROJECT.__snap_data__['__packages__'] or []:
				path = package['path']
				
				# TODO also initialize display?  load shaders, assign them to dict, have shaders for each of the file states...
				# TODO do lookup result as the dict, in the shader...

				yield

			# TODO cleanup

		def __init__(self, PROJECT):

			assert PROJECT is not None
			self.__project__ = weakref_ref(PROJECT)
			self.__tasks__ = {
				#'name':SnapTimer,
			}


	return SnapProjectTasks

