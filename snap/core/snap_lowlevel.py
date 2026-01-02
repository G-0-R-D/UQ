
def build(ENV):

	# these are low-level calls which bypass the creation of BoundChannel types...
	# (for when you know what you're doing and speed matters)

	SnapMessage = ENV.SnapMessage
	DUMMY_MSG = SnapMessage()

	def snap_ignore(self, OUTPUT_CHANNEL_NAME, LISTENER, INPUT_CHANNEL_NAME):

		listeners = getattr(self, '__snap_listeners__', None)
		if listeners is None:
			return None

		listeners.disconnect(OUTPUT_CHANNEL_NAME, LISTENER, INPUT_CHANNEL_NAME)

		if listeners.unused():
			delattr(self, '__snap_listeners__')

		return None

	ENV.snap_ignore = snap_ignore

	def snap_listen(self, OUTPUT_CHANNEL_NAME, LISTENER, INPUT_CHANNEL_NAME, converter=None):

		assert isinstance(OUTPUT_CHANNEL_NAME, str) and isinstance(INPUT_CHANNEL_NAME, str), 'channels must be strings'

	
		listeners = getattr(self, '__snap_listeners__', None)
		if listeners is None:
			listeners = self.__snap_listeners__ = ENV.SnapNodeListeners()

		return listeners.connect(OUTPUT_CHANNEL_NAME, LISTENER, INPUT_CHANNEL_NAME, converter)

	ENV.snap_listen = snap_listen

	def snap_send_msg(self, CHANNEL_NAME, MSG):
		listeners = getattr(self, '__snap_listeners__', None)
		if listeners is not None:
			if MSG is None:
				MSG = DUMMY_MSG
			return listeners.send(self, CHANNEL_NAME, MSG)
		return None

	ENV.snap_send_msg = snap_send_msg

	def snap_send(self, CHANNEL_NAME, *a, **k):
		return snap_send_msg(self, CHANNEL_NAME, SnapMessage(*a, **k))

	ENV.snap_send = snap_send

	def snap_emit_msg(self, CHANNEL_NAME, MSG):

		listeners = getattr(self, '__snap_listeners__', None)
		if listeners is not None and CHANNEL_NAME in listeners.channels:

			if MSG is None:
				MSG = DUMMY_MSG

			try:
				ENV.__snap_queue_send__(self, CHANNEL_NAME, MSG)
			except:
				ENV.snap_warning('ENV cannot queue send (emit)?')
				snap_send_msg(self, CHANNEL_NAME, MSG)

		return None

	ENV.snap_emit_msg = snap_emit_msg

	def snap_emit(self, CHANNEL_NAME, *a, **k):
		return snap_emit_msg(self, CHANNEL_NAME, SnapMessage(*a, **k))

	ENV.snap_emit = snap_emit

	def snap_call_msg(self, CHANNEL_NAME, MSG):
		# bypasses SnapBoundChannel creation...
		return getattr(self.__class__, CHANNEL_NAME)(self, MSG if MSG is not None else DUMMY_MSG)

	ENV.snap_call_msg = snap_call_msg

	def snap_call(self, CHANNEL_NAME, *a, **k):
		return snap_call_msg(self, CHANNEL_NAME, SnapMessage(*a, **k))

	ENV.snap_call = snap_call


	# properties

	# these bypass the creation of the bound channel for efficiency...

	# XXX these have been deprecated, __getitem__, __setitem__, __delitem__ have been optimized to do something more like this anyway...
	"""
	def snap_prop_get(self, PROP_NAME, MSG):
		prop = getattr(self.__class__, PROP_NAME, None)
		if prop is not None:
			return getattr(prop, 'get')(self, MSG)
		return None

	#ENV.snap_prop_get = snap_prop_get

	def snap_prop_set(self, PROP_NAME, MSG):
		setter = getattr(getattr(self.__class__, PROP_NAME), 'set')
		return setter(self, MSG)

	#ENV.snap_prop_set = snap_prop_set

	def snap_prop_delete(self, PROP_NAME, MSG):
		prop = getattr(self.__class__, PROP_NAME, None)
		if prop is not None:
			return getattr(prop, 'delete')(self, MSG)
		return None

	#ENV.snap_prop_delete = snap_prop_delete
	"""
