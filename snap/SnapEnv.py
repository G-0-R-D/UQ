
# ABOUT:
"""
the env build system requires that participating modules implement a build(ENV) in their mainbody and optionally a main(ENV) if they want to run directly (useful for testing)

the advantages:
	1. modules have no import statements, they just access what they want to use from the ENV by name, which gives us the opportunity to change what is being accessed (even at runtime...)
		-- Also moving nodes around is easier since they don't need to update their own import statements
		-- a good practice is to put the ENV.__build__ statements into the __init__.py of a folder to easily just build the whole sub-package (which is usually what you want to do anyway)
	2. modules can be placed anywhere inside the package, and have access to data from all other modules anywhere else in the package (relative to the package root -- registered with the ENV)
	3. when importing modules there is no implicit execution of the module (other than to define the build and main), so when you want just a module from a package you don't have to build a.b.c.... you can just build c when you access a.b.c.build(ENV)
	4. it bypasses bootstrapping problems, like many gui libraries have when initializing a new application, where the application needs to exist and be init() before the rest of the code can run...  initialization is very easily and explicitly handled in build() and then main() comes after all modules have been built.
		-- ie. you'll notice engine components and gui stuff doesn't have to worry about backend and initialization stuff, it just assumes that has already been done before it is even built with it's build(ENV) call!

NOTE: main(ENV) can still access ENV.__build__ if it needs to initialize something to be able to run
"""

import os#, inspect
THISDIR = os.path.realpath(os.path.dirname(__file__))

import importlib.util
import sys

from collections import OrderedDict
from types import FunctionType

SNAP_DIR = os.path.realpath(os.path.dirname(__file__)).rstrip(os.sep)
assert SNAP_DIR.endswith('snap'), 'not in snap project directory? {}'.format(repr(THISDIR))
SNAP_PATH = os.path.dirname(SNAP_DIR)
"""
assert THISDIR.endswith('snap/lib/core'), 'not in core folder? {}'.format(THISDIR)
assert THISDIR.count('snap') == 1, 'incorrect folder structure for ENV setup? {}'.format(THISDIR)
SNAP_DIR = THISDIR
while not SNAP_DIR.endswith('snap'):
	SNAP_DIR = os.path.dirname(SNAP_DIR)
"""

if SNAP_PATH not in sys.path:
	sys.path.insert(1, SNAP_PATH)
	print('snap:', repr(SNAP_DIR))

def purge_pycache(ROOT):

	# I have found sometimes that changes to files don't register if there is a cached version, as the cache is preferred
	# I usually run with "python -B module.py" to prevent these in the first place
	#	-- pycache is useful once your code is complete; but not useful when you're actively developing it :)

	from shutil import rmtree
	import os
	for r,s,f in os.walk(ROOT):
		if '__pycache__' in s:
			cache = os.path.join(r, '__pycache__')
			print('purged', cache)
			rmtree(cache)
			s.remove('__pycache__')
assert os.path.basename(os.path.dirname(THISDIR)) == 'UQ'
#purge_pycache(os.path.dirname(THISDIR))

class SnapEnv(object):

	# TODO wishlist: make this a lazy import system using __getattr__ or something?  so we build dependencies only when they are needed?  but how to know what the dependencies are without building?  python modules could be analyzed with ast...?

	# NOTE to self: self.__PRIVATE__['__MAINLOOP_NODE__'] can also be found at ENV.mainloop.__data__[0]
	#@property
	#def __mainloop__(self):
	#	self.mainloop # touch to create mainloop
	#	return self.__PRIVATE__['__MAINLOOP_NODE__']

	def mainloop_next(self):
		# this is in user space, for if the user wants to pump the mainloop themselves
		M = self.__PRIVATE__.get('__MAINLOOP_NODE__')
		if M is None:
			self.mainloop
			M = self.__PRIVATE__['__MAINLOOP_NODE__']
		assert not M.OWNED, 'mainloop already in use'
		return M.next()

	def mainloop_start(self):
		''

	@property
	def mainloop(self):
		# NOTE: if an error occurs inside a property when __getattr__ is used,
		# it will cause AttributeError (when error might be something else)
		# https://perso.lpsm.paris/~msangnier/property.html

		LOCAL_ENV = self

		#TIMERS = self.TIMERS
		SnapTimers = self.SnapTimers
		snap_time_since_epoch = self.snap_time_since_epoch

		NODE = LOCAL_ENV.__PRIVATE__.get('__MAINLOOP_NODE__')
		if NODE is None:

			DUMMY_MSG = LOCAL_ENV.SnapMessage()

			class MainLoop(LOCAL_ENV.SnapNode):

				__slots__ = []

				OWNED = False # claim mainloop by assigning here, if assigned then user cannot call mainloop_next()

				@LOCAL_ENV.SnapProperty
				class running:

					def get(self, MSG):
						"()->bool"
						return bool(self.__snap_data__['__running__']) # XXX or assign the owner of the mainloop process?  like gui?

				@LOCAL_ENV.SnapChannel
				def mainloop(self, MSG):
					""
					raise NotImplementedError('use ENV.mainloop_start()')

				# not a SnapChannel so it can't be connected into, as that would be crazy
				def next(self):

					current = self['__pending__'] or []
					self['__pending__'] = []

					# TIMERS and TASKS listen to mainloop to function, user can listen to mainloop too,
					# but using tasks or timers is the preferred method...

					CURRENT_TIME = snap_time_since_epoch()
					SnapTimers.ELAPSED_TIME = CURRENT_TIME - SnapTimers.CURRENT_TIME
					SnapTimers.CURRENT_TIME = CURRENT_TIME

					self.mainloop.__send__(DUMMY_MSG)

					for node,ch,msg in current:
						try:
							getattr(node,ch).__send__(msg)
						except Exception as e:
							LOCAL_ENV.snap_error(repr(e), LOCAL_ENV.snap_exception_info(e))

					#self.next.send() # ? notify that next was called specifically?  technically same as mainloop though...

					self.__timeout__() # ?  block only if this is it's own thread...

					return True # continue

				def __timeout__(self):
					# waits if running faster than rate

					# TODO either program runs in own thread (so has own mainloop) or in same thread as main app,
					# in which case the main app will drive the refresh (call timer timeouts directly...
					# ie. same-thread program should register with main app when running (and ignore when stopped?)

					rate = self['__rate__']

					elapsed = LOCAL_ENV.snap_time_since_epoch() - self['__last_time__']
					if elapsed < rate:
						#print('sleep used')
						LOCAL_ENV.snap_sleep(rate - elapsed) # wait remaining (extra) time
					self['__last_time__'] += elapsed

					return None


				def __snap_queue_send__(self, NODE, CHANNEL, MSG):

					# TODO use linked list?
					# TODO length check?  make sure there aren't too many in queue?
					self['__pending__'].append((NODE, CHANNEL, MSG))
					return True # accepted

				def __init__(self):
					LOCAL_ENV.SnapNode.__init__(self)

					self['__pending__'] = []

					# TODO nicer?
					self['__last_time__'] = LOCAL_ENV.snap_time_since_epoch()
					self['__rate__'] = 1/2000. # not full on to start (set 0 for max speed)

			NODE = self.__PRIVATE__['__MAINLOOP_NODE__'] = MainLoop()

		return NODE.mainloop

	def __snap_queue_send__(self, NODE, CHANNEL, MSG):
		self.mainloop # touch to create node if not existing
		return self.__PRIVATE__['__MAINLOOP_NODE__'].__snap_queue_send__(NODE, CHANNEL, MSG)






	def __getattr__(self, ATTR):
		#print('ENV getattr', ATTR)

		#if ATTR == 'mainloop':
		#	return self.mainloop_test()

		# lazy load?
		# TODO make lazy loading a general policy?  if attr is in built modules (we need to track the names as we build, check the difference) then build...
		# the only trick there is we need to build first to know what the new names are...  then save to json file externally or something?
		#if ATTR in ('TIMERS', 'TASKS'):
		#	d = {'TIMERS':'SnapTimers', 'TASKS':'SnapTasks'}
		#	n = getattr(self, d[ATTR])()
		#	setattr(self, ATTR, n)
		#	return n

		try:
			#if self.__PARENT_ENV__ is not None:
			return getattr(self.__PRIVATE__['__PARENT_ENV__'], ATTR)
		except AttributeError as e:
			raise AttributeError('{} has no attribute: {}'.format(self.__class__.__name__, repr(ATTR)))

	def __import__(self, STRING):

		module_name = STRING

		if module_name in sys.modules:
			module = sys.modules[module_name]
			return module

		user_path = module_name.split('.')
		root = user_path[0]
		searchpath = self.__PRIVATE__['__SEARCH_PATHS__'][root]

		filepath = os.path.join(searchpath, os.sep.join(user_path))
		if os.path.isdir(filepath):
			filepath = os.path.join(filepath, '__init__.py')
		else:
			filepath = filepath + '.py'

		spec = importlib.util.spec_from_file_location(module_name, filepath)
		module = importlib.util.module_from_spec(spec)
		sys.modules[module_name] = module
		spec.loader.exec_module(module)

		return module

	def __build__(self, STRING):
		# TODO import should build if not yet...

		# TODO save list of keys before build, keep track of modules that belong with that build by checking the difference after...
		# TODO OR: do a build call with a fake ENV object, that just keeps track of what is requested...?  what is assigned...  what is built...
		#	-- wild idea: use __getattr__ and do a search for module name when it is missing?  then when a name is accessed that doesn't exist, it gets built...  just requires that modules represent single objects with the same name...  (engines break this)

		# XXX can we figure out the dependencies by just parsing the ast of all the project modules themselves?  (they will always assign to ENV...?  engine components assign to ENV.graphics.__current_graphics_build__...)

		# XXX most of the functionality of the program will be implemented by parsing and compiling other code, in which case the namespace and the env for that will be very customizable...  so we don't really need this to be so fully featured!  treat this one as just one big shared namespace...

		module_name = STRING
		# TODO support importing by full absolute path as well...

		if 0:
			try:
				trace = self.snap_inspect_frame(1).f_globals['__file__'].replace(SNAP_PATH, '..')
				print('ENV.__build__ >>', trace, STRING)
			except:
				print('ENV.__build__ >>', STRING)

		if module_name not in self.__PRIVATE__['__BUILT_MODULES__']:

			# NOTE: the reason double build can't be allowed is because if a build localizes with Class = ENV.Class then a new ENV.Class assignment would be a different Class than the one in use!
			#raise NameError('double build', module_name)

			if module_name not in sys.modules:
				module = self.__import__(module_name)
			else:
				module = sys.modules[module_name]

			# NOTE: build doesn't HAVE to return anything...
			_return = module.build(self)
			self.__PRIVATE__['__BUILT_MODULES__'][module_name] = module
		else:
			_return = self.__PRIVATE__['__BUILT_MODULES__'][module_name]

		return _return


	def __run_gui__(self, NODE, *user_args, **user_kwargs):
		# this will start an application mainloop, using gui if selected
		# INTERNALS is a dict of internal options

		args,INTERNALS = self.__init_argv__()

		#if not INTERNALS:
		#	INTERNALS = {}
		assert isinstance(INTERNALS, dict)

		if self.__PRIVATE__.get('__RUNNING__', False):
			raise RuntimeError('ENV is already running')
		self.__PRIVATE__['__RUNNING__'] = True


		# TODO headless XXX for now use self.__run__() for headless
		# moved to __init__ so they exist before module build calls...
		#self.graphics.load(name=INTERNALS.get('graphics', 'QT5'))
		GUI = self.GUI

		win = GUI.Window() # so self.GUI.MAINWINDOW exists before user.__init__() is run

		#self.__build__('snap.lib.app')


		instance = None
		if isinstance(NODE, str):
			STRING = NODE
			assert STRING not in self.__PRIVATE__['__BUILT_MODULES__'], 'unsupported, build value should return instance'
			if STRING not in self.__PRIVATE__['__BUILT_MODULES__']:
				# TODO returned values should be saved with the built module data?
				loaded = self.__build__(STRING)

			assert loaded is not None, 'user build() must return instance to run in gui'

			instance = loaded(*user_args, **user_kwargs)

		elif isinstance(NODE, type) and issubclass(NODE, self.SnapNode):
			instance = NODE(*user_args, **user_kwargs)
		elif isinstance(NODE, FunctionType) and getattr(NODE, '__name__', None) == 'build':
			loaded = NODE(self)
			instance = loaded(*user_args, **user_kwargs)
		else:
			assert NODE is None, 'must provide string path or SnapNode baseclass for gui to run, not: {}'.format(NODE)
			instance = None

		#self.gui.start(user=instance)
		win['user'] = instance
		GUI.start_mainloop()

		del self.__PRIVATE__['__RUNNING__']

		self.snap_out('__run_gui__({}) -> exit ok\n'.format(repr(NODE)) + 80 * '_')


	def __run__(self, X, *user_args, **user_kwargs):
		# this will run the main(ENV) function of the module defined by STRING (after building it)
		# useful for writing tests for individual modules (usually done with "if __name__ == '__main__':")

		# TODO or pass SnapNode or main function?

		if isinstance(X, str):
			STRING = X
			if os.sep in STRING:
				# TODO convert the system path into dot notation, relative to a package root...
				raise NotImplementedError('path', STRING, os.curdir())

			if STRING not in self.__PRIVATE__['__BUILT_MODULES__']:
				self.__build__(STRING) # TODO if SnapNode instance is returned then instantiate it

			module = self.__PRIVATE__['__BUILT_MODULES__'][STRING]
			assert hasattr(module, 'main'), '{} has no main function'.format(repr(STRING))

			_return = module.main(self)

			if _return is not None:
				self.snap_warning('main() returned: ', _return)

		elif isinstance(X, FunctionType) and getattr(X, '__name__', None) == 'build':
			loaded = X(self)
			assert isinstance(loaded, type)
			instance = loaded(*user_args, **user_kwargs)

		elif isinstance(X, type):# and issubclass(X, self.SnapNode):
			instance = X(*user_args, **user_kwargs)
		else:
			assert X is None, 'must provide string path, type, or callable to run'

		self.snap_out('__run__({}) -> exit ok\n'.format(repr(X)) + 80 * '_')

	def __register_import_path__(self, PATH):
		# TODO this becomes a viable root for import (like 'snap' is the root folder found on the path...)

		PATH = os.path.realpath(PATH)
		assert os.path.isdir(PATH), 'not a directory: {}'.format(repr(PATH))

		name = os.path.basename(PATH)

		SEARCH_PATHS = self.__PRIVATE__['__SEARCH_PATHS__']
		assert name not in SEARCH_PATHS.keys(), 'cannot use same basename as another registered path (same name): {}'.format((repr(PATH), repr(SEARCH_PATHS[name]), repr(name)))
		SEARCH_PATHS[name] = os.path.dirname(PATH)

	def __register_package__(self, PATH):
		return self.__register_import_path__(PATH)

	def __init_argv__(self):
		# TODO use json on commandline to pass args...  (serialize json for all inter-process communications?)
		p = self.__PRIVATE__
		return p['__init_args__'], p['__init_kwargs__']

	def __init__(self, parent=None, *ARGS, **KWARGS):

		if parent is not None:
			assert isinstance(parent, SnapEnv), 'SnapEnv(parent) must be SnapEnv or subtype, not: {}'.format(repr(type(parent)))

		PRIVATE = self.__PRIVATE__ = {
			'__BUILT_MODULES__':OrderedDict(),
			'__PARENT_ENV__':parent,
			'__SNAP_RECURSION_GUARD__':3000,

			'__SEARCH_PATHS__':{'snap':SNAP_PATH}, # SNAP_PATH is directory where snap is found (parent directory of snap)

			# TODO: these obtained from sys.argv by caller, and passed into __init__()
			# -- merge with what is passed into __init__ here...  warn if conflicting?
			#	-- json: args:"[1,2,3]" kwargs:"{'a':1}" -- make command line easier to use by using json strings? "{...}" ? -- can tie in to save/load SnapNode api?
			'__init_args__':ARGS,
			'__init_kwargs__':KWARGS,
		}

		self.SnapEnv = SnapEnv

		# TODO only build these if parent ENV is None or in separate thread...
		# TODO also use lazy loading system... XXX that will be for interpreted components...
		self.__build__('snap.lib.extern')
		self.__build__('snap.lib.core')

		self.__build__('snap.lib.events')
		self.__build__('snap.lib.graphics')
		self.graphics.load(name=KWARGS.get('graphics', 'QT5'))

		self.__build__('snap.lib.os.multiprocessing')
		self.__build__('snap.lib.os.devices')
		self.__build__('snap.lib.gui')
		GUI = self.gui.load(name=KWARGS.get('gui', 'QT5'))

		self.__build__('snap.lib.parsing')

		self.__build__('snap.lib.programming')


def main():

	ENV = SnapEnv()

	#ENV.__run_gui__(None)#'snap.lib.graphics.engines.SnapEngineTest')
	#ENV.__run_gui__('snap.lib.gadgets.media.SnapMediaPlayer')
	#ENV.__run__('snap.lib.core.SnapNode')
	#ENV.__run__('snap.lib.media.SnapMediaReader')
	#ENV.__run_gui__('snap.lib.os.devices.SnapDevicesTest')
	#ENV.__run__('snap.lib.os.devices.SnapDeviceKeyboard')
	ENV.__run_gui__('snap.lib.gui.widgets.SnapButton')
	#ENV.__run__('snap.lib.graphics.shader.SnapShaderProgram')
	#ENV.__run_gui__('snap.lib.gadgets.code.SnapCodeViewer')

	#ENV.__run__('snap.lib.parsing.language.c')

if __name__ == '__main__':

	main()

