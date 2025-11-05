
import os,sys,re
os_basename = os.path.basename
import inspect
import traceback

def build(ENV):

	# TODO if ENV is in separate thread it should somehow pass it's output to the parent process to log or print or whatever...

	inspect_currentframe = inspect.currentframe

	ENV.DEBUG_NONE = 0 # no output
	ENV.DEBUG_WITH_DEBUG = 1 # include debug messages
	ENV.DEBUG_WITH_OUT = 1 << 1 # include out messages
	ENV.DEBUG_WITH_WARNING = 1 << 2 # include warning messages
	ENV.DEBUG_WITH_ERROR = 1 << 3 # include error messages
	ENV.DEBUG_WITH_ALL = ENV.DEBUG_WITH_DEBUG | ENV.DEBUG_WITH_OUT | ENV.DEBUG_WITH_WARNING | ENV.DEBUG_WITH_ERROR

	ENV.DEBUG_LEVEL = ENV.DEBUG_WITH_ALL # this could be changed during runtime to modify output

	def module_display_path(FILEPATH):
		filepath = os.path.realpath(FILEPATH)
		for project_path in ENV.__PRIVATE__['__SEARCH_PATHS__'].values():
			if project_path in filepath:
				return filepath[len(project_path):].strip(os.sep).replace(os.sep, '.')
		return filepath#.replace(os.sep, '.') # if doesn't work then just report as an actual filepath


	def snap_set_debug_level(LEVEL):
		# just in case this changes in the future
		ENV.DEBUG_LEVEL = LEVEL
	ENV.snap_set_debug_level = snap_set_debug_level

	def snap_inspect_frame(step_up=0):
		frame = inspect_currentframe().f_back # start with the calling frame (not this one)
		while step_up > 0:
			frame = frame.f_back
			step_up -= 1
		return frame
	ENV.snap_inspect_frame = snap_inspect_frame

	def snap_print_stack():
		ROOTPATH = getattr(ENV, '__SNAP_ROOTPATH__', None)
		if ROOTPATH is None:
			ROOTPATH = __file__.split(os.sep)
			ROOTPATH = os.sep.join(ROOTPATH[:ROOTPATH.index('snap')])
		current = inspect_currentframe()
		frames = [current.f_back]
		while frames[-1].f_back:
			frames.append(frames[-1].f_back)
		print('\n[{}]{} >> {}():'.format(current.f_lineno, module_display_path(__file__), current.f_code.co_name))
		for frame in reversed(frames):
			filepath = frame.f_globals['__file__']
			if ROOTPATH is not None:
				filepath = filepath.replace(ROOTPATH, '../')
			print('[{}]{} >> {}'.format(frame.f_lineno, filepath, frame.f_code.co_name))
	ENV.snap_print_stack = snap_print_stack
		

	def SNAP_FUNCNAME():
		return snap_inspect_frame(1).f_code.co_name
	ENV.SNAP_FUNCNAME = SNAP_FUNCNAME

	def SNAP_LINE():
		return snap_inspect_frame(1).f_lineno
	ENV.SNAP_LINE = SNAP_LINE

	def SNAP_FILENAME():
		return os_basename(snap_inspect_frame(1).f_globals['__file__'])
	ENV.SNAP_FILENAME = SNAP_FILENAME

	def snap_inspect_frame_info(FRAME):
		# just module and line (for the print functions)
		return FRAME.f_lineno, module_display_path(FRAME.f_globals['__file__'])
	ENV.snap_inspect_frame_info = snap_inspect_frame_info

	#def __print(FMT, *args): # XXX c will implement print() that behaves like python (with line and module injected?)
	#	print(FMT, args)
	def snap_print(*args):
		print("[{}]{} >>".format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_print = snap_print

	def snap_print_raw(*args):
		for a in args:
			sys.stdout.write(str(a))
	ENV.snap_print_raw = snap_print_raw

	def snap_debug(*args):
		if ENV.DEBUG_LEVEL & ENV.DEBUG_WITH_DEBUG:
			print("\033[94m[{}]{} >>\033[0m".format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_debug = snap_debug

	def snap_error(*args):
		if ENV.DEBUG_LEVEL & ENV.DEBUG_WITH_ERROR:
			print("\033[91m[{}]{} >>\033[0m".format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_error = snap_error

	def snap_warning(*args):
		if ENV.DEBUG_LEVEL & ENV.DEBUG_WITH_WARNING:
			print("\033[93m[{}]{} >>\033[0m".format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_warning = snap_warning
		
	def snap_out(*args):
		if ENV.DEBUG_LEVEL & ENV.DEBUG_WITH_OUT:
			print("\033[92m[{}]{} >>\033[0m".format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_out = snap_out

	def snap_log(*args):
		# TODO write to log file assigned to debugging?  debugging needs to be in ENV...
		print('[{}]{}:log >>'.format(*snap_inspect_frame_info(snap_inspect_frame(1))), *args)
	ENV.snap_log = snap_log

	def snap_test_out(STATEMENT):

		#line,module,_class,func = frame_info()
		frame = snap_inspect_frame(1)
		line,module = snap_inspect_frame_info(frame)

		frameinfo = inspect.getframeinfo(frame)
		source = frameinfo.code_context[0].strip('\t\n ')

		# remove the test_out() parens, only report between them
		# (this will also remove the test_out name, whatever it is called)
		source = source[source.find('(')+1:source.rfind(')')]

		if bool(STATEMENT):
			print("\033[92m[{}]{} >>\033[0m [\033[92mTEST OK\033[0m] {}".format(line, module, source))
		else:
			print("\033[91m[{}]{} >>\033[0m [\033[91mTEST FAIL\033[0m] {}".format(line, module, source))

		return bool(STATEMENT)
	ENV.snap_test_out = snap_test_out

	# https://stackoverflow.com/questions/34318948/how-to-determine-the-origin-of-a-python-exception
	def snap_exception_info(E):

		info = [] # stack of [(line,file), ...]

		frame = getattr(E, '__traceback__', None)
		while getattr(frame, 'tb_next', None):
			#print(frame.tb_lineno, os_basename(frame.tb_frame.f_code.co_filename))
			frame = frame.tb_next

		if frame is not None:
			return '[{}]{}.{} >> {}'.format(frame.tb_lineno, os_basename(frame.tb_frame.f_code.co_filename), frame.tb_frame.f_code.co_qualname, repr(E))
		else:
			return '[?]?.? >> {}'.format(repr(E))

	ENV.snap_exception_info = snap_exception_info

	def snap_print_exception(E):
		print('[{}]{} >>'.format(*snap_inspect_frame_info(snap_inspect_frame(1))), snap_exception_info(E))

	ENV.snap_print_exception = snap_print_exception



	# XXX TODO use strings as error identities instead?  just pass general Exception() with name?

	class SnapException(Exception):
		pass # TODO name and message  TODO or even make an error module that __getattr__ creates new Exception with attr name assigned...

	class SnapInfiniteRecursionError(Exception): pass
	ENV.InfiniteRecursionError = SnapInfiniteRecursionError



def main(ENV):

	ENV.snap_debug('this is debug')
	ENV.snap_out('this is out')
	ENV.snap_warning('this is a warning')
	ENV.snap_error('this is an error')

	print('')

	ENV.snap_set_debug_level(ENV.DEBUG_WITH_OUT)
	ENV.snap_debug('this is invisible')
	ENV.snap_out('this is visible')
	ENV.snap_set_debug_level(ENV.DEBUG_WITH_ALL)
	ENV.snap_debug('this is now visible')

	# NOTE: have to be inside a function for these to work:
	print('[{}]{}'.format(ENV.SNAP_LINE(), ENV.SNAP_FILENAME()), '>>', ENV.SNAP_FUNCNAME())

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

