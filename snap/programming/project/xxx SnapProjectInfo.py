
import os

def build(ENV):

	SnapContainer = ENV.SnapContainer

	class SnapProjectInfo(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class packages:

			def get(self, MSG):
				"()->list(str)"
				return self.__snap_data__['packages'] or []

			def set(self, MSG):
				"(list(str))"
				packages = MSG.args[0]
				if packages is not None:
					packages = [os.path.realpath(p) for p in packages]
					for p in packages:
						assert os.path.exists(p), 'invalid path: {}'.format(repr(p))
				self.__snap_data__['packages'] = packages

				existing = self.__snap_data__['modules']
				if existing:
					''
				del self.__snap_data__['modules'] # TODO could do a more refined difference check cause this could have been a lot of processing on large projects!  just clear the filepaths that are different?
				# TODO we should store the stat time and size and use that for difference checks too...

				# TODO we need to remove missing, add new, and also remove the info for any module that was referencing what was removed...  (if it imported a now missing module that info needs to be cleared)
				self.changed(packages=packages)

		@ENV.SnapProperty
		class files:

			def get(self, MSG):
				"()->list[](str)"
				files = []
				packages = self['packages'] or []

				for root in packages:
					if os.path.isfile(root):
						files.append(root)
					elif os.path.isdir(root):
						for r,s,f in os.walk(root):
							for fname in f:
								files.append(os.path.join(r,fname))
					else:
						ENV.snap_debug('invalid package path:', repr(root))

				return files

			set = None

		@ENV.SnapProperty
		class modules:

			# dicts of info about each module, including graphic info and any other information
			# update() will process this list one at a time

			def get(self, MSG):
				"()-list(*dict)"
				# NOTE: these will be maintained in draw order...
				return self.__snap_data__['modules'] or []

			set = None # assigned in update call if there are none but there are files

		@ENV.SnapProperty
		class languages:

			def get(self, MSG):
				"()->list(*str)"
				return list(set([m['language']['name'] for m in self['modules'] if 'language' in m]))

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
			ENV.TASKS.callback(self.update)
			return SnapContainer.changed(self, MSG)

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

	ENV.SnapProjectInfo = SnapProjectInfo
