
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

	snap_time = ENV.snap_time

	SnapBoundChannel = ENV.SnapBoundChannel


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




	def snap_gui_send_event(GRAPHIC, MESSAGE):

		msg = SnapMessage()
		msg.kwargs = MESSAGE
		msg.source = ENV.GUI
		msg.channel = "device_event"

		device_event = getattr(GRAPHIC, 'device_event', None)
		if device_event:
			if isinstance(device_event, SnapBoundChannel):
				device_event = device_event.__direct__

			try:
				return device_event(msg)
			except Exception as e:
				ENV.snap_print_exception(e)

	ENV.snap_gui_send_event = snap_gui_send_event


	def snap_gui_update_pointer_interaction(GUI, POINTER, is_pointer_motion=False):
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
			POINTER = DEVICES['pointer'] # default pointer

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

		assert (POSITION is not None and X is not None and Y is not None), 'invalid pointer configuration?'

		interact_info = POSITION['interact_info'] or {}
		previous_lookup_results = interact_info.get('lookup_results') or []

		previous_window = interact_info.get('window')
		#current_graphic = interact_info.get('graphic')
		#current_graphic_offset = interact_info.get('graphic_offset')

		active_window = GUI._window_at_position(X['value'], Y['value'])

		POSITION['interact_info'] = dict(window=active_window)

		if active_window is None:
			# send proximity out to all current results and current window
			for lookup_result in reversed(previous_lookup_results):
				graphic = lookup_result['graphic']
				# no handling, send to all
				snap_gui_send_event(graphic, dict(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION))
			if previous_window is not None:
				snap_gui_send_event(previous_window, dict(action='proximity', state=False, time=TIME, device=POINTER, source=POSITION))

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
					snap_gui_send_event(lookup_result['graphic'], dict(action='proximity', state=False, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION))
				if previous_window is not None:
					snap_gui_send_event(previous_window, dict(action='proximity', state=False, lookup_result=None, time=TIME, device=POINTER, source=POSITION))

				for lookup_result in reversed(lookup_results):
					snap_gui_send_event(lookup_result['graphic'], dict(action='proximity', state=True, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION))

				snap_gui_send_event(active_window, dict(action='proximity', state=True, lookup_result=None, time=TIME, device=POINTER, source=POSITION))
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
					snap_gui_send_event(graphic, dict(action='proximity', state=False, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION))

				for lookup_result in reversed(lookup_results):
					graphic = lookup_result['graphic']
					if id(graphic) in set_previous_lookup_results:
						continue
					snap_gui_send_event(graphic, dict(action='proximity', state=True, lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION))

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

					if snap_gui_send_event(graphic, dict(action='motion', local_position=gfx_local_pos[:2], local_delta=gfx_local_delta[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=POSITION)) is True:
						break

				else:
					if not window_in_graphics:
						snap_gui_send_event(active_window, dict(action='motion', local_position=win_local_pos[:2], local_delta=win_local_delta[:2], lookup_result=None, time=TIME, device=POINTER, source=POSITION))

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

					handled = snap_gui_send_event(graphic, dict(action='drag', local_position=gfx_local_pos[:2], local_delta=gfx_local_delta[:2], lookup_result=lookup_result.copy(), time=TIME, device=POINTER, source=BUTTON))

				if handled is not True and window is not None and window is not graphic:
					snap_gui_send_event(window, dict(action='drag', local_position=win_local_pos[:2], local_delta=win_local_delta[:2], lookup_result=None, time=TIME, device=POINTER, source=BUTTON))


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
	ENV.snap_gui_update_pointer_interaction = snap_gui_update_pointer_interaction

