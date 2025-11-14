
def build(ENV):

	# this is for global time info, for better efficiency

	SnapNode = ENV.SnapNode

	snap_time_since_epoch = ENV.snap_time_since_epoch

	class SnapTimers(SnapNode):

		__slots__ = []

		# updated once per mainloop iteration... (efficient! yay!)
		CURRENT_TIME = snap_time_since_epoch()
		ELAPSED_TIME = 0

		@ENV.SnapChannel
		def UPDATE(self, MSG):
			""
			raise NotImplementedError("UPDATE is send() only")

		@ENV.SnapChannel
		def RENDER(self, MSG):
			""
			raise NotImplementedError("RENDER is send() only")

		@ENV.SnapChannel
		def fps_timeout(self, MSG):
			"()"
			self.UPDATE.send()

			GUI = getattr(ENV, 'GUI', None)
			DEVICES = getattr(ENV, 'DEVICES', None)
			if GUI is not None and DEVICES is not None:
				# TODO set a flag in device motion, if device is updated within frame we don't need to do it again!  set the flag back to false here...
				# TODO ENV.__PRIVATE__['__DEVICE_EVENT_THIS_FRAME__'] = False
				for pointer in DEVICES['pointers']:
					GUI._update_pointer_interaction(pointer, is_pointer_motion=False) # so animated elements can notify if they are under mouse after update...

			self.RENDER.send()

		def __init__(self):
			SnapNode.__init__(self)


	ENV.SnapTimers = SnapTimers
	ENV.TIMERS = SnapTimers()
