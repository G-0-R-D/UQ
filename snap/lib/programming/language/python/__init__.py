
def build(ENV):

	ENV.__build__('snap.lib.programming.language.python.SnapPythonLanguageDecoder')

	SnapProgrammingLanguage = ENV.SnapProgrammingLanguage

	# TODO subclass of SnapProgrammingLanguage?

	class SnapPythonLanguage(SnapProgrammingLanguage):

		__slots__ = []

		__EXTENSIONS__ = ['py']

		@ENV.SnapProperty
		class name:

			def get(self, MSG):
				"()->str"
				return "python"


		def get_module_info(self, PROJECT, PROJECT_FILE):
			''


		#def reset(self):
		#	del self.__snap_data__['__newline_index__']
		#	return SnapProgrammingLanguage.reset(self)

		def decode(self, *a, **k):
			return ENV.SnapPythonLanguageDecoder().decode(*a, **k)

		def __init__(self):
			SnapProgrammingLanguage.__init__(self)

	ENV.SnapPythonLanguage = SnapPythonLanguage	
	#ENV.LANGUAGE.python = SnapPythonLanguage()
	return SnapPythonLanguage()

def main(ENV):

	import json, os

	THISDIR = os.path.realpath(os.path.dirname(__file__))

	py = ENV.LANGUAGE.python
	#with open(__file__, 'r') as openfile:
	settings = dict(generalized=True, with_line_info=False)

	EXAMPLE = """
a,b,c = 1,2,3
	"""

	if 0:
		with open(os.path.join(THISDIR, 'test/everything.py'), 'r') as openfile:
			EXAMPLE = openfile.read()

	j = py.decode(EXAMPLE, **settings)

	print(json.dumps(j, indent=4))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())






