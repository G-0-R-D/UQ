
import os,json

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	#SnapProjectFile = ENV.SnapProjectFile
	SnapProjectSettings = ENV.SnapProjectSettings
	SnapProjectLayout = ENV.SnapProjectLayout

	SnapProjectTasks = ENV.SnapProjectTasks

	# TODO can run headless
	GFX = getattr(ENV, 'GRAPHICS', None)

	if GFX is not None:
		'build shaders...'


	# decorator
	def task(FUNC, *args, **kwargs):
		'register'
		# TODO wrapper gets assigned to the timer, and assigned to self...
		# then wrapper does the iteration (or just a call if not an iterator)
		# and wrapper cleans up after (remove from local assign from FUNC.__name__)
		#	-- assign to self.__snap_data__['__tasks__'] on whatever self is (a SnapNode type)
		#	-- TODO and use methods to define the tasks, decorate them with this
		#	-- TODO maybe make a task manager decorator that assigns to an instance in data['__task_manager__']? XXX this is the task manager, just assign the tasks to a dict from here
		def wrapper(self, *a, **k):
			timer = SnapTimer(None)
			gen = FUNC(self, self.__project__(), timer, *a, **k)
			existing = [t for t in self.__tasks__.get(FUNC.__name__, []) if t['running']] # housekeeping
			self.__tasks__[FUNC.__name__] = existing + [timer]
			timer.start(gen, seconds=0, repeat=True)
			return timer#FUNC(self, PROJECT, TIMER)
		return wrapper


	class SnapProject(SnapContainer):

		__slots__ = ['__tasks__']

		@ENV.SnapProperty
		class packages:

			def get(self, MSG):
				"()->str[]"
				return tuple(p['path'] for p in self.__snap_data__['__packages__'] or [])

			def set(self, MSG):
				"(str[])"
				paths = MSG.args[0]
				changed = False
				if paths is None:
					if self.__snap_data__['__packages__']:
						changed = True
					del self.__snap_data__['__packages__']
				else:

					assert all([isinstance(s, str) for s in paths]), 'packages must be strings'

					existing = {p['path']:p for p in (self.__snap_data__['__packages__'] or [])}

					packages = []

					for path in paths:
						fullpath = os.path.realpath(path)
						try:
							p = existing.pop(fullpath)
						except:
							changed = True
							p = {'path':fullpath, 'files':[]}
						packages.append(p)

					self.__snap_data__['__packages__'] = packages
					self.__tasks__.refresh()
					if existing:
						changed = True
						self.__tasks__.dismiss(*existing.values())

				if changed:
					self.changed(packages=paths)

		@ENV.SnapProperty
		class modules:

			def get(self, MSG):
				"()->dict[]"
				return [m['filepath'] for p in (self.__snap_data__['__packages__'] or []) for m in p['files'] if 'module_info' in m]

			set = None

		@ENV.SnapProperty
		class layout:
			# current / active layout

			def get(self, MSG):
				"()->SnapProjectLayout"
				layout = self.__snap_data__['layout']
				if layout is None:
					layout = self.__snap_data__['layout'] = SnapProjectLayout(self)
				return layout

			def set(self, MSG):
				"(SnapProjectLayout!)"
				layout = MSG.args[0]
				if layout is None:
					layout = SnapProjectLayout(self) # default, must always have a layout to display!

				assert isinstance(layout, SnapProjectLayout)

				previous = self.__snap_data__['layout']
				self.__snap_data__['layout'] = layout
				layout.update(from_layout=previous)
				self.changed(layout=layout)

		@ENV.SnapProperty
		class layouts:

			def get(self, MSG):
				"()->SnapProjectLayout[]"
				return self.__snap_data__['layouts'] or []

			def set(self, MSG):
				"(SnapProjectLayout[])"
				layouts = MSG.args[0]
				if layouts is not None:
					assert isinstance(layouts, (list, tuple))
					layouts = list(layouts)
				self.__snap_data__['layouts'] = layouts
				self.changed(layouts=layouts)

		@ENV.SnapProperty
		class settings:

			def get(self, MSG):
				"()->SnapProjectSettings"
				s = self.__snap_data__['settings']
				if not s:
					s = self.__snap_data__['settings'] = SnapProjectSettings()
				return s
		

		@ENV.SnapProperty
		class HUD:

			# TODO HUD: {'origin(declaration)':..., 'file_list':..., 'upstream':..., 'dowstream':..., 'minimap':..., 'commandline':...}
			# TODO make window_event() (or even parent_event())?  and support emit by listener...

			def get(self, MSG):
				"()->SnapContainer"
				# TODO

			def set(self, MSG):
				"(SnapContainer!)"
				# TODO


		@ENV.SnapProperty
		class children:

			def get(self, MSG):
				return [self['layout']]

			set = None


		@ENV.SnapProperty
		class build_targets:
			# this is for compilation, you can create a series of output configurations for your project
			# like different operating systems, and different settings like debug... etc...

			# TODO add build targets as dicts of configuration options to compile to...
			#	-- make a SnapProjectBuildTarget() node to contain and edit easily...

			def get(self, MSG):
				"()->list(*SnapProjectBuildTarget)"
				raise NotImplementedError()

			def set(self, MSG):
				"(SnapProjectBuildTarget | list(*SnapProjectBuildTarget))"
				raise NotImplementedError()

		@build_targets.alias
		class compile_targets: pass

		@ENV.SnapChannel
		def compile(self, MSG):
			"()"
			build_targets = self['build_targets']
			assert build_targets, 'no build targets to compile'

			# TODO 
			raise NotImplementedError('compile')


		@ENV.SnapChannel
		def close(self, MSG):
			""
			# TODO

		@ENV.SnapChannel
		def open(self, MSG):
			"(str savefile!)"

			# TODO 

		@open.alias
		def load(self, MSG): pass


		@ENV.SnapChannel
		def save(self, MSG):
			''
			# save json info as project working file
			raise NotImplementedError()

		@ENV.SnapChannel
		def parent_event(self, MSG):
			"()"
			action = MSG.unpack('action', None)
			ENV.snap_out('action', action)


		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			# XXX process exists new/delete status in one pass upon package change...
			#	-- to delete we just flag it as deleted, play an animation, and then remove it...

			modules = self.__snap_data__['modules'] or []
			if not modules:
				modules = self.__snap_data__['modules'] = [{'filepath':f, 'stat':os.stat(f)} for f in self['files']]

			# TODO:
			"""
			module = {
				'filepath':str(),
				'dependencies':[...], # list of files that this one references?
				'structure':{...}, # language analysis...
				'render':{...}, 
				'stat':os.stat,
			}
			"""

			for module in modules:
				print('process', module)

				if 'no longer exists':
					'delete'
					continue # TODO or yield?

				stat = os.stat(module['filepath'])
				if 'stat' not in module or stat.st_size != module['stat'].st_size or stat.st_mtime != module['stat'].st_mtime:
					# reload module from scratch
					filepath = module['filepath']
					module.clear()
					module['filepath'] = filepath
					module['stat'] = stat
					yield

				# TODO just yield the module and caller can then continue processing it...  pipeline!

				
				'get info from language, if not language type then language:None to indicate it has been processed'

			#for filepath in self['files']:
			#	print(filepath)

			#print('update', info['packages'])
			#for mod in info['modules']:
			#	print(mod)


		@ENV.SnapChannel
		def changed(self, MSG):
			#ENV.TASKS.callback(self.update)
			#if 'packages' in MSG.kwargs:
			#	self.update()
			return SnapContainer.changed(self, MSG)
			

		def __init__(self, **SETTINGS):

			self.__tasks__ = SnapProjectTasks(self)

			SnapContainer.__init__(self, **SETTINGS)



	ENV.SnapProject = SnapProject
	return SnapProject

def main(ENV):
	ENV.__run_gui__(ENV.SnapProject, packages=["../../../demo/snap/programming/hello_world/project/"])

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())



