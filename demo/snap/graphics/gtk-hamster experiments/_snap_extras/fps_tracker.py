class FPSTrackerXXX(object):
	
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


class FPSTracker(object):

	def __init__(self, time_func):
		self.time = time_func
		self.last_time = time_func()
		self.report = [] # average for more stable feedback
		self.interval = 1 # second(s)

	def update(self):
		# compat with previous design so it works in-place
		self.fps = self.next()

	def next(self):
		current_time = self.time()
		elapsed = current_time - self.last_time
		self.last_time = current_time

		while sum(self.report) > self.interval:
			self.report.pop(0)
		self.report.append(elapsed)
		return sum([1./elapsed for elapsed in self.report]) / len(self.report)

