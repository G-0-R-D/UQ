
#from snap.lib.core import *

#from snap.lib.gui import SnapGuiWindowBase as SnapGuiWindowBaseModule
#from snap.lib.os.devices.SnapDeviceInteraction import *

def build(ENV):

	ENV.__build__('snap.lib.gui.SnapGuiWindowBase')

	SnapNode = ENV.SnapNode

	SnapMessage = ENV.SnapMessage

	snap_matrix_t = ENV.snap_matrix_t
	snap_extents_t = ENV.snap_extents_t
	snap_vector_t = ENV.snap_vector_t
	snap_matrix_transform_point = ENV.snap_matrix_transform_point
	snap_matrix_map_extents = ENV.snap_matrix_map_extents
	snap_matrix_invert = ENV.snap_matrix_invert
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX

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

		@property
		def MAINWINDOW(self):
			windows = ENV.GUI['windows']
			assert windows, 'no mainwindow'
			if len(windows) > 1:
				ENV.snap_warning('MAINWINDOW access with > 1 window')
			return windows[0] # mainwindow will always be first created...

		@property
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
				ENV.snap_out('keyboard event', ACTION, SOURCE)

				# TODO objects can just register/unregister themselves with keyboard interact_info?

				KEYBOARD = DEVICE

				if ACTION == 'press':
					'handle press'

				elif ACTION == 'release':
					'handle release'

				# TODO Text event?  action='text_entry'

				else:
					ENV.snap_debug('unknown keyboard event', ACTION, SOURCE)

			else:
				ENV.snap_debug('unknown device event?', ACTION, SOURCE)


		def _update_pointer_interaction(self, POINTER, is_pointer_motion=False):
			# called for each pointer when it is moved, and all pointers when scene is updated (animated) to update what is under the pointer (if anything)

			# TODO send event to window with local window coordinates, and lookup list (just the graphics)
			#	-- if return True it is handled, stop, otherwise start sending to each graphic in local coordinates with list of sub-graphics...
			#	-- so at the top level we are mapping the coordinates directly into the graphic_offset, but locally they just map to the child...
			#	-- TODO send interaction events from top lookup_results[-1] backwards, so what is in front gets the event first?  if it returns True then it stops, otherwise it keeps going?
			#		-- send to window first, and continue if return is not True?

			# TODO just send lookup[-1] and backwards, and THEN the window after if none of them handled!  do the reverse!
			#	-- how to handle proximity?  store the whole list?  notify to each unless someone handles?  or just notify all that change, use set()?
			#	-- or maybe proximity change means event sends to new one?  otherwise it keeps sending to existing one?  as long as it is still in lookup results?  so accept (return True) on the proximity event to 'register' as the active_graphic?

			TIME = snap_time()

			if POINTER is None:
				POINTER = ENV.DEVICES['pointer'] # default pointer

			if POINTER is None:
				ENV.snap_error('no pointer for interaction update')
				return

			'map the position into the window matrix'

			'do lookup on the window'

			'if window or graphic changed then send proximity events (enter/exit)'
			'if buttons pressed or released then send those events'
			'send motion event to active graphic if the mouse has moved'
			'if graphic doesnt absorb the motion event, then also send it to the window (and user != graphic to prevent double send)'

			# if mouse moved or scene updated then we do lookup and emit motion event if it is a mouse move
			# if button presses/releases then send them all
			# TODO XXX this means that button press / release can just be sent immediately to active graphic/window...
			# update and pointer motion trigger lookup...  so that's here?
			#	-- but we need to make sure the button events go to the right graphic (the active one), so if that is deferred in a separate mainloop callback that might not work -- let's just make an operator function to handle the motion update and call it from mouse or scene update events...

			# flag mouse motion as dirty (then get from mouse, just use latest position)
			# flag button presses (keep list of press and releases for all buttons, send them all)
			# flag scene update as dirty, as motion?  so if something is animated under the mouse it will register...

			# TODO send proximity events for all lookup graphics...  TODO use mouse enter/leave in gui to send proximity for window...

			POSITION = POINTER.get('position')
			X = POSITION.get('x')
			Y = POSITION.get('y')

			interact_info = POSITION['interact_info'] or {}
			previous_lookup_results = interact_info.get('lookup_results') or []

			previous_window = interact_info.get('window')
			#current_graphic = interact_info.get('graphic')
			#current_graphic_offset = interact_info.get('graphic_offset')

			active_window = self._window_at_position(X['value'], Y['value'])

			POSITION['interact_info'] = dict(window=active_window)

			if active_window is None:
				# send proximity out to all current results and current window
				for lookup_result in reversed(previous_lookup_results):
					graphic = lookup_result['graphic']
					# no handling, send to all
					graphic.device_event(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION)
				if previous_window is not None:
					previous_window.device_event(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION)

				POSITION['interact_info'] = dict(lookup_results=None)
			else:


				win_local_pos = snap_vector_t(X['value'] or 0, Y['value'] or 0, 0, 0)
				win_local_delta = snap_vector_t(X['delta'] or 0, Y['delta'] or 0, 0, 0)

				win_inv_matrix = snap_matrix_t(*active_window['matrix'])
				snap_matrix_invert(win_inv_matrix, win_inv_matrix)
				snap_matrix_transform_point(win_inv_matrix, win_local_pos, 0, win_local_pos)
				snap_matrix_transform_point(win_inv_matrix, win_local_delta, 1, win_local_delta)

				l_img = lookup_image()
				lookup_results = ENV.GRAPHICS.do_lookup(image=l_img, x=win_local_pos[0], y=win_local_pos[1], items=active_window['__user_window__']['render_items'])#, offset=m)

				POSITION['interact_info'] = dict(lookup_results=lookup_results)

				'do lookup and send proximity events accordingly...'
				if active_window is not previous_window:

					# send proximity to all, no handling

					for lookup_result in reversed(previous_lookup_results):
						# no handling, send to all
						lookup_result['graphic'].device_event(action='proximity', state=False, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION)
					if previous_window is not None:
						previous_window.device_event(action='proximity', state=False, lookup_result=None, time=TIME, device=POINTER, source=POSITION)

					for lookup_result in reversed(lookup_results):
						lookup_result['graphic'].device_event(action='proximity', state=True, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION)
					active_window.device_event(action='proximity', state=True, lookup_result=None, time=TIME, device=POINTER, souce=POSITION)
				else:
					# NOTE: windows are same here, so only need to process the graphics...
					# new = set(lookup_results) - set(previous_lookup_results)
					# old = set(previous_lookup_results) - set(lookup_results)
					set_lookup_results = set([id(r['graphic']) for r in lookup_results])
					set_previous_lookup_results = set([id(r['graphic']) for r in previous_lookup_results])

					for lookup_result in reversed(previous_lookup_results):
						graphic = lookup_result['graphic']
						if id(graphic) in set_lookup_results:
							continue
						graphic.device_event(action='proximity', state=False, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION)

					for lookup_result in reversed(lookup_results):
						graphic = lookup_result['graphic']
						if id(graphic) in set_previous_lookup_results:
							continue
						graphic.device_event(action='proximity', state=True, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION)

				if is_pointer_motion:

					window_in_graphics = False

					gfx_local_pos = snap_vector_t(*win_local_pos)
					gfx_local_delta = snap_vector_t(*win_local_delta)
					for lookup_result in reversed(lookup_results):
						#ENV.snap_out('motion lookup result', lookup_result)
						graphic = lookup_result['graphic']
						offset = lookup_result['offset']
						snap_matrix_transform_point(offset, gfx_local_pos, 0, gfx_local_pos)
						snap_matrix_transform_point(offset, gfx_local_delta, 1, gfx_local_delta)

						window_in_graphics = window_in_graphics or graphic is active_window

						if graphic.device_event(action='motion', local_position=gfx_local_pos[:2], local_delta=gfx_local_delta[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION) is True:
							break

					else:
						if not window_in_graphics:
							active_window.device_event(action='motion', local_position=win_local_pos[:2], local_delta=win_local_delta[:2], lookup_result=None, time=TIME, device=POINTER, source=POSITION)

				else:
					# TODO maybe also send a different event when it's the scene that has changed?  notify of mouse position update?
					pass


			if is_pointer_motion:
				# send drag event to any graphic or window currently assigned to the interact_info of each button
				for BUTTON in (POINTER.get('buttons') or []):

					interact_info = BUTTON['interact_info']

					if not interact_info:
						continue

					window = interact_info.get('window')
					lookup_result = interact_info.get('lookup_result') or {}
					graphic = lookup_result.get('graphic')

					win_local_pos = snap_vector_t(X['value'] or 0, Y['value'] or 0, 0, 0)
					win_local_delta = snap_vector_t(X['delta'] or 0, Y['delta'] or 0, 0, 0)
					if window is None:
						ENV.snap_warning('no window on button drag event')
					else:
						win_inv_matrix = snap_matrix_t(*window['matrix'])
						snap_matrix_invert(win_inv_matrix, win_inv_matrix)
						snap_matrix_transform_point(win_inv_matrix, win_local_pos, 0, win_local_pos)
						snap_matrix_transform_point(win_inv_matrix, win_local_delta, 1, win_local_delta)

					handled = False

					if graphic is not None:
						graphic_offset = lookup_result['offset']

						gfx_local_pos = snap_vector_t(*win_local_pos)
						gfx_local_delta = snap_vector_t(*win_local_delta)
						snap_matrix_transform_point(graphic_offset, gfx_local_pos, 0, gfx_local_pos)
						snap_matrix_transform_point(graphic_offset, gfx_local_delta, 1, gfx_local_delta)

						handled = graphic.device_event(action='drag', local_position=gfx_local_pos[:2], local_delta=gfx_local_delta[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=BUTTON)

					if handled is not True and window is not None and window is not graphic:
						window.device_event(action='drag', local_position=win_local_pos[:2], local_delta=win_local_delta[:2], lookup_result=None, time=TIME, device=POINTER, source=BUTTON)


			#return None
			# XXX ---- DONE -----
				"""

			if not is_pointer_motion:
				# scene update, just send proximity events to graphics if they change under pointer
				# TODO clear delta on pointer?

				'' # TODO just do lookup if active window to see if active_graphic has changed...
				if current_window is None:
					return

				'do lookup on window to see if graphic has changed'

				'if graphic has changed send proximity in/out and update interact info'

			else:

				# TODO notify proximity change to set() of lookup results and last active window (in and out for all that are different...)
				# TODO then send motion event from top of lookup results to bottom (or window if not handled)

				#ENV.snap_out('get window at position', active_window, [X['value'], Y['value']])

				# first update the interact information
				if active_window is not None:

					#ENV.snap_out("win_local_pos before", win_local_pos[:], win_local_delta[:])

					#ENV.snap_out("win_local_pos after", win_local_pos[:], win_local_delta[:])





					gfx_local_pos = snap_vector_t(*win_local_pos)
					gfx_local_delta = snap_vector_t(*win_local_delta)

					#camera = active_window['camera'] or SnapCamera()
					#m = camera['render_matrix']

					#ENV.snap_out('do lookup', win_local_pos[:])

					active_graphic = lookup_results[0].graphic if lookup_results else None
					active_graphic_offset = lookup_results[0].offset if lookup_results else None

					#ENV.snap_out("find graphic at", active_graphic, win_local_pos[:])
					
				else:
					d = dict(window_local_position=None, window_local_delta=None)
					if current_window is not None:
						d['window'] = None
					POSITION['interact_info'] = d

					active_graphic = None
					active_graphic_offset = None
					lookup_results = []

				#subresults = lookup_results[1:]

				# TODO first do set comparison of lookup results of position vs last time
				# TODO then send motion event from top to bottom until handled or to window

				# XXX position just has lookup results, and send proximity events to all that change (set comparison)
				#	-- otherwise send from top to bottom until handled, or send to window
				if active_graphic is not None:
					snap_matrix_transform_point(active_graphic_offset, gfx_local_pos, 0, gfx_local_pos)
					snap_matrix_transform_point(active_graphic_offset, gfx_local_delta, 1, gfx_local_delta)
					POSITION['interact_info'] = dict(graphic=active_graphic, graphic_offset=active_graphic_offset,
						graphic_local_position=gfx_local_pos[:2], graphic_local_delta=gfx_local_delta[:2],
						lookup_results=lookup_results)
				else:
					d = dict(graphic_local_position=None, graphic_local_delta=None)
					if current_graphic is not None:
						d['graphic'] = None
						d['graphic_offset'] = None
						d['lookup_results'] = None
					POSITION['interact_info'] = d

				if active_graphic is not current_graphic:

					if current_graphic is not None:
						current_graphic.device_event(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION)

					if active_graphic is not None:
						active_graphic.device_event(action='proximity', state=True, time=TIME, device=POINTER, source=POSITION)

				if active_graphic is not None:
					active_graphic.device_event(action='motion', local_position=gfx_local_pos[:2], local_delta=gfx_local_delta[:2], time=TIME, device=POINTER, source=POSITION)

				if active_window is not current_window and active_window is not active_graphic:

					if current_window is not None:
						current_window.device_event(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION)

					if active_window is not None:
						active_window.device_event(action='proximity', state=True, time=TIME, device=POINTER, source=POSITION)

				if active_window is not None and active_window is not active_graphic:
					active_window.device_event(action='motion', local_position=win_local_pos[:2], local_delta=win_local_delta[:2], time=TIME, device=POINTER, source=POSITION)
				"""




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

			#offset,local_position,local_delta, graphic_position, graphic_delta = MSG.unpack(
			#	'offset',None, 'local_position',None, 'local_delta',None, 'graphic_position',None, 'graphic_delta',None)

			inverse_offset = snap_matrix_t()

			snap_matrix_invert(offset, inverse_offset)

			if local_position:
				snap_matrix_transform_point(inverse_offset, local_position, 1, GRAPHIC_POSITION)

			if local_delta:
				snap_matrix_transform_point(inverse_offset, local_delta, 0, GRAPHIC_DELTA)
			
			return None

		def Window(self, *a, **k):

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


