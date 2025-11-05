
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapProgrammingLanguageAnalyzer(SnapNode):
		# XXX just put this back onto language: analyze(*roots) and module_info(path)

		__slots__ = []

		@ENV.SnapProperty
		class language:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['language'] or '<UNKNOWN>'

		@ENV.SnapProperty
		class roots:

			def get(self, MSG):
				"()->list[](str)"
				return self.__snap_data__['roots'] or []

			def set(self, MSG):
				"(list[](str))"
				# TODO only analyze the new roots, add them in, can call refresh() to call again? (just assign roots to none and then back to roots)
				assign_roots = MSG.args[0]
				if assign_roots is None:
					del self.__snap_data__['roots']
				else:
					assert isinstance(assign_roots, (list, tuple)), 'roots must be assigned as a list or tuple of path strings'
					self.__snap_data__['roots'] = [os.path.realpath(r) for r in assign_roots]

				self.refresh()

				self.changed(roots=True)
				

		@ENV.SnapChannel
		def refresh(self, MSG):
			"()"

			all_modules = {} # {root:[module, ...]} # so we can know the bias when resolving imports?  store modules as path segment

			for root in self['roots']:
				modules = all_modules[root] = []

				if os.path.isfile(root):
					modules.append(root)
				elif os.path.isdir(root):
					for r,s,f in os.walk(root):
						for fname in files:
							if self.uses_extension(fname.split('.')[-1]):
								seg = os.path.join(r,fname)[len(root):].strip(os.sep)
								modules.append(seg)
				else:
					ENV.snap_warning('invalid path:', repr(root))


			# - get list of all the modules for this language found in the rootpaths
			# - find the imports for each module and create graph of dependencies (list module:[import, import, ...]
			#	-- figure out the imports and the names from each import...
			# - resolve the names and note any missing

			# TODO basically we just need import and names (+ type?) list for each module so we can navigate the dependencies...
			


		@ENV.SnapChannel
		def module_info(self, MSG):
			"(str filepath!)"

			info = {
				'type':'module',
				'language':self['language'],
				'imports':[], # not full filepaths, just the local names, resolve externally...
					# TODO also the names accessed from other modules?  or just list the names that aren't defined in here?
				'unresolved_names':[], # TODO resolved_names, which modules reference this one?  store all possibilities let user resolve conflicts?
				'function_declarations':[], # XXX these three are just list of type and name for everything that leads in or out of the module... (accesses from others, exports to others) -- full hierarchy?
				'class_declarations':[],
				# TODO vars that are globally visible?
			}

			path = MSG.args[0]
			assert os.path.isfile(path), 'not a filepath: {}'.format(path)
			ext = os.path.basename(path).split('.')[-1]
			if not self.uses_extension(ext):
				return None

			# TODO use ast parser generalized parse to answer the above info
			#	-- actually, c probably wouldn't use the parser for this, atleast not until the includes are resolved...

			# TODO break this down into further steps?  make analyzer it's own class?  so it can maintain state and track what it needs to know for queries?

			return info


		@ENV.SnapChannel
		def analyze(self, MSG):
			"()"

			info = {
				'type':'analysis',
				'language':self['language'],
				'roots':[],
				'modules':[],

				# imports -> do 'filepath':['imported_module_filepath', ...]
			}

			for path in MSG.args:
				path = os.path.realpath(path)
				info['roots'].append(path) # keep track of it even if it is invalid, always validate before crawling
				if os.path.isfile(path):
					if self.uses_extension(os.path.basename(path).split('.')[-1]):
						info['modules'].append(path)
				elif os.path.isdir(path):
					for root,subs,files in os.walk(path):
						for fname in files:
							if self.uses_extension(fname.split('.')[-1]):
								info['modules'].append(os.path.join(root, fname))
				else:
					ENV.snap_warning('not a valid path', repr(path))
					continue

			# TODO create and return new api representing analysis?

			# TODO basically open

			# walk and find all relevant files...
			# find the import structure of those files...

			# return as dict? XXX keep locally so we can then ask the language more questions like roots or things like that?  or just make sure all the necessary information is returned?
			# imports (as trees?), per-module info for names defined, and their types?  interface info...

			# TODO and then the build analyze() would give us the info on how to piece things together?
			return info


		def module_info(self, FILEPATH):
			''

		def load(self, *ROOTS):
			''

		def __init__(self, *ROOTS, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if ROOTS:
				'kick it off'


	ENV.SnapProgrammingLanguageAnalyzer = SnapProgrammingLanguageAnalyzer
