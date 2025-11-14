
# ABOUT: this is my first compiler design, outputting to c functions that represent the operations.  Doesn't support asynchronous operations (no yield statements!), but it still useful for compiling back-end (internal) components, enabling the possibility of writing the components in python!  makes it easier to design and implement at the same time...

# redesigning in a way that makes subclasses 'opt-in' explicit for each encoder it wants to implement (rather than just inheriting them all), so subclasses can exclude any defaults by not mentioning them...
#	-- subclasses should inherit from base, and then attach any encoders they want (or inherit from the compiler if all encoders are wanted)

# NOTE: this uses generalized ast so any language could potentially be input for the backend...  using python for now though...

import os, re



def clean_name(NAME):
	for token in ('.','/','\\',' '): # TODO use 'is alphanumeric or underscore', else underscore
		NAME = NAME.replace(token, '_')
	return NAME


	
def walk_tree(NODE):

	#if NODE.get('__type__') != 'module':
	#	print('warning: toplevel node is not a module?', repr(NODE.get('__type__')))

	QUEUE = [[NODE]]
	while QUEUE:

		PATH = QUEUE.pop(0)
		#SRC_NODE = NODE['__src__']

		yield PATH

		NODE = PATH[-1]
		if NODE is None:
			continue

		#if 'body' in NODE and TYPE not in ('class_definition',):
		#	NODE['locals'] = {} # has own local namespace XXX this would be creating new sub ENV


		# ENQUEUE
		for attr,value in NODE.items():
			if isinstance(value, list) and all([isinstance(d, dict) and '__type__' in d for d in value]):
				QUEUE.extend([PATH + [n] for n in value])
			elif isinstance(value, dict) and '__type__' in value:
				QUEUE.append(PATH + [value])

def build(ENV):

	SnapInternalCompilerPreprocess = ENV.SnapInternalCompilerPreprocess
	SnapInternalCompilerEncode = ENV.SnapInternalCompilerEncode

	class SnapInternalCompilerBase(object):

		__slots__ = ['settings', 'imports', 'predefs']

		# TODO generic encode/preprocess api that will always be the same


		@property
		def indent_token(self):
			try:
				return self.settings['indent_token']
			except:
				return '\t'

		@property
		def is_headerfile(self):
			return self.settings.get('is_headerfile', False)



		@property
		def filepath(self):
			return self.settings.get('filepath', 'unknown')

		@property
		def basename(self):
			return os.path.basename(self.filepath)

		@property
		def module_name(self):
			return clean_name(self.basename)

		# TODO can we push the class to a stack?  get the classname of the current class as a property?
		def class_instance_name(self, CLASSNAME):
			# TODO find class in stack...
			return '__' + self.module_name + '_' + CLASSNAME

		def class_type_name(self, CLASSNAME):
			return self.class_instance_name(CLASSNAME) + 'Type'

		def class_predefined_name(self, CLASSNAME):
			return self.module_name + '_class_' + CLASSNAME

		def method_name(self, CLASSNAME, METHODNAME):
			return self.class_instance_name(CLASSNAME) + '_' + METHODNAME + '__mthd'



		def function_predefined_name(self, FUNCNAME):
			return self.module_name + '_' + FUNCNAME + '__func'

		def register_ENV_name(self, X):
			'' # TODO



		def indent(self):
			self.settings['indent_level'] += 1

		def dedent(self):
			self.settings['indent_level'] -= 1
			assert not self.settings['indent_level'] < 0, 'unmatched dedent?'

		def INDENT(self, sublevel=0):
			indent_level = self.settings.get('indent_level', 0) + sublevel
			return self.settings.get('indent_token', '\t') * indent_level




		def add_predefinition(self, N):
			TYPE = 'predefine_' + N['__type__']
			index = len([True for n in self.predefs.values() if n['__type__'] == TYPE]) + 1
			pre = {'__type__':TYPE, '__src__':N, 'index':index}

			self.predefs[id(N)] = pre

			pre['count'] = len(self.predefs) # this is to make sure we can define them in dependency order...
			return pre

		def node_preprocess(self, NODE):

			# NOTE: this is not a recursive call, maybe assert NODE['__type__'] == 'module'?

			for root in walk_tree(NODE):
				# root hasn't actually been used yet, but I thought it might be useful to know...
				N = root[-1]
				getattr(self, 'preprocess_' + N['__type__'])(root, N)

		def node_encode(self, NODE):

			# NOTE: this is a recursive call (potentially)

			for s in getattr(self, 'encode_' + NODE['__type__'])(NODE):
				yield s

		def fully_encode(self, NODE):
			return ''.join([s for s in self.node_encode(NODE)])

		def module_encodeXXX(self, NODE):
			# TODO maybe make a header encode and main encode?  include gdb and valgrind when encoding main?  or who does the actual gcc compile?
			# XXX this name is not good, it confuses the preprocess/encode structure, maybe put it somewhere else, the logic of the backend and the gcc compile
			assert NODE['__type__'] == 'module'
			yield # header guard
			# include
	
			yield # endif header guard

		def set(self, **SETTINGS):
			# TODO validate?
			self.settings.update(SETTINGS)



		def encode(self, JSON):
			# encodes the abstract ast (postprocessed) from python syntax (python_decoder.py) into a python-like c mapping (not directly c syntax)

			assert JSON['__type__'] == 'module', 'only module type supported right now...'

			self.reset()
			#wrapped = wrap_tree(JSON)
			self.node_preprocess(JSON)
			for s in self.node_encode(JSON):
				yield s


		def reset(self):

			self.settings['indent_level'] = 0
			self.imports = []
			#self.stack = []
			self.predefs = {}


		def __init__(self, **SETTINGS):

			self.settings = {
				'indent_level':0,
				'indent_token':'\t',
			}
			self.imports = [] # so we can see the list of imports after
			self.predefs = {} # {id():dict(), ...}

			if SETTINGS:
				self.set(**SETTINGS)


	ENV.SnapInternalCompilerBase = SnapInternalCompilerBase


	class SnapInternalCompiler(
		SnapInternalCompilerPreprocess,
		SnapInternalCompilerEncode,
		SnapInternalCompilerBase):

		__slots__ = []

		# piecewise could use:

		#preprocess_module = SnapInternalCompilerPreprocess.preprocess_module

		#encode_module = SnapInternalCompilerEncode.encode_module

		# but since default is to include all we'll just inherit

	ENV.SnapInternalCompiler = SnapInternalCompiler





def main(ENV):

	THISDIR = os.path.realpath(os.path.dirname(__file__))
	TESTFILE = os.path.join(os.path.dirname(THISDIR), 'include/snap/types/SnapEnv.py')

	if not getattr(ENV, 'SnapInternalCompiler', None):
		build(ENV)

	c = ENV.SnapInternalCompiler()

	with open(TESTFILE, 'r') as openfile:
		j = ENV.LANGUAGE.python.decode(openfile.read())

	c.settings['filepath'] = TESTFILE # TODO nicer...
	for text in c.encode(j):
		print(text, end='')



if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())
