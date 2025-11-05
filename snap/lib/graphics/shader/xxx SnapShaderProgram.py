
# XXX NOTE: this works, but I'm ditching it atleast for now because it's overkill!  the new shader design is based on an assignable shader which can be swapped, so changing the shader program isn't necessary (and all of the security issues and performance issues that go with it!)

from weakref import ref as weakref_ref

# dir(globals()['__builtins__'])
builtins = """
ArithmeticError --
AssertionError --
AttributeError --
BaseException --
BaseExceptionGroup --
BlockingIOError --
BrokenPipeError --
BufferError --
BytesWarning --
ChildProcessError --
ConnectionAbortedError --
ConnectionError --
ConnectionRefusedError --
ConnectionResetError --
DeprecationWarning --
EOFError --
Ellipsis --
EncodingWarning --
EnvironmentError --
Exception ?
ExceptionGroup --
False +
FileExistsError --
FileNotFoundError --
FloatingPointError --
FutureWarning --
GeneratorExit --
IOError --
ImportError --
ImportWarning --
IndentationError --
IndexError --
InterruptedError --
IsADirectoryError --
KeyError --
KeyboardInterrupt --
LookupError --
MemoryError --
ModuleNotFoundError --
NameError --
None +
NotADirectoryError --
NotImplemented --
NotImplementedError --
OSError --
OverflowError --
PendingDeprecationWarning --
PermissionError --
ProcessLookupError --
RecursionError --
ReferenceError --
ResourceWarning --
RuntimeError --
RuntimeWarning --
StopAsyncIteration --
StopIteration ?
SyntaxError --
SyntaxWarning --
SystemError --
SystemExit --
TabError --
TimeoutError --
True +
TypeError --
UnboundLocalError --
UnicodeDecodeError --
UnicodeEncodeError --
UnicodeError --
UnicodeTranslateError --
UnicodeWarning --
UserWarning --
ValueError --
Warning --
ZeroDivisionError --
_ --
__build_class__ --
__debug__ --
__doc__ --
__import__ --
__loader__ --
__name__ --
__package__ --
__spec__ --
abs +
aiter --
all +
anext --
any +
ascii +
bin +
bool +
breakpoint --
bytearray +
bytes +
callable --
chr +
classmethod --
compile --
complex --
copyright --
credits --
delattr ?
dict +
dir --
divmod +
enumerate +
eval --
exec --
exit --
filter +
float +
format --
frozenset --
getattr +
globals --
hasattr +
hash --
help --
hex +
id +
input --
int + 
isinstance +
issubclass +
iter +
len +
license --
list +
locals --
map +
max +
memoryview --
min +
next +
object +
oct +
open --
ord +
pow +
print +
property +
quit --
range +
repr +
reversed +
round +
set +
setattr +
slice +
sorted +
staticmethod +
str +
sum +
super +
tuple +
type +
vars --
zip +
"""
acceptable = []
for l in builtins.split('\n'):
	l = l.strip(' \t')
	if not l or l.startswith('#'):
		continue
	word,symbol = l.split(' ')
	if symbol not in ('+','?'):
		continue
	acceptable.append(word)
	
#acceptable = [l.rstrip(' +?') for l in builtins.split('\n') if l and not l.startswith('#') and l.strip(' \t')[-1] in ('+','?')]
#print(acceptable)

names = [l.split(' ')[0] for l in builtins.split('\n') if l and not l.startswith('#')]
missing = [attr for attr in dir(globals()['__builtins__']) if attr not in names]
if missing:
	''#ENV.snap_warning('missing builtins? {}'.format(missing))

ACCEPTED_BUILTINS = set(acceptable)

ACCEPTED_ENV = set() # TODO snap_matrix_t, extents, etc...

def build(ENV):

	SnapNode = ENV.SnapNode
	SnapBoundProperty = ENV.SnapBoundProperty

	def SnapShader_compile(self, STRING):

		assert isinstance(STRING, str), 'source code must be a str!'

		#g = {'__builtins__':self}
		#b = globals()['__builtins__']
		#g.update({attr:getattr(b, attr) for attr in accepted})

		# TODO ignore newlines in strings or comments...?  do we need to?
		INDENTED = '\n'.join(['\t' + l for l in STRING.split('\n')])

		# TODO replace spaces with tabs?

		COMPILE = 'def usercode(CTX):\n' + INDENTED + '\n\treturn None'

		g = {'__builtins__':self}
		exec(COMPILE, g)

		return g['usercode']
	
	ENV.SnapShader_compile = SnapShader_compile

	class SnapShader(SnapNode):

		# NOTE: object creation is not supported, if an intermediate object is required for a calculation, then make a property for it!

		__slots__ = []

		# NOTE: because these internal properties don't implement get(), they can't be accessed from inside the shader!

		@ENV.SnapProperty
		class __draw_code__:

			#def get(self, MSG):
			#	"()->str"
			#	return self.__snap_data__['__source_code__']

			def set(self, MSG):
				"(str!)"
				STRING = MSG.args[0]

				if STRING is not None:
					self.__snap_data__['__draw_executable__'] = SnapShader_compile(self, STRING)
				else:
					self.__snap_data__['__draw_executable__'] = None

				self.changed(__draw_code__=STRING)


		@ENV.SnapProperty
		class __lookup_code__:

			def set(self, MSG):
				"(str!)"
				STRING = MSG.args[0]
				if STRING is not None:
					self.__snap_data__['__lookup_executable__'] = SnapShader_compile(self, STRING)
				else:
					self.__snap_data__['__lookup_executable__'] = None

				self.changed(__lookup_code__=STRING)

		# NOTE: technically the executable is just a function that accepts a SnapContext as a single positional argument...
		@ENV.SnapProperty
		class __draw_executable__:
			pass

		@ENV.SnapProperty
		class __lookup_executable__:
			pass


		@ENV.SnapChannel
		def update(self, MSG):
			"(SnapNode?)"
			# use this to update variables outside of render code, pass in a target if the shader needs to reference it
			# typically SnapContainer.changed() will forward to SnapContainer['shader'].update(self)
			pass


		def draw(self, CTX):
			# NOTE: shader code can be placed here (or even in the draw call of the container) if it is not assignable
			try:
				return self.__snap_data__['__draw_executable__'](CTX)
			except Exception as e:
				ENV.snap_warning(repr(e))

		def lookup(self, CTX):
			try:
				return self.__snap_data__['__lookup_executable__'](CTX)
			except Exception as e:
				ENV.snap_warning(repr(e))




		def __getitem__(self, KEY):

			# NOTE: this will make it seem like the shader program has properties for any builtin name (like 'print')

			if isinstance(getattr(self, KEY, None), SnapBoundProperty):
				return SnapNode.__getitem__(self, KEY)

			# TODO 
			#try:
			#	return SnapNode.__getitem__(self, KEY)
			#except KeyError:
			#	pass

			if KEY in ACCEPTED_BUILTINS:
				#return getattr(globals()['__builtins__'], KEY)
				return globals()['__builtins__'][KEY]

			elif KEY in ACCEPTED_ENV:
				return getattr(ENV, KEY)

			raise NameError(KEY, '(if name exists it is not allowed in a shader program)')


		# TODO put draw and lookup on here?  makes it easier to organize, lookup would probably use same 'shape' for example as render!  or atleast use a shape that is based on what the draw is doing!
				
		def __init__(self, DRAW_STR, LOOKUP_STR, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if DRAW_STR is not None:
				self['__draw_code__'] = DRAW_STR
			if LOOKUP_STR is not None:
				self['__lookup_code__'] = LOOKUP_STR

	ENV.SnapShader = SnapShader



def main(ENV):

	CODE = [
		"apple = 1",
		"print('apple is', apple)",
		"print('context is', CTX)",
		#"print('hello world')",
	]

	p = ENV.SnapShader('\n'.join(CODE), None)

	p.draw(None)


