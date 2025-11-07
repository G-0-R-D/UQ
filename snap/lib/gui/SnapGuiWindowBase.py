
#from snap.lib.core import *

#from snap.lib.graphics.SnapWindow import * # includes Container
#from snap.lib.os.devices.SnapDevices import * # TODO access devices through ENV() though...



def build(ENV):

	SnapGuiDummyWindow = ENV.SnapGuiDummyWindow

	SNAP_DEBUGGING_GUI = True
	if SNAP_DEBUGGING_GUI:
		snap_debug = debug_gui = ENV.snap_debug_gui = ENV.snap_debug
	else:
		snap_debug = debug_gui = ENV.snap_debug_gui = lambda *args: None
	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error
	snap_out = ENV.snap_out

	#snap_input = ENV.snap_input
	#snap_emit = ENV.snap_emit

	SnapNode = ENV.SnapNode

	SnapContainer = ENV.SnapContainer
	SnapMetrics = ENV.SnapMetrics
	#SnapGraphic = ENV.SnapGraphic # TODO get from engine? XXX actually why not just subclass SnapNode?
	snap_extents_t = ENV.snap_extents_t
	snap_matrix_t = ENV.snap_matrix_t
	snap_extents_fit = ENV.snap_extents_fit
	snap_matrix_map_extents = ENV.snap_matrix_map_extents
	snap_matrix_invert = ENV.snap_matrix_invert
	SnapWindow = ENV.SnapWindow # TODO

	SnapMessage = ENV.SnapMessage

	#snap_incoming = ENV.snap_incoming
	snap_time = ENV.snap_time
	SNAP_FUNCNAME = ENV.SNAP_FUNCNAME

	# TODO get these from ENV.PROGRAM
	DEVICES = getattr(ENV, 'DEVICES', None)
	#TIMERS = getattr(ENV, 'TIMERS', None)
	SnapTimer = ENV.SnapTimer

	class SnapGuiWindowBase(SnapContainer):

		__slots__ = []

		#__slots__ = ['_user_', '_user_window_', '_gui_window_extents_', '_blit_texture_', '_fps_', '__render_forced__', 'interactive']

		GUI = None

		@ENV.SnapProperty
		class extents:
			# set and get locally, but also forwarded to user to crop as well!

			def get(self, MSG):
				"()->snap_extents_t"
				return SnapContainer.extents.get(self, MSG)

				"""
				# TODO add the gui offset to the user window?  or just deal with it separately?
				try:
					#ENV.snap_out('extents get', self['__user_window__']['extents'][:])
					return self['__user_window__']['extents']
				except:
					return snap_extents_t(0,0,0, 1,1,1)
				"""

			def set(self, MSG):
				"(snap_extents_t!)"
				#ENV.snap_out("set extents", MSG.args)
				SnapContainer.extents.set(self, MSG) # set normally

				# TODO this is user api, it should trigger gui window implementation resize event (which then bypasses this call)

				# forward to the user window
				try:
					self['__user_window__']['extents'] = MSG.args[0]
				except:
					pass

		@ENV.SnapProperty
		class matrix:

			def get(self, MSG):
				"()->snap_matrix_t"
				return SnapContainer.matrix.get(self, MSG)

			def set(self, MSG):
				"(snap_matrix_t!)"
				SnapContainer.matrix.set(self, MSG)
				#ENV.snap_out('set matrix', MSG.args[0][:])


		@ENV.SnapProperty
		class user:

			def get(self, MSG):
				"()->SnapContainer"
				return self.__snap_data__['__user__']

			def set(self, MSG):
				"(SnapContainer!)" # TODO (SnapNode) ?

				USER = MSG.args[0]

				if USER is not None:
					assert isinstance(USER, SnapNode),"gui \"user\" must be a SnapNode subtype or None"

				#existing_user = data.get('__user__')

				data = self.__snap_data__

				data['__user__'] = USER
				data['__blit_texture__'] = None

				if USER is None:
					data['__user_window__'] = None
					data['__blit_texture__'] = None
					#ENV.snap_out('set user abort')
					return

				elif isinstance(USER, SnapWindow):
					# toplevel must be a window so __user_window__.render() is available...
					debug_gui('user IS a Window')
					data['__user_window__'] = USER
				else:
					debug_gui('user is NOT a Window')
					if not isinstance(self['__user_window__'], SnapGuiDummyWindow):
						# TODO where to init size?  from user window?  if it is a window?
						# problem: gui window won't be resized when user resizes implicitly,
						# and init size is often 1 pixel, so we would likely end up with 1 pixel
						# gui window to init that won't rescale as user does...
						data['__user_window__'] = SnapGuiDummyWindow(items=[USER], size=[640,480])
					else:
						data['__user_window__'].set(items=[USER])

				user_window = data['__user_window__']

				user_window['extents'] = snap_extents_t(0,0,0, 640,480,0)

				# if toplevel is not in the same graphics engine as the gui then
				# image must be transferred to a local copy in gui format
				# so a __blit_texture__ is only assigned/used if user engine is different than
				# gui, otherwise __user_window__.texture() is used directly

				GUI_ENGINE = getattr(ENV, 'GUI_GRAPHICS', None) #ENV.snap_preferred_engine()
				if user_window is None:
					return
				USER_ENGINE = user_window['engine']

				assert GUI_ENGINE is not None, 'cannot render if no gui graphics!'

				if GUI_ENGINE == USER_ENGINE:
					data['__blit_texture__'] = None
				else:
					'assign __blit_texture__ to new GUI_ENGINE.Texture()'
					image = GUI_ENGINE.Image()
					data['__blit_texture__'] = GUI_ENGINE.Texture(image=image)

				if not DEVICES:
					ENV.snap_warning("no devices for user assign!")

				self.changed(user=USER)


		@ENV.SnapProperty
		class children:

			def get(self, MSG):
				"()->list(*SnapContainer)"
				return self['__user_window__'].children.get(*MSG.args, **MSG.kwargs)

			def set(self, MSG):
				"(list(*SnapContainer))"
				return self['__user_window__'].children.set(*MSG.args, **MSG.kwargs)



		@ENV.SnapChannel
		def device_event(self, MSG):
			# TODO forward to user?
			user_window = self['__user_window__']
			if user_window is not None:
				#ENV.snap_debug('unhandled device event', MSG.kwargs.keys())
				return user_window.device_event.__direct__(MSG)
			return None

		@ENV.SnapChannel
		def render(self, MSG):

			#ENV.snap_out('render begin', ENV.SnapTimers.CURRENT_TIME)

			# if "FORCE_RENDER" is called a flag is set to prevent the next render from going through until previous render completes...
			if not self['__render_forced__']:
				user_window = self['__user_window__']
				#ENV.snap_out("user window", user_window)
				if user_window is not None:
					if SNAP_DEBUGGING_GUI:
						start_time = snap_time()
					#ENV.snap_out('user window render', user_window, user_window['render_items'])
					user_window.render()
					if SNAP_DEBUGGING_GUI:
						start_time = snap_time() - start_time
						#snap_debug_gui("render completed in %lf secs or %lf/sec", start_time, 1.0/start_time)

					#ENV.snap_out("user_window items", list(user_window.render_items()))
					#import os
					#savepath = '/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/TestNode_render_result.png'
					#texture = user_window['texture']
					#if not os.path.exists(savepath) and texture['image']['size'] != [1,1]:
					#	ENV.snap_out("image saved", savepath, texture['image']['size'])
					#	texture['image'].save(savepath)

					self.trigger_blit() # gui updates display

					# TODO if getattr(self, "interactive") == "TRUE": update active graphic of pointers?  then all other event updates refer to that graphic

			else:
				# cancels force status, another force may now commence
				self['__render_forced__'] = False

			# TODO if interactive then do a lookup on render for each pointer device?
			# otherwise pointer motion does a lookup
			# pointer buttons can then just use the lookup result assigned to the device!

			return None

		@ENV.SnapChannel
		def force_render(self, MSG):
			# TODO put this onto a special FPS timer that can be forced?  listen to refresh and when it happens then reset render forced to False
			# this is a way for the user to kind of force a synchronization with the rendering and the scene
			# like for video playback: this is called when the frame is ready for display
			# NOTE: you can only force once per fps, force won't be possible again until fps timeout

			if not self['__render_forced__']:
				#snap_setattr_at(self, "__render_forced__", "FALSE", IDX_SnapGuiWindowBase___render_forced__);
				self.render()
				self['__render_forced__'] = True # means don't render again until refresh callback...
				self._reset_render_timer() # now next fps timeout should be in synch
			else:
				pass #snap_out("render force denied")

			return None

		@ENV.SnapChannel
		def sync_render(self, MSG):
			return self.force_render.__direct__(MSG)

		@ENV.SnapChannel
		def allocate(self, MSG):
			ENV.snap_warning("TODO: allocate deprecated")

			# XXX make this self['extents'] = snap_extents_t() (or just forward to it?)
			# TODO when resized, buffer is invalidated (delete?) and then recreated when needed on render (or blit?) call

			#def allocate(self, extents=None, **SETTINGS):

			extents = MSG.unpack('extents', None)

			#ENV.snap_out("allocate", extents)

			if not extents:
				return None

			curr_extents = self['extents']
			if not curr_extents or extents[:] != curr_extents[:]:
				# extents changed
				# TODO make sure extents fit in screen?

				ext = extents
				# take position out of extents, just size passed to subordinates -- so window extents are normal extents?
				user_extents = snap_extents_t(0.,0.,0., ext[3]-ext[0], ext[4]-ext[1], ext[5]-ext[2])

				self['extents'] = ext

				# send to user window and user window is expected to send to user and so on...
				user_window = self['__user_window__']
				user_window.allocate(extents=user_extents)

				# XXX window dummy forwards crop to user?
				if 0:
					user = data['__user__']
					if user and user != user_window:
						user.allocate(extents=user_extents)

			return None

		@ENV.SnapChannel
		def changed(self, MSG):

			source = MSG.source

			#if source is data['__user_window__'] or source is data['__user__']:
			if source is self['__user__']: # TODO user window or a texture?
				# TODO just call set user again?  and update blit data logic is now there...
				#self._update_blit_data()
				self.set(user=source)

			elif source is self:
				ENV.snap_out('gui resize?') # TODO
				#self.allocate()
				# emit changed...



		@ENV.SnapChannel
		def focus(self, MSG):
			raise NotImplementedError() # TODO?

		@ENV.SnapProperty
		class frames_per_second:
			def get(self, MSG):
				"""()->float"""
				return float(self.__snap_data__['fps'] or 0.)

			def set(self, MSG):
				"""(float)"""
				t = MSG.args[0]
				if t:
					assert isinstance(t, (float,int)), 'must be float or int'
				else:
					t = 0.

				self.__snap_data__['fps'] = float(t)
				self._reset_render_timer()

		@frames_per_second.shared
		class fps: pass

		@ENV.SnapProperty
		class gui_extents:
			def get(self, MSG):
				"""()->snap_extents_t"""
				return self.__snap_data__['__gui_window_extents__'] or snap_extents_t()

		@gui_extents.shared
		class window_extents: pass

		@ENV.SnapChannel
		def blit(self, MSG):
			# TODO make this call self.draw() and that does the image transfer?
			raise NotImplementedError()

		@ENV.SnapChannel
		def trigger_blit(self, MSG):
			# gui will usually have some way to flag that window display needs to be updated, call it here
			return self.blit.__direct__(MSG)

		@ENV.SnapChannel
		def grab(self, MSG):
			raise NotImplementedError('grab')


		def _update_blit_data(self, MSG):
			# when user window changes this is called from callback to reconfigure blit texture

			return None

			GUI_ENGINE = getattr(ENV, 'GUI_GRAPHICS', None) #ENV.snap_preferred_engine()
			user_window = self['__user_window__']
			if user_window is None:
				return
			USER_ENGINE = user_window['engine']

			blit_texture = None

			# TODO this just needs to create an intermediary texture if user isn't a window...
			# XXX just do the isinstance(user, window) check on blit?  then obtain the image and use it or else?
			#	-- but it's more efficient to have the engine specific image already in existence for the transfer, and it's a better strategy to use the existing proxy api...
			# XXX Proxy deprecated, just connect changed events together between engines!
			# TODO either user is window, use it as is (assign as __user_window__), or create dummy window...
			#	-- user is window in same engine, or window but different engine...  so we may need to use a dummy window AND transfer the buffer to other engine!
			#	-- so use the texture from __user_window__ directly, and connect the changed events together?

			if 'user is not window':
				'__user_window__ = DummyWindow()'
			else:
				'__user_window__ = __user__'

			if 'user engine is different':
				'__blit_texture__ is new and listens for changed'
			else:
				'__blit_texture__ is __user_window__ texture'

			if GUI_ENGINE and USER_ENGINE:
				# renderable, make proxy if needed
				ENV.snap_out("GUI_ENGINE and USER_ENGINE")
				if USER_ENGINE is not None and GUI_ENGINE is not None:
					image = user_window['image']
					if image is not None:
						ENV.snap_out("image is not None")
						blit_texture = GUI_ENGINE.Texture(image=GUI_ENGINE.Proxy(image)) # XXX proxy no longer exists...  (just connect the changed events...)
					ENV.snap_out("image is None")
				else:
					ENV.snap_out("using texture")
					blit_texture = user_window['texture']

			else:
				if GUI_ENGINE is None:
					# this may initially be true until user adds subitems or shader -- then render call will
					# find the engine and rendering will begin
					ENV.snap_warning("ENGINE not set for GUI window! (nothing will display)")

			ENV.snap_out("assign __blit_texture__", blit_texture)
			self['__blit_texture__'] = blit_texture

			return None

		def _get_default_deviceXXX(self, MSG):
			# (self, DEVICE_NAME):

			try:
				DEVICES = ENV.DEVICES
			except:
				return None

			if DEVICES:
				default = DEVICES.device(DEVICE_NAME, 0)
				if default:
					return default

			return None

		def _reset_render_timer(self):
			# (self):

			#TIMERS = getattr(ENV, 'TIMERS', None)
			#if TIMERS is None:
			#	ENV.snap_debug("no TIMERS on window for fps timeout")
			#	return None

			fps = self['fps']
			if fps is None:
				ENV.snap_debug("no fps on window for fps timeout!")
				return

			#TIMERS.start(self.render, fps=fps, repeat=True)
			ENV.snap_out('timer init')
			self.__snap_data__['__render_timer__'] = SnapTimer(self.render, fps=fps, repeat=True)




		#@ENV.SnapChannel
		def lookupXXX(self, MSG):
			# (self, X, Y):#, GRAPHIC, OFFSET):
			# just return the front-most interactive graphic

			x,y = MSG.args

			ENV.snap_warning('lookup', 'not implemented')

			# do graphic lookup on new window

			user_window = self['__user_window__']

			# TODO lookup
			#lookup_results = user_window.lookup(position=local_position)
			lookup_results = []
			if lookup_results:
				return lookup_results[0]

				#*GRAPHIC = (SnapNode)lookup_results->data[0];
				#lookup_results->data[0] = NULL;

				#snap_memcpy(OFFSET, lookup_results->data[1], 16 * sizeof (double));
				#lookup_results->data[1] = NULL; // allow free to happen

				#SnapEngine_delete_lookup_results(&lookup_results);

			return (None, None) #snap_matrix_t(*SNAP_IDENTITY_MATRIX))




		def _update_window_bounds(self):
			#(self, x, y, w, h):
			# callback from gui resize/window configure event (bypasses user api and call superclass directly)
			# ie. this call is between the gui and the superclass: user api -> gui (trigger event) -> this -> superclass

			#double curr_ext[] = {0., 0., 0., 0., 0., 0.};
			#snap_copyattr_at(self, "_gui_window_extents_", curr_ext, 6 * sizeof (double), IDX_SnapGuiWindowBase__gui_window_extents_);
			#snap_copyattr_at(self, "_extents_", curr_ext, 6 * sizeof (double), IDX_SnapMetrics__extents_);

			# just always assign a fresh set (so it is set before events go out)
			# TODO use matrix to translate window for easy point mapping
			#double new_window_ext[] = {0., 0., 0., w, h, 0.};
			#snap_assignattr_at(self, "_extents_", new_window_ext, 6 * sizeof (double), IDX_SnapMetrics__extents_);

			curr_ext = self['extents']
			if curr_ext is not None and ((curr_ext[3] - curr_ext[0]) != w or (curr_ext[4] - curr_ext[1]) != h):
				# resized (resize event)
				#debug_gui("resize(%.1lf %.1lf) ext(%.1lf %.1lf %.1lf  %.1lf %.1lf %.1lf) extw(%lf) exth(%lf)", w, h,
				#	curr_ext[0], curr_ext[1], curr_ext[2], curr_ext[3], curr_ext[4], curr_ext[5],
				#	curr_ext[3] - curr_ext[0], curr_ext[4] - curr_ext[1]
				#	);
				new_ext = snap_extents_t(0.,0.,0., w,h,0.) #double new_ext[] = {0., 0., 0., w, h, 0.}; // user space is always at pos(0,0)

				# NOTE: we do not call snap_event(self, "CROP", ...) because that is a user api call and would create a loop!
				# this if FROM the gui event callback and needs to finalize the window configure (and send to user)
				#snap_event_redirect(SnapGuiWindowBase_event, self, "CROP", "extents", new_ext);
				SnapGuiWindowBase.allocate(self, SnapMessage(extents=new_ext))


			m = self['matrix']
			if m is not None and (m[3] != x or m[7] != y):
				# position changed (move event)
				#debug_gui("TODO window move(%lf %lf) != (%lf %lf)", x,y, curr_ext[0], curr_ext[1]);

				m[3] = x
				m[7] = y
				m[11] = 0.
				#snap_assignattr_at(self, "_matrix_", m, 16 * sizeof (double), IDX_SnapMatrix__matrix_);

			return None


		@ENV.SnapChannel
		def fit_to_user_content(self, MSG):
			ENV.snap_out('fit to user content', self['__user__'])
			user = self['__user__']
			if user is not None:
				user_ext = self['__user__']['mapped_extents']
				#self.allocate(extents=user_ext)
				self['extents'] = user_ext
			else:
				ENV.snap_warning('no user on window to fit')

		@ENV.SnapChannel
		def center(self, MSG):
			# TODO call this fit()?
			'get current size and position the gui window in the screen'
			sw,sh = ENV.GUI['screen_size']

			screen_extents = snap_extents_t(0,0,0,sw,sh,0)
			ext = self['extents'] or snap_extents_t(0,0,0, 0,0,0)
			ENV.snap_out('center', sw,sh, ext)
			M = SnapMetrics(extents=ext)
			snap_extents_fit(screen_extents,M,uniform=True,lock_scale=True)

			#ENV.snap_out("extents fit", M.mapped_extents()[:])
			#self.allocate(extents=M['mapped_extents'])
			self['extents'] = M['mapped_extents']


		def __init__(self, items=None, user=None, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			GUI = self.GUI
			assert GUI is not None, 'gui not assigned in gui window'
			GUI.__snap_data__['__open_windows__'] = (GUI.__snap_data__['__open_windows__'] or []) + [self]

			data = self.__snap_data__

			data['__user__'] = None
			data['__user_window__'] = None
			#ext = self._gui_window_extents_ = snap_extents_t(0,0,0, 640,480,1)
			data['__blit_texture__'] = None # XXX TODO have the image and texture ready to go (if not the same as the user engine, do the pixel transfer on the blit)
			data['fps'] = None # XXX fps is program or env domain...
			data['__render_forced__'] = False
			data['interactive'] = False # XXX gui is always interactive, just depends on if user is...?  assume it always is for now?  if not then lookup render won't do anything...?

			if items and user is not None:
				ENV.snap_warning("items not allowed, must be assigned a single \"user\"")

			#self.set(**{k:v for k,v in SETTINGS.items() if k in ('width','height','size','extents')})

			self.set(user=user)

			#ENV.snap_out('user set', self['user'])

			if 0: # TODO
				w,h = self['size']
				if w <= 1 or h <= 1:
					self.set(size=(640,480))

			"""
			for_attr_in_SnapNode(MSG)
				if (attr == (any)"width"){
					ext[3] = ext[0] + *((double*)value);
					size_set = 1;
				}
				else if (attr == (any)"height"){
					ext[4] = ext[1] + *((double*)value);
					size_set = 1;
				}
				else if (attr == (any)"size"){
					ext[3] = ext[0] + ((double*)value)[0];
					ext[4] = ext[1] + ((double*)value)[1];
					size_set = 1;
				}
				else if (attr == (any)"extents"){
					snap_memcpy(ext, value, 6 * sizeof (double));
					size_set = 1;
				}
			}

			if (ext[3] < 1) ext[3] = 1; # should be if ext[3] <= ext[0]: ext[3] = ext[0]+1
			if (ext[4] < 1) ext[4] = 1;
			"""

			# size of GUI window on screen
			#snap_assignattr_at(self, "_gui_window_extents_", ext, 6 * sizeof (double), IDX_SnapGuiWindowBase__gui_window_extents_);

			# size with gui window corner as origin (ie. local to window, user space) XXX TODO use matrix for translation
			#snap_event(self, "CROP", "extents", ext);

			self['interactive'] = True # TODO better api

			if not self['fps']:
				self.set(fps=30.0)


	ENV.SnapGuiWindowBase = SnapGuiWindowBase

