
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


		def get_import_names(self, FILEPATH):
			if not self.is_module(FILEPATH):
				return None
			'parse the text and get the names, try to resolve them'
			# report: resolved, unresolved, multiple resolutions?
			# TODO list name, and candidate filepaths that could resolve it XXX or just return the names, let the caller resolve?
			raise NotImplementedError('implement in language subclass')

		def get_module_info(self, FILEPATH, *IMPORTS):
			# TODO IMPORTS are the paths to the imported modules (already resolved)

			if not self.is_module(FILEPATH):
				return None

			raise NotImplementedError('implement in language subclass')


		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

	ENV.SnapProgrammingLanguage = SnapProgrammingLanguage

