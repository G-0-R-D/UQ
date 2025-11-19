class FPSTracker(object):
	
	def __init__(self, snap_time_func):
		self.snap_time = snap_time_func
		self.last_frame_time = None
		self.fps = 0.0
	
	def update(self):
		current_time = self.snap_time()
		if self.last_frame_time is not None:
			delta = current_time - self.last_frame_time
			if delta > 0:
				self.fps = 1.0 / delta
		self.last_frame_time = current_time
		return self.fps
	
	def reset(self):
		self.last_frame_time = None
		self.fps = 0.0
