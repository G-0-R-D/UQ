
import re

def build(ENV):

	ENV.__build__('snap.lib.programming.language.c.SnapCLanguageDecoder')

	SnapProgrammingLanguage = ENV.SnapProgrammingLanguage

	class SnapCLanguage(SnapProgrammingLanguage):
		# NOTE: this will provide c and cpp, via clang (as in 'a "c" language')

		# TODO ideas introducted by c:
		"""
		casting (just wrap the new type, like int(char()) ?  error if the type can't initialize from the other?  or we could make a cast(to, from) that can re-interpret the data without bias...  -- literally just a __bytes__ & __size__ transfer from the SnapObject struct...)
		strict typing (verify args from message with isinstance() or type()?)
		"""

		__slots__ = []

		LANGUAGE_NAME = 'C'

		def get_module_info(self, FILEPATH, PROJECT):
			'' # TODO

			# TODO list modules as single-name paths relative to project paths...

			# TODO verify extension is ours... c/h/cpp/hpp?

			include_pattern = re.compile(r'#\s*include\s*[\<\"]([^\<\"]+)')
			with open(FILEPATH, 'r') as openfile:
				for line in openfile:
					line = line.strip('\n\t ')
					match = include_pattern.match(line)
					if match:
						name = match.group(1)
						print('found include', name)

		def decode(self, *a, **k):
			return ENV.SnapCLanguageDecoder().decode(*a, **k)



	ENV.SnapCLanguage = SnapCLanguage
	#ENV.LANGUAGE.c = SnapCLanguage
	return SnapCLanguage()

def main(ENV):

	import json, os

	THISDIR = os.path.realpath(os.path.dirname(__file__))

	c = ENV.LANGUAGE.c
	#with open(__file__, 'r') as openfile:
	settings = dict(generalized=True, with_line_info=True)

	EXAMPLE = """
int main(void){
	int a = 1;
}
	"""

	if 0:
		with open(os.path.join(THISDIR, 'test/everything.c'), 'r') as openfile:
			EXAMPLE = openfile.read()

	j = c.decode(EXAMPLE, **settings)

	print(json.dumps(j, indent=4))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


