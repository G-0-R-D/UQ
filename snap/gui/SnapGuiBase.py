
#from snap.lib.core import *

#from snap.lib.gui import SnapGuiWindowBase as SnapGuiWindowBaseModule
#from snap.lib.os.devices.SnapDeviceInteraction import *

def build(ENV):

	SnapNode = ENV.SnapNode

	SnapMessage = ENV.SnapMessage

	snap_matrix_t = ENV.snap_matrix_t
	snap_extents_t = ENV.snap_extents_t
	snap_vector_t = ENV.snap_vector_t
	snap_matrix_transform_point = ENV.snap_matrix_transform_point
	snap_matrix_map_extents = ENV.snap_matrix_map_extents
	snap_matrix_invert = ENV.snap_matrix_invert
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX

	snap_gui_update_pointer_interaction = ENV.snap_gui_update_pointer_interaction

	SnapCamera = ENV.SnapCamera

	snap_time = ENV.snap_time

	DEVICES = getattr(ENV, 'DEVICES', None)
	if not DEVICES:
		ENV.snap_warning('gui did not find devices!  (mouse and keyboard events won\'t work)')

	LOOKUP_IMAGE = [None] # assign once used, created from ENV.GRAPHICS.Context()
	def lookup_image():
		img = LOOKUP_IMAGE[0]
		if img is None:
			img = ENV.GRAPHICS.Image(width=1, height=1, format='RGBA')
			LOOKUP_IMAGE[0] = img
		return img

	class SnapGuiBase(SnapNode):

		__slots__ = []

		#__slots__ = ['name', 'version', '_window_', '_open_windows_', 'INTERACTION']

		# TODO make keyboard and pointer handlers, which add the extra params, do the lookup, and forward the event...

		#@snap_incoming

		Window = None # assign in implementation

		@ENV.SnapProperty
		class mainwindow:
			def get(self, MSG):
				"()->SnapGuiWindowBase"
				windows = self['windows']
				assert windows, 'no mainwindow'
				if len(windows) > 1:
					ENV.snap_warning('mainwindow access with > 1 window')
				return windows[0] # mainwindow will always be first created...

			set = None

		@mainwindow.alias
		class default_window: pass

		@ENV.SnapProperty
		class name:
			def get(self, MSG):
				'()->str'
				return self.__class__.__name__

		@ENV.SnapProperty
		class __open_windows__:

			def get(self, MSG):
				return self.__snap_data__['__open_windows__'] or []

		@ENV.SnapProperty
		class windows:
			def get(self, MSG):
				"""()->list(*SnapGuiWindow)"""
				return self['__open_windows__'][:] # copy so user can't change it

		@ENV.SnapProperty
		class screen_size:
			def get(self, MSG):
				"""()->list(int,int)"""
				raise NotImplementedError('must be implemented by gui (subclass)')


		@ENV.SnapChannel
		def device_event(self, MSG):

			ACTION = MSG.kwargs.get('action')
			SOURCE = MSG.kwargs['source']

			#ENV.snap_out('announce device event', ACTION, SOURCE, MSG.source)

			DEVICE = SOURCE['device']

			TIME = MSG.kwargs.get('time', snap_time())

			if isinstance(DEVICE, ENV.SnapDevicePointer):

				POINTER = DEVICE

				POSITION = POINTER.get('position') or []
				BUTTONS = POINTER.get('buttons') or []
				WHEELS = POINTER.get('wheels') or []

				wheel_axes = [s for w in WHEELS for s in w] # TODO better design...

				name = SOURCE['name']
				if SOURCE in POSITION and name in ('x','y'):

					# motion event:
					# TODO this just updates a position, and then on redraw we do the lookup?  or decide a frame rate for update/render separately and do the lookup on update?
					# TODO just connect to mainloop refresh?  then do lookup at pointer position...
					#	-- button presses are queued?  so one lookup is done on refresh, and that is the position (if button is released before lookup then it is cancelled?  or still send on/off for each press...)
					#	-- mainloop can just flag if lookup is 'dirty' -- scene has been updated or device event has occurred...  particularly motion...
					"""
					1. lookup graphic under new position (if position has changed)
					2. if graphic is different then emit leave proximity to previous, and enter proximity to new
						-- assign the graphic to the interact of the position
					send motion event to the graphic
					send motion event to the window (if graphic doesn't handle it?)
					"""

					# TODO delta should be cleared in mainloop?  or clear here after sending event?
					DELTA = SOURCE['delta']
					if DELTA is None:
						ENV.snap_debug('no change in motion event', ACTION, SOURCE)
						return None # no change

					self._update_pointer_interaction(POINTER, is_pointer_motion=True)


				elif ACTION == 'press' and SOURCE in BUTTONS:
					#ENV.snap_out('unhandled pointer button event', ACTION, SOURCE)

					BUTTON = SOURCE

					POSITION = POINTER.get('position')
					X,Y = POSITION.get('x'), POSITION.get('y')

					# we want the active graphic currently under the mouse
					position_interact_info = POSITION['interact_info'] or {}
					#ENV.snap_out('press position interact info', position_interact_info)
					#position_lookup_result = position_interact_info.get('lookup_result') or {}
					#if position_lookup_result:
					#	ENV.snap_warning('position lookup result!', position_lookup_result)
					#position_graphic = position_lookup_result.get('graphic') # XXX TODO this is now reverse(lookup_results) until handled...

					position_window = position_interact_info.get('window')
					lookup_results = position_interact_info.get('lookup_results') or []

					button_interact_info = BUTTON['interact_info'] or {}
					button_lookup_result = button_interact_info.get('lookup_result') or {}
					button_graphic = button_lookup_result.get('graphic')
					button_window = button_interact_info.get('window')

					"""
					get window and lookup_results from position (assign to own interact_info -- warn if existing)
					if lookup_results:
						send to device_event of the graphic and if return is True then break	
					"""

					BUTTON['interact_info'] = dict(window=position_window, lookup_results=lookup_results, lookup_result=None)

					if position_window is None:
						#if position_graphic is not None:
						#	ENV.snap_warning('graphic but no window for press event?')
						return None

					window_local_pos = snap_vector_t(X['value'] or 0, Y['value'] or 0, 0, 0)
					win_inv_matrix = snap_matrix_t(*position_window['matrix'])
					snap_matrix_invert(win_inv_matrix, win_inv_matrix)
					snap_matrix_transform_point(win_inv_matrix, window_local_pos, 0, window_local_pos)

					if button_graphic is not None:
						# send release event?
						ENV.snap_warning('BUTTON has graphic on press?')

					if button_window is not None:
						# send release event
						ENV.snap_warning("BUTTON has window on press?")

					for lookup_result in reversed(lookup_results):
						graphic = lookup_result['graphic']
						offset = lookup_result['offset']

						graphic_local_pos = snap_vector_t(0,0,0)
						position_graphic_offset = offset#position_interact_info['graphic_offset']
						snap_matrix_transform_point(position_graphic_offset, window_local_pos, 0, graphic_local_pos)

						if graphic.device_event(action='press', local_position=graphic_local_pos[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=SOURCE) is True:
							BUTTON['interact_info'] = dict(lookup_result=lookup_result)
							break
					else:
						# graphic did not accept the event, send to window
						BUTTON['interact_info'] = dict(lookup_result=None)#, graphic_offset=None)
						if position_window is not None: # XXX TODO and position_window is not position_graphic:
							# NOTE: if window responds to lookup() then it can use lookup_result system as it should be in the graphic results...
							position_window.device_event(action='press', local_position=window_local_pos[:2], lookup_result=None, time=TIME, device=POINTER, source=SOURCE)
							BUTTON['interact_info'] = dict(lookup_result=dict(graphic=position_window, offset=snap_matrix_t(*SNAP_IDENTITY_MATRIX)), window=position_window)
						else:
							BUTTON['interact_info'] = dict(window=None, lookup_result=None, lookup_results=None)


				elif ACTION == 'release' and SOURCE in BUTTONS:
					#ENV.snap_out('unhandled pointer button event', ACTION, SOURCE)

					BUTTON = SOURCE

					button_interact_info = BUTTON['interact_info'] or {}

					# TODO keep graphic assign, assign the active graphic once graphic accepts event?
					lookup_result = button_interact_info.get('lookup_result') or {}
					active_graphic = lookup_result.get('graphic')
					active_graphic_offset = lookup_result.get('offset')
					active_window = button_interact_info.get('window')
					#subresults = (button_interact_info.get('lookup_results') or [])[1:]

					BUTTON['interact_info'] = dict(
						window=None, lookup_results=None, lookup_result=None,
						#graphic=None, graphic_offset=None,
						#graphic_local_position=None, graphic_local_delta=None,
						#window_local_position=None, window_local_delta=None,
					)

					POSITION = POINTER.get('position')
					X,Y = POSITION.get('x'), POSITION.get('y')

					window_local_pos = snap_vector_t(X['value'] or 0, Y['value'] or 0, 0, 0)
					win_inv_matrix = snap_matrix_t(*active_window['matrix']) if active_window is not None else snap_matrix_t(*SNAP_IDENTITY_MATRIX)
					snap_matrix_invert(win_inv_matrix, win_inv_matrix)
					snap_matrix_transform_point(win_inv_matrix, window_local_pos, 0, window_local_pos)

					if active_graphic is not None:
						graphic_local_pos = snap_vector_t(0,0,0)
						snap_matrix_transform_point(active_graphic_offset, window_local_pos, 0, graphic_local_pos)
						active_graphic.device_event(action="release", local_position=graphic_local_pos[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=SOURCE)

					if active_window is not None and active_window is not active_graphic:
						active_window.device_event(action="release", local_position=window_local_pos[:2], lookup_result=None, time=TIME, device=POINTER, source=SOURCE)


				elif ACTION == 'motion' and SOURCE in wheel_axes:
					#ENV.snap_warning('unhandled pointer wheel event', ACTION, SOURCE)

					WHEEL = SOURCE

					POSITION = POINTER.get('position')

					interact_info = POSITION['interact_info'] or {}
					lookup_results = interact_info.get('lookup_results', [])
					active_window = interact_info.get('window')

					for lookup_result in reversed(lookup_results):
						# TODO include local position and local delta
						if lookup_result['graphic'].device_event(action='scroll', lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=WHEEL) is True:
							break
					else:
						# send to window if no graphic accepted the event
						if active_window is not None:
							# TODO include local position and local delta
							active_window.device_event(action='scroll', lookup_result=None, time=TIME, device=POINTER, source=WHEEL)

				else:
					ENV.snap_debug('unhandled pointer event', ACTION, SOURCE)
					

			elif isinstance(DEVICE, ENV.SnapDeviceKeyboard):
				#ENV.snap_out('unhandled keyboard event', ACTION, SOURCE)

				# TODO just forward to user window?  indicate local?  propagate if not return True?
				# TODO active window is ['windows'][-1] (on top) # TODO make sure it is on pointer events...

				open_windows = self['windows']
				if open_windows:
					# TODO maintain active_window at front of list
					active_window = open_windows[0]
					user_window = active_window['__user_window__']
					user_window.device_event.__direct__(MSG)

			else:
				ENV.snap_debug('unknown device event?', ACTION, SOURCE)


		def _update_pointer_interaction(self, POINTER, is_pointer_motion=False):
			return snap_gui_update_pointer_interaction(self, POINTER, is_pointer_motion=is_pointer_motion)


		def _window_at_position(self, GLOBAL_X, GLOBAL_Y):
			#(self, global_x, global_y):
			# TODO lookup window that is front and under mouse (walk _open_windows_ list backward?)

			for window in reversed(self['windows']):

				#ENV.snap_out('window', window)

				# TODO window extents represent real window position? (was _gui_window_extents_)
				ext = window['extents']
				mat = window['matrix']
				if not (ext and mat):
					ENV.snap_warning("no extents on gui window!", ext, mat)
					continue

				#ENV.snap_out('check window', window, mat[:], ext[:])

				# now check if position is inside window bounds
				if GLOBAL_X > mat[3] and GLOBAL_X < mat[3] + ext[3] and \
					GLOBAL_Y > mat[7] and GLOBAL_Y < mat[7] + ext[4]:

					# is inside window
					return window

			return None


		def _map_local_to_graphic_offset(self, offset, local_position, local_delta, GRAPHIC_POSITION, GRAPHIC_DELTA):
			# XXX this should just be using SnapMatrix().transform_point(...)

			#offset,local_position,local_delta, graphic_position, graphic_delta = MSG.unpack(
			#	'offset',None, 'local_position',None, 'local_delta',None, 'graphic_position',None, 'graphic_delta',None)

			inverse_offset = snap_matrix_t()

			snap_matrix_invert(offset, inverse_offset)

			if local_position:
				snap_matrix_transform_point(inverse_offset, local_position, 1, GRAPHIC_POSITION)

			if local_delta:
				snap_matrix_transform_point(inverse_offset, local_delta, 0, GRAPHIC_DELTA)
			
			return None

		def WindowXXX(self, *a, **k):
			# TODO make this an assign of the gui window base class, and access the gui in the window?  window can register itself in gui windows...
			#	-- assign Window to gui base, and when gui is __init__ it can assign it's instance to the local Window assignment so window can see it...

			window_base = self['__window_type__']
			assert window_base is not None, 'no __window_type__ assigned to gui; cannot create new window'

			window = window_base(*a, **k)

			open_windows = self.__snap_data__['__open_windows__']
			if open_windows is None:
				open_windows = []
			open_windows.append(window)
			self.__snap_data__['__open_windows__'] = open_windows
			#snap_listen(window, self) # XXX TODO?
			
			return window

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self)

			self.Window.GUI = self

			#data['name'] = None
			#data['version'] = None
			self.__snap_data__['__window_type__'] = None # base class should assign this to be the gui window base class (uninstantiated)
			self.__snap_data__['__open_windows__'] = []
			self['interaction'] = None # SnapInteraction_event manager of device interactions (clicks, drags, motions, ...)

			if DEVICES:
				# XXX connect this outside of the gui?  XXX initialize it in gui, and make the interface a component of the gui?
				# listens to the whole category...
				if 1:
					POINTER = DEVICES['pointer'] # XXX TODO 
					KEYBOARD = DEVICES['keyboard']
					POINTER.device_event.listen(self.device_event)
					KEYBOARD.device_event.listen(self.device_event)

				#SnapObject INTERACTION = SnapObject_create(SNAP_ENV, SnapInteraction_event); // assign GUI?
				#snap_setattrs_SnapObjects(self, "INTERACTION", INTERACTION);

			# TODO keyboard and pointer event filter, processing events and forwarding them to user if applicable...

		def __del__(self):

			for window in self['__open_windows__']:
				window.changed.ignore(self.changed)
			del self.__snap_data__['__open_windows__']

			#return SnapNode.__delete__(self)



	ENV.SnapGuiBase = SnapGuiBase


