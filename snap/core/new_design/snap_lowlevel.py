
def build(ENV):

	# these are low-level calls which bypass the creation of BoundChannel types...
	# (for when you know what you're doing and speed matters)

	SnapMessage = ENV.SnapMessage

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
			return listeners.send(self, CHANNEL_NAME, MSG)
		return None

	ENV.snap_send_msg = snap_send_msg

	def snap_send(self, CHANNEL_NAME, *a, **k):
		return snap_send_msg(self, CHANNEL_NAME, SnapMessage(*a, **k))

	ENV.snap_send = snap_send

	def snap_emit_msg(self, CHANNEL_NAME, MSG):

		listeners = getattr(self, '__snap_listeners__', None)
		if listeners is not None and CHANNEL_NAME in listeners.channels:

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


	# properties

	# these bypass the creation of the bound channel for efficiency...

	def snap_prop_get(self, PROP_NAME, MSG):
		getter = getattr(getattr(self.__class__, PROP_NAME), 'get')
		return getter(self, MSG)

	ENV.snap_prop_get = snap_prop_get

	def snap_prop_set(self, PROP_NAME, MSG):
		setter = getattr(getattr(self.__class__, PROP_NAME), 'set')
		return setter(self, MSG)

	ENV.snap_prop_set = snap_prop_set

	def snap_prop_delete(self, PROP_NAME, MSG):
		delete = getattr(getattr(self.__class__, PROP_NAME), 'delete')
		return delete(self, MSG)

	ENV.snap_prop_delete = snap_prop_delete

