
from weakref import ref as weakref_ref
import os

def build(ENV):

	SnapTimer = ENV.SnapTimer


	class SnapProjectTasks(object):

		__slots__ = ['__project__', '__tasks__', '__weakref__']

		def task_decorator(FUNC):
			def wrapper(self, *a, **k):
				timer = SnapTimer(None)
				gen = FUNC(self, self.__project__(), timer, *a, **k)
				existing = [t for t in self.__tasks__.get(FUNC.__name__, []) if t['running']] # housekeeping
				self.__tasks__[FUNC.__name__] = existing + [timer]
				timer.start(gen, seconds=0, repeat=True)
				return timer#FUNC(self, PROJECT, TIMER)
			return wrapper

		@task_decorator
		def refresh(self, PROJECT, TIMER):
			# run when packages change, make sure the file structure is loaded (just the basic dict and filepath info)

			self.loading()

			modules = [] # for post-processing to figure out how they connect together...

			for package in PROJECT.__snap_data__['__packages__'] or []:
				package_path = package['path']

				# TODO maybe in the future for large projects it might make sense not to do a full reload when packages change...?
				#	-- should accumulate the paths for os.walk() first into lists of the paths, and then check the differences...?
				package['files'] = []

				if not os.path.isdir(package_path):
					ENV.snap_warning('invalid package:', repr(package_path))
					yield
					continue

				for rootpath,subdirs,files in os.walk(package_path):

					if not files:
						package['empty_directories'] = package.get('empty_directories', []) + [rootpath]
						continue						

					for fname in files:
						filepath = os.path.join(rootpath,fname)
						split = fname.split('.')
						if len(split) > 1:
							ext = split[-1]
							lang = ENV.LANGUAGE.get_by_extension(ext)
						else:
							lang = None

						if not lang:
							# NOTE: layouts could apply colors for regular files based on mimetype
							# or something, and that would store with the layout, we'll just store the path
							package['files'] = package.get('files', []) + [{'filepath':filepath, 'stat':os.stat(filepath)}]
						else:
							#ENV.snap_out('module', filepath)
							module = {'filepath':filepath, 'module_info':{'language':lang}, 'stat':os.stat(filepath)}
							modules.append(module)
							package['files'] = package.get('files', []) + [module]

							# TODO lang.get_imports(module['filepath']) -> c can scan for includes

						PROJECT['layout'].register_file(package['files'][-1])

						#ENV.snap_out('load', fname)
						yield


			all_files = [f['filepath'] for f in package['files'] for package in PROJECT.__snap_data__['__packages__']]

			for module in modules:
				module_info = module['module_info']
				

			PROJECT['layout'].update()

			# TODO and now query the dependency structure: lang.get_imports(filepath) -> c can just scan for #include directives...?

			# TODO also initialize display?  load shaders, assign them to dict, have shaders for each of the file states...
			# TODO do lookup result as the dict, in the shader...

			# TODO cleanup

		@task_decorator
		def get_module_info(self, PROJECT, TIMER, FILE_INFO):
			'load ast and display info for it, if this is a language file...'

			# XXX this isn't a task, use a regular method?  open should do this AND perform the analysis...
			# get the module info, then figure out what the viable candidates possibly are, open those ones too...  then we can resolve the data and close the module

			assert isinstance(FILE_INFO, dict), 'not a dict: {}'.format(type(FILE_INFO))

			'get the language and decode it'
			# that's it, the orientation will be done by the caller

			yield

		@task_decorator
		def switch_to_layout(self, PROJECT, TIMER, LAYOUT):
			'set the display and positions of the modules, and assign the shaders from the layout?'
			# XXX instead of saving the layout setup we'll just make the layouts tasks...  then we can 'switch' by just running the layout task we want...
			# XXX we do need to save layouts so we can add changes made by user (even just dragging a module to a new position, or excluding a module from the layout rules)
			#	-- also we probably want to assign the 'active layout' handler so we can call it as other operations are completing...
			# TODO layout should also be per-component, and then general (so we layout the files and the overall package separately)

			yield

		@task_decorator
		def loading(self, PROJECT, TIMER):

			#existing = self.__tasks__.get('loading')
			#if existing is not None and existing[0]['running']:
			#	return

			self.__tasks__['loading'] = [TIMER] # only one

			'add a loading graphic to scene or to HUD'
			'animate it until tasks finished'

			yield

			

			# TODO register a loading graphic and animate it until complete (tasks finished?  maybe save the names of tasks at the start and wait for all of them to finish...)

		@task_decorator
		def dismiss(self, PROJECT, TIMER, *DISMISS):
			'remove the FILES, maybe do an animation / fade out / or pop?'

			for layout in PROJECT['layouts']:
				layout.dismiss(*DISMISS)

			yield
			"""
			for x in DISMISS:
				assert isinstance(x, dict), 'invalid dismiss type: {}'.format(type(x))
				if 'path' in x:
					'package'
					# if layout is displaying regular files then make a nice animation for them too...
				elif 'filepath' in x:
					'file'
				else:
					ENV.snap_warning('unhandled dismiss', x.keys())

				# TODO remove from any and all layouts?  layout handles animation?

				#x.clear() # XXX presumably the caller already discarded the reference...

			yield
			"""
		def __init__(self, PROJECT):

			assert PROJECT is not None
			self.__project__ = weakref_ref(PROJECT)
			self.__tasks__ = {
				#'name':[SnapTimer, ...], ...
			}


	ENV.SnapProjectTasks = SnapProjectTasks

