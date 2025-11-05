
def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_time = ENV.snap_time

	class SnapMediaPlayer(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class ready: # TODO emit when ready?
			# this is primed at end of refresh (returns True if all open queues have atleast 1 frame)

			def get(self, MSG):
				"""()->bool"""
				if self.__snap_data__['ready']:
					return True

				# TODO check open stream queues to make sure each has atleast 1 frame

		@ENV.SnapProperty
		class playing: # TODO emit on playing

			def get(self, MSG):
				"""()->bool"""

			def set(self, MSG):
				"""(bool!)"""
				if MSG.args[0]:
					'set playing' # TODO
				else:
					'set paused' # TODO

		@ENV.SnapProperty
		class finished: # TODO finished.emit() when playback complete...

			def get(self, MSG):
				'' # TODO report True if we are at end...
				# TODO True if not playing, or if reader is at the end and the stream buffers are empty
				if self['playing']:
					return False

				media_reader = self.__snap_data__['media_reader']
				if media_reader:
					return media_reader['finished']

				return True # not playing or reading = finished

		@ENV.SnapProperty
		class duration:

			def get(self, MSG):
				"""()->float"""
				media_reader = self.__snap_data__['media_reader']
				if media_reader:
					return media_reader['duration'] or 0.
				return 0.


		@ENV.SnapProperty
		class filepath:

			def get(self, MSG):
				"""()->str"""
				return self.__snap_data__['filepath']

			def set(self, MSG):
				"""(str!)"""
				filepath = MSG.args[0]
				if filepath:
					'open'
				else:
					'close'
				self.__snap_data__['filepath'] = filepath


		@ENV.SnapProperty
		class frame:

			def get(self, MSG):
				"""()->int"""
				# current frame number
				return 0

			def set(self, MSG):
				'' # TODO treat this as seek by frame?

		@ENV.SnapProperty
		class time:

			def get(self, MSG):
				"""()->float"""
				return self.__snap_data__['time'] or 0.

			def set(self, MSG):
				'' # TODO treat this as seek by time?

				"""
				#snap_out("elapsed", elapsed)
				if elapsed < .25:
					# TODO check elapsed size, if large (got held up) then consider SEEK as well?
					self._current_time_ += elapsed # advance
					self._last_time_ = t

				else:
					# big jump, just keep playing from same place?
					self._last_time_ = None
					self._ready_ = False
					return self.seek(seconds=self._current_time_)
				"""	
				if self['time'] >= self['duration']:
					# finished playing (reached end)
					self.stop() # could also "PAUSE"
					ENV.snap_out("finished")
					self.finished.emit()#snap_emit(self, "FINISHED") # specifically means we played until the end
					return None

		@ENV.SnapProperty
		class position:
			# normalized time from 0.0 -> 1.0

			def get(self, MSG):
				"""()->float"""
				try:
					return self.__snap_data__['time'] / self['duration']
				except ZeroDivisionError:
					return 0.

			def set(self, MSG):
				'' # TODO seek by position (0.0 -> 1.0)
				# greater or less than 0/1 is ValueError
				# duration 0 and position > 0 is IndexError


		@ENV.SnapChannel
		def device_event(self, MSG):
			'' # TODO

		@ENV.SnapChannel
		def process(self, MSG):
			# advance position, buffer next

			# TODO we want to support both directions, at any rate...

			reader = self.__snap_data__['media_reader']
			if reader is None:
				ENV.snap_debug('no reader in {}'.format(self.__class__.__name__))
				return

			# attempt to advance frame
			if not self['playing']:
				self.__snap_data__['__last_time__'] = None
				self.__snap_data__['ready'] = False

			elif not self['ready']:
				self.__snap_data__['__last_time__'] = False

			elif self.__snap_data__['__last_time__'] is None:
				self.__snap_data__['__last_time__'] = snap_time()

			else:
				# playing and ready with time, start advancing
				last_time = self.__snap_data__['__last_time__']
				t = snap_time()
				elapsed = t - last_time

				self.__snap_data__['__last_time__'] = t

				self['time'] += elapsed # advance (by using time.set() to seek)

			# load frame buffers # TODO queue the frames on the reader streams...
			call_again_immediately = False
			room_for_more = True

			

		@ENV.SnapChannel
		def timeout(self, MSG):
			self.process()




		@ENV.SnapChannel
		def pause(self, MSG):
			"""()"""
			if self.__snap_data__['playing']:
				self.__snap_data__['playing'] = False
				self.pause.emit()

		@ENV.SnapChannel
		def play(self, MSG):

			if not self.__snap_data__['playing']:
				ENV.TIMERS.start(self.timeout, seconds=0., repeat=True)
				self.__snap_data__['playing'] = True

			self.__snap_data__['buffering'] = True # TODO?

		@play.shared
		def start(self, MSG): pass

		@ENV.SnapChannel
		def stop(self, MSG):
			''

		@stop.shared
		def close(self, MSG): pass # TODO or is this stop and then clear filepath?

			


		@ENV.SnapChannel
		def allocate(self, MSG):
			return SnapContainer.allocate(self, MSG)
		

		@ENV.SnapChannel
		def seek(self, MSG):
			'' # TODO support time or frame + or -...
		


		@ENV.SnapProperty
		class screen:

			def get(self, MSG):
				'' # TODO visual for player if used (or surface for audio visualizations if that is enabled)

		@ENV.SnapProperty
		class controls:

			def get(self, MSG):
				'' # TODO gui player controls, if used

		# TODO settings?  visualization=True|False, ...?  TODO how to select visualizer?

		@ENV.SnapChannel
		def draw(self, MSG):
			return SnapContainer.draw(self, MSG)


		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self)

			# TODO init view render with screen image...  TODO make it hideable when video not present?  render as black square


			

	ENV.SnapMediaPlayer = SnapMediaPlayer
	return SnapMediaPlayer
