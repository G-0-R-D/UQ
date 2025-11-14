
import os
THISDIR = os.path.realpath(os.path.dirname(__file__))

def build(ENV):

	'' # TODO make a module instance and build and assign each language that is available (as regular object attr)

	# we want ENV.parsing.language.x.encode()|decode() syntax
	#	-- ENV.LANGUAGE.x.encode|decode()

	ENV.__build__('snap.programming.language.SnapProgrammingLanguage')
	ENV.__build__('snap.programming.language.SnapProgrammingLanguageCompiler')
	ENV.__build__('snap.programming.language.SnapProgrammingLanguageDecoder')
	#ENV.__build__('snap.programming.language.SnapProgrammingLanguageProject')

	LANGUAGES = {}

	for name in os.listdir(THISDIR):
		fullpath = os.path.join(THISDIR, name)
		if not os.path.isdir(fullpath): continue
		if not os.path.exists(os.path.join(fullpath, '__init__.py')): continue

		try:
			LANGUAGES[name] = ENV.__build__('snap.programming.language.' + name)
		except Exception as e:
			ENV.snap_debug('no', name)

	class SnapLanguageModule(object):

		@property
		def languages(self):
			return list(LANGUAGES.values())

		#def __getattr__(self, ATTR):
		#	lang = ENV.__build__('snap.lib.programming.language.' + ATTR)
		#	assert lang is not None, 'unable to build language: {}'.format(repr(ATTR))
		#	assert isinstance(lang, type), 'must provide type of language'
		#	setattr(self, ATTR, lang)
		#	return lang

		def get_by_extension(self, EXT):

			for lang in self.languages:
				try:
					if lang.uses_extension(EXT):
						return lang
				except:
					pass

			return None

		def __init__(self):

			for name,lang in LANGUAGES.items():
				setattr(self, name, lang)

		# TODO we don't need lazy loading, just build each language into the ENV, and then store them here for lookup

			# TODO validate the languages?

	ENV.LANGUAGE = SnapLanguageModule()

def main(ENV):

	import json

	with open(__file__, 'r') as openfile:
		print(json.dumps(ENV.LANGUAGE.python.decode(openfile.read()), indent=4))



