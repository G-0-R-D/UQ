
import os

# just trying to make the SnapProject.py file shorter...
# this is the backend stuff the SnapProject.py will make use of to actually do useful stuff...

def build(ENV):

	SnapContainer = ENV.SnapContainer

	SnapTimer = ENV.SnapTimer

	SnapProjectTasks = ENV.SnapProjectTasks

	SnapProjectLayout = ENV.SnapProjectLayout

	class SnapProjectBase(SnapContainer):

		__slots__ = ['__tasks__']

		# TODO HUD: {'origin(declaration)':..., 'file_list':..., 'upstream':..., 'dowstream':..., 'minimap':..., 'commandline':...}
		# TODO make window_event() (or even parent_event())?  and support emit by listener...

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
							p = {'path':fullpath, 'regular_files':[], 'modules':[]}
						packages.append(p)

					self.__snap_data__['__packages__'] = packages
					self.__tasks__.refresh()
					if existing:
						changed = True
						self.__tasks__.dismiss(*existing.values())

				if changed:
					self.changed(packages=paths)

		@ENV.SnapProperty
		class layout:
			# current / active layout

			def get(self, MSG):
				"()->SnapProjectLayout"
				return self.__snap_data__['layout']

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


	ENV.SnapProjectBase = SnapProjectBase

