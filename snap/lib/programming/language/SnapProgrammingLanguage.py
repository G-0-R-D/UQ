
import os

def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapProgrammingLanguage(SnapNode):

		__slots__ = []

		# TODO file info on project, so we can decode a file with **info generally?  or make a decode_file using a filepath?  and the c project can find the includes from the project or externals when it does this?

		__EXTENSIONS__ = None # assigned in subclass, list of extensions (lowercase)

		"""
		@ENV.SnapProperty
		class rootpath:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['rootpath']

			def set(self, MSG):
				"(str!)"
				rootpath = MSG.args[0]
				if rootpath is not None:
					assert os.path.isdir(rootpath), 'not a package directory: {}'.format(repr(rootpath))
					self.analyze(rootpath)
				self.changed(rootpath=rootpath)
		"""

		def get_extension(self, FILEPATH):
			filename = os.path.basename(FILEPATH)
			split = filename.split('.')
			if len(split) > 1:
				return split[-1]
			return None

		def uses_extension(self, EXT):
			return EXT in self.__EXTENSIONS__ if self.__EXTENSIONS__ else None

		def is_module(self, FILEPATH):
			return self.uses_extension(self.get_extension(FILEPATH))


		def list_modulesXXX(self, *ROOTS):
			modules = []
			for root in ROOTS:
				if os.path.isfile(root):
					modules.append(root)
				elif os.path.isdir(root):
					for r,s,f in os.walk(root):
						for fname in files:
							if self.uses_extension(fname.split('.')[-1]):
								modules.append(os.path.join(r,fname))
				else:
					ENV.snap_warning('invalid path:', repr(root))
			return modules

		def analyzeXXX(self, *ROOTS):
			'build a dict report of the modules in all of the paths, and their dependencies between eachother, both what they access from others and export to others'

			modules = self.list_modules(*ROOTS)

			print('found', modules)

			# get the info for each module # TODO c might require knowing the roots for the include file locations... TODO pass full info for module_info to fill in?
			# figure out the resolution of modules, and valid starting points
			#	-- report missing or invalid stuff too...

			# TODO missing modules (something is imported but not found)

		def get_module_info(self, FILEPATH, *ALL_FILES):

			# will match all viable dependencies if there are more than one...

			if not self.is_module(FILEPATH):
				return None

			# TODO implement a general decode() handling, where we find import and import_from, and other structures of interest...
			# generalized
			
			# TODO parse with ast, and figure out the accesses from other modules and exports from this module, full resolution from top to bottom with type and name for each component in the tree...
			# TODO just get the ast, the QUEUE walk it with full rootpath, and figure out what is externally visible and what is accessed from elsewhere...

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

	ENV.SnapProgrammingLanguage = SnapProgrammingLanguage

