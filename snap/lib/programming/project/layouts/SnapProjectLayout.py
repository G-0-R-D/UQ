
from weakref import ref as weakref_ref

def build(ENV):

	SnapContainer = ENV.SnapContainer
	SnapProjectTasks = ENV.SnapProjectTasks

	SnapProjectLayoutFile = ENV.SnapProjectLayoutFile

	class SnapProjectLayout(SnapContainer):

		__slots__ = ['__project__', '__tasks__']

		task_decorator = SnapProjectTasks.task_decorator

		@task_decorator
		def update(self, PROJECT, TIMER, from_layout=None):

			if from_layout:
				'animate previous positions to new positions'
				# if from layout then we save the current positions, set immediately to existing layout config, and then animate to the original positions...

			'update the rest'


			graphics = []

			x_offset = 0
			for package in PROJECT.__snap_data__['__packages__'] or []:
				for file in package['files']:
					ENV.snap_debug('add file to scene', file['filepath'])
					#d = SnapProjectLayoutFile(self, module)
					#graphics.append(d)
					#d['matrix'] = ENV.snap_matrix_t(1,0,0,x_offset, 0,1,0,0, 0,0,1,0, 0,0,0,1)
					#x_offset += d['width'] + 100
					#ENV.snap_out("step", d['width'], x_offset)

			ENV.snap_out('modules added')

			#PROJECT['children'] = graphics

			yield

		@task_decorator
		def animate(self, PROJECT, TIMER):

			TIMER['fps'] = 30

			found_animated = False
			while 1:
				for node in self['children'] or []:
					'if node still animating, call node.next()'
					break # TODO if node['animating']: found_animated = True

				if not found_animated:
					break

				yield

		@task_decorator
		def file_changed(self, PROJECT, TIMER, FILE):
			'check if file is registered'
			'update file display, and those affected by it...'

			

			# determine all new positions, then animate to them (here) -- use animation system...
			self.update()
			yield

		@task_decorator
		def register_file(self, PROJECT, TIMER, FILE):

			registry = self.__snap_data__['__registry__'] = self.__snap_data__.get('__registry__', {})
			node = registry.get(FILE['filepath'])
			if not node:
				node = register[FILE['filepath']] = SnapProjectLayoutFile(FILE)
				self.file_changed(FILE)

			# TODO we calculate new positions, assign them to the graphic, and then queue animation which calls next() on each of them until nothing left to animate
			yield

		@task_decorator
		def dismiss(self, PROJECT, TIMER, *DISMISS):
			''

			yield

		def cancel(self):
			'stop loading, set all animations to their final positions'


# / tasks ############################################################

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

			#self.update()


	ENV.SnapProjectLayout = SnapProjectLayout
