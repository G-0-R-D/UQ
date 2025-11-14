
#from snap.lib.core.SnapObject import *
#from snap.lib.core.SnapWeakref import *

from weakref import ref as weakref_ref

from types import FunctionType, MethodType, GeneratorType

# XXX just use a dict?
"""
typedef struct SnapTimers_timer_t {
	SnapObject NODE;
	any EVENT; // assigned as "TIMEOUT" unless specified
	double started; // time of timer initialization (never changes)
	double interval; // time from start that results in timeout
	double current; // current time of timer (starts at interval and is subtracted until < 0 and then reset)
	int repeat; // 1 if timer repeats, 0 if is deleted after use
} SnapTimers_timer_t;
"""


def build(ENV):

	SnapNode = ENV.SnapNode
	snap_time_since_epoch = ENV.snap_time_since_epoch

	SnapBoundChannel = ENV.SnapBoundChannel

	SnapMessage = ENV.SnapMessage

	def processing(TIMER):
		# this would be assigned to timer, just keep calling until done...?

		while 1:

			yield

			kwargs = {'elapsed':TIMER.elapsed, 'interval':TIMER.interval} if TIMER.with_arguments else {}

			NODE = TIMER.REF()
			if NODE is None:
				TIMER.processing = None
				return # complete

			#ENV.snap_out("NODE", NODE)

			if TIMER.channel is not None:
				#assert isinstance(NODE, SnapNode) # assume checks have already been done
				CALLABLE = getattr(NODE, TIMER.channel)
			else:
				CALLABLE = NODE

			#if isinstance(NODE, SnapNode):
			#	'get bound for channel'
			#	CALLABLE = getattr(NODE, TIMER.channel)

			if isinstance(CALLABLE, SnapBoundChannel):
				node,channel,method = CALLABLE.__data__
				if method is None:
					TIMER.processing = None
					return # if channel doesn't exist then there is nothing to call, but ignore silently?

				#ENV.snap_out('call channel', CALLABLE, node, channel)
				_return = CALLABLE(**kwargs)#.__direct__(MSG)
			#else:
			#	_return = CALLABLE(**kwargs)#MSG)

			elif isinstance(CALLABLE, (MethodType, FunctionType)):
				_return = CALLABLE(**kwargs)

			elif isinstance(CALLABLE, GeneratorType):
				ENV.snap_out('generator!')
				_return = CALLABLE # drop down

			else:
				raise TypeError(type(CALLABLE))

			#ENV.snap_out('drop', _return)

			if not isinstance(_return, GeneratorType):
				if TIMER.repeat:
					continue
				TIMER.processing = None
				return

			# if the method returns a generator type (uses yield) then we keep processing it until it is complete...
			# it is the user's job to make sure the processing does not take a long time
			# quit by returning from the generator

			while 1:
				
				try:
					next(_return)
				except StopIteration:
					TIMER.processing = None
					return # no error
				#except Exception as e:
				#	ENV.snap_error(node, channel, 'error >>')
				#	ENV.snap_print_exception(e)
				#	ENV.snap_print_stack()
				#	return

				yield


	class SnapTimerInternal(object):
		__slots__ = ["REF","channel","processing","elapsed","interval","repeat","with_arguments"]
		def __init__(self, NODE, CHANNEL, interval, repeat=True, with_arguments=False):
			# https://stackoverflow.com/questions/599430/why-doesnt-the-weakref-work-on-this-bound-method
			# https://code.activestate.com/recipes/81253/
			
			if isinstance(NODE, MethodType):
				def fake_ref():
					return NODE
				self.REF = fake_ref
			else:
				self.REF = weakref_ref(NODE)
			self.channel = CHANNEL
			#self.handler = HANDLER
			self.processing = processing(self)

			# TODO we just need next_timeout = snap_time_since_epoch() + interval
			# -- just last_time, and interval, then snap_time_since_epoch() - last_time > interval means expired!  and then set last time to current...
			#self.started = started # -1 or time of timer initialization (never changes)
			#self.interval = interval # -1 or time from start that results in timeout
			#self.current = current # -1 or current time of timer (starts at interval and is subtracted until < 0 and then reset)
			self.elapsed = 0. # the change in time each timer process accumulates until interval is reached...
			self.interval = interval # the duration of the timer
			self.repeat = repeat # False or whether timer repeats or is discarded after use
			self.with_arguments = with_arguments


		def __repr__(self):
			if self.REF() is not None:
				n = 'node:{}.{}'.format(self.REF().__class__.__name__, self.channel)
			else:
				n = 'node:None'
			t = 'elapsed:{} interval:{}'.format(self.elapsed, self.interval)
			r = 'repeat:{}'.format(bool(self.repeat))
			data = ' '.join([n,t,r])
			return '<{}({}) {}>'.format(self.__class__.__name__, data, hex(id(self)))

	

	# putting these here cause I don't think they should be user accessible
	# (users of timers should be ensured that if the program is running the timers are too,
	# this is for when there are no timers to prevent mainloop spamming); internal use only

	def start(self):
		if self['__last_time__'] is None:
			self['__last_time__'] = snap_time_since_epoch()
		self['__paused__'] = False
		ENV.mainloop.listen(self.process)

	def pause(self):
		self['__last_time__'] = None
		self['__paused__'] = True
		ENV.mainloop.ignore(self.process)

	class SnapTimers(SnapNode):

		__slots__ = []

		# TODO all instances of timers (one per program) share a single __LAST_TIME__ which is updated by the main program?  then all timers are evaluated from that value at once?  so do emit not send!
		# TODO last time and change in time would both need to be global singletons...

		#def __getattribute__(self, ATTR):
		#	return SnapNode.__getattribute_strict__(self, ATTR)

		@ENV.SnapProperty
		class fps:
			# for gui frame rate, putting it in a logical location
			# TODO this needs to be implemented as a timer?  maybe a special one?  so when we change the rate the timer is updated?  then it needs to call a timeout that sends update() and render() emissions to the appropriate channels...
			def get(self, MSG):
				"()->float"
				for tinfo in self['__timers__']:
					if tinfo.channel == '_fps_timeout' and tinfo.REF and tinfo.REF() is self:
						return tinfo.interval
				return None

			def set(self, MSG):
				"(float!)"
				fps = MSG.args[0]
				if fps is None:
					self.stop(self._fps_timeout)
				else:
					self.start(self._fps_timeout, fps=fps, repeat=True)
				self.changed(fps=fps)

		@fps.shared
		class frames_per_second: pass

		@ENV.SnapChannel
		def scene_update(self, MSG):
			raise NotImplementedError('only for send()')

		@ENV.SnapChannel
		def scene_render(self, MSG):
			raise NotImplementedError('only for send()')

		@ENV.SnapChannel
		def _fps_timeout(self, MSG):
			'()'

			self.scene_update.send()

			GUI = getattr(ENV, 'GUI', None)
			DEVICES = getattr(ENV, 'DEVICES', None)
			if GUI is not None and DEVICES is not None:
				# TODO set a flag in device motion, if device is updated within frame we don't need to do it again!  set the flag back to false here...
				# TODO ENV.__PRIVATE__['__DEVICE_EVENT_THIS_FRAME__'] = False
				for pointer in DEVICES['pointers']:
					GUI._update_pointer_interaction(pointer, is_pointer_motion=False) # so animated elements can notify if they are under mouse after update...

			self.scene_render.send()

		@ENV.SnapChannel
		def process(self, MSG):
		#def REFRESH(self, SOURCE, *args, **kwargs):
			# update and emit

			#ENV.snap_out('process', len(self['__timers__'] or []))

			if self['__paused__']:
				return None

			timers = self['__timers__']
			if len(timers) < 1:
				pause(self)
				return None

			CURRENT_TIME = snap_time_since_epoch()
			#ENV.snap_out("current time", CURRENT_TIME)
			CHANGE = CURRENT_TIME - self['__last_time__']
			#snap_out("CHANGE %lli\n  current %lli\nlast_time %lli" % (CHANGE, CURRENT_TIME, last_time))
			self['__last_time__'] = CURRENT_TIME

			# copy timers so original can be edited without causing problems
			# if we assign copy to local variable so it is visible then a timer could be cancelled during evaluation by assigning NULL in duplicate list
			# TODO what if instead of this we QUEUE new timers, and add them into listing at beginning of cycle?  and delete them after? as separate lists, so START goes to the queue to be added to active?
			fixed_length = self['__fix_timers_length__'] = len(timers)
			# timers < fixed_length will be understood to be actively processed (can still be cancelled)

			#SnapTimers_timer_t* tinfo;
			#SnapObject N, ref; // to localize self for callback, where user can't access it

			#elapsed = 0.
			#interval = 0.
			#SNAPLIST(callback_msg, "elapsed", &elapsed, "interval", &interval);

			i = -1
			while 1:
				i += 1

				if i >= fixed_length:
					break

				tinfo = timers[i]

				if not tinfo or not tinfo.REF or tinfo.REF() is None or tinfo.processing is None:
					# deleted?
					# okay to change timer length here?  length = timers[0]?
					# swap last timer to this position and set last timer position to None and re_alloc smaller?
					#ENV.snap_debug('invalid timer (no node)')
					timers[i] = None
					continue

				#NODE = tinfo.REF()

				#ENV.snap_out("process timer", tinfo)
				tinfo.elapsed += CHANGE
				if tinfo.elapsed >= tinfo.interval:

					#ENV.snap_out('timer expired', tinfo)#.elapsed, tinfo.interval, CHANGE)

					# XXX do this without abs()
					#elapsed = tinfo->current;// / tinfo->interval;
					#skip = (int)(elapsed / tinfo->interval) - 1; // will always be one, we want to know how many more than one
					#remainder = elapsed % tinfo->interval;

					# NOTE: the node has to be localized, so that the variable is protected from the user
					# so if timer is cancelled from the callback it won't change the address of the call!
					# ie. if the user cancels the timer from the callback without the localized var here, self will
					# suddenly be pointing to NULL data!  (since the timer was cancelled but the address is still
					# referenced as self)
					#N = tinfo.NODE
					#ref = tinfo.NODE
					#snap_event(&N, tinfo->EVENT, "elapsed", &tinfo->current, "interval", &tinfo->interval);
					#elapsed = tinfo.current
					#interval = tinfo.interval
					#_snap_event(&N, tinfo->EVENT, &callback_msg);
					# XXX this is wrong, send is an emit, we want to call!  store the method as REF (instead of NODE) and just call it, pass in message direct...
					# TODO also: protect this with try!
					#try:
						# TODO don't pass args?  or make it optional...  and support iterators like tasks does...
						# skip = (elapsed % interval) - 1
						#getattr(NODE, tinfo.channel)(elapsed=tinfo.elapsed, interval=tinfo.interval)
					next(tinfo.processing)
					#except StopIteration:
					#	tinfo.REF = None
					#	tinfo.processing = None
					#except Exception as e:
					#	ENV.snap_error(tinfo.REF() if tinfo.REF is not None else None, tinfo.channel, ENV.snap_exception_info(e))
					#	tinfo.REF = None # remove timer
					#	tinfo.processing = None
					#snap_send(NODE, self, tinfo.EVENT, elapsed = tinfo.current, interval = tinfo.interval)

					#ENV.snap_out('tinfo', tinfo)

					# now the timer might have changed after the user event...
					if timers[i] != tinfo or tinfo.REF is None or tinfo.REF() is None or tinfo.processing is None:
						
						if timers[i] != tinfo:
							#snap_warning("timer cancelled in callback")
							if tinfo not in timers: # TODO binary search? #if (SnapList_find(&timers, tinfo) < 0){
								# assume timer was freed during event call
								continue

					# XXX this is in processing now?
					if not tinfo.repeat: # NODE check in case it was deleted?
						timers[i] = None # remove from list first
						#if (snap_event(self, "NODE_USED", tinfo->NODE) != (any)"TRUE"){
						# only ignore if node not used in another timer
						# XXX snap_ignore(tinfo.NODE(), self) #snap_event(&tinfo->NODE, "IGNORE", *self);
						#snap_free(tinfo);
						continue

					# carry over remainder to next timeout (%)
					#tinfo->current = (tinfo->interval > 0.) ? 0. : snap_double_modulo(elapsed, tinfo->interval);

					# always reset to 0 (this means timers won't be very accurate BUT if a timer over-expires it won't spam!
					tinfo.elapsed = 0.

			self['__fix_timers_length__'] = None
			#snap_assignattr_at(self, "_fix_timers_length_", NULL, 0, IDX_SnapTimers__fix_timers_length_);

			# constrict timers here, start and cancel just work on list in place or append to it

			self['__timers__'] = timers = [t for t in timers if t != None]
			if len(timers) < 1:
				pause(self)

			return None

		@ENV.SnapChannel
		def start(self, MSG):

			# TODO timers only support method type (store the actual method!), tasks can support method or generator

			# TODO check for same time between timers and group them into single checks?  (ie. if multiple different timers are all for 2 seconds, they should be grouped so they can be checked just the one time)

			# TODO allow regular functions/methods and generators...
			# just wrap in a handler function...

			# TODO also group the timers by time interval?  if timers are for same interval then fire them together (just check expiry of first element and if so then fire off the whole set...)

			callback = MSG.args[0]
			if isinstance(callback, SnapBoundChannel):
				assert isinstance(callback, SnapBoundChannel), 'arg[0] must be a SnapBoundChannel'

				node,channel,method = callback.__data__

				if method is None or node is None:
					ENV.snap_warning('cannot add timer for channel with no method or node: {}'.format(repr(channel)))
					return None
				

			elif isinstance(callback, (MethodType, FunctionType, GeneratorType)):
				# can still become generator if it returns one...
				node = callback
				channel = None

			else:
				raise TypeError(type(callback), 'unsupported')

			# TODO just store the method (if it isn't None otherwise raise or just warn?)

			interval = 0. # will only be as fast as the owning program next() / mainloop rate...
			repeat = True # because non-repeating 'timers' are usually better implemented as a task (callback), so timers are usually assumed to repeat...
			with_arguments = False # whether to pass elapsed info in the callback, or no arguments

			for attr,value in MSG.kwargs.items():

				#if attr in ('event','EVENT'):
				#	EVENT = value

				if attr in ('seconds', 'secs', 's', 'interval'):
					interval = float(value)

				elif attr in ("milliseconds", "millisecs", "ms"):
					interval = float(value) * .001 #/ 1000.0
				
				elif attr in ('microseconds', 'microsecs', 'usecs'):
					interval = float(value) * .000001 #/ 1000000.0

				elif attr in ('nanoseconds','nanosecs','ns'):
					interval = float(value) * .000000001 #/ 1000000000.0

				# TODO else if (attr == (any)"timestamp") // TODO put timestamp conversions in this module?  or into an os.time.h module
				elif attr in ('fps', 'per_second', 'per_sec'):
					if value and value != 0:
						interval = 1.0 / float(value)
					else:
						interval = ENV.SNAP_DOUBLE_MAX

				elif attr == 'with_arguments':
					with_arguments = bool(value)

				elif attr == 'repeat':
					repeat = bool(value)

				else:
					ENV.snap_warning("unknown arg \"%s\"" % attr)


			if interval < 0.:
				interval = 0.
				ENV.snap_warning("interval clamped (was < 0, now 0)")

			ID = id(node)

			timers = self['__timers__'] or []
			i = 0
			while i < len(timers):

				timer = timers[i]

				if timer and timer.REF and id(timer.REF()) == ID:

					fixed_length = self['__fix_timers_length__']
					if fixed_length is not None and i < fixed_length and not timer.repeat:
						pass # a timer is being processed but it will not repeat so create a new to replace it! (drop down)
					else:
						# timer already exists, overwrite and reset
						#snap_debug("timer already exists \"%s\", restarted", (char*)EVENT);
						# reset existing timer
						#timer.handler = handler
						timer.elapsed = 0.
						timer.interval = interval
						timer.repeat = repeat
						timer.with_arguments = with_arguments
						timer.processing = processing(timer)
						return None

				i += 1

			timer = SnapTimerInternal(
				node,
				channel,
				interval=interval,
				repeat=repeat,
				with_arguments=with_arguments)

			# TODO NODE.__gc__.listen(self.__gc__) ?
			#snap_listen(NODE, self)

			#ENV.snap_out("new timer", timer)

			timers.append(timer) #SnapList_append(&timers, timer); # TODO sorted insert
			self['__timers__'] = timers #snap_setattr_at(self, "_timers_", timers, IDX_SnapTimers__timers_);

			start(self)

			# TODO return the timer as a SnapObject?  use that timer as the identity when using multiple timers?
			return timer

		@ENV.SnapChannel
		def stop(self, MSG):# node=None, **SETTINGS):

			callback = MSG.args[0]
			if isinstance(callback, SnapBoundChannel):
				assert isinstance(callback, SnapBoundChannel), 'arg[0] must be a SnapBoundChannel'

				node,channel,method = callback.__data__

				if method is None or node is None:
					ENV.snap_warning('cannot add timer for channel with no method or node: {}'.format(repr(channel)))
					return None
				

			elif isinstance(callback, (MethodType, FunctionType, GeneratorType)):
				node = callback
				channel = None

			else:
				raise TypeError(type(callback), 'unsupported')
			
			
			#node,channel,method = bound_channel.__data__

			#if method is None or node is None:
			#	return None

			timers = self['__timers__']
			if not timers or len(timers) < 1:
				return None


			#def node_used(NODE):

			#	nid = id(NODE)
			#	for tinfo in timers:
			#		if tinfo and tinfo.NODE and id(tinfo.NODE()) == nid:
			#			return True
			#	return False

			ID = id(node)
			i = 0
			while i < len(timers):

				timer = timers[i]
				if timer and timer.REF and id(timer.REF()) == ID:
					# NOTE: we do not constrict list on cancel, it is done at end of refresh
					timers[i] = None
					#if not node_used(timer.NODE()): XXX?  timer.NODE().__gc__.ignore(self.__gc__)?
					#	ENV.snap_ignore(timer.NODE(), self)

				i += 1

			return None

		# XXX we don't want all timers to be clearable, nodes should just free their own timers...
		"""
		def clear(self, MSG):
			# cancel and remove all timers XXX should this be possible?

			# NOTE: constrict only happens in refresh

			data = self.data

			timers = data['__timers__']
			if not timers:
				return None

			i = 0
			while i < len(timers):

				timer = timers[i]
				timers[i] = None
				if 0:#timer:
					# NOTE: even if emit is underway we clear out all timers
					# and just ignore on each call since there will be none left
					if timer.REF is not None and timer.REF() is not None:
						#ENV.snap_ignore(timer.NODE(), self)
						'timer.NODE().__gc__.ignore(self.__gc__)' # TODO ?

				i += 1

			return None
		"""

		def __del__(self):
			''#ENV.snap_error('timers del')

		def __init__(self):
			SnapNode.__init__(self)

			self['__timers__'] = []
			self['__fix_timers_length__'] = None #(int*) of length of timers during refresh; means we're processing timers, so new ones added need to consider that...
			self['__paused__'] = True # starts when timer added
			self['__last_time__'] = None

	ENV.SnapTimers = SnapTimers
	#ENV.TIMERS = SnapTimers()

def main(ENV):

	SnapNode = ENV.SnapNode
	
	class User(SnapNode):

		@ENV.SnapChannel
		def timeout(self, MSG):
			ENV.snap_out('timeout', MSG)
			self.count += 1

		def __init__(self):
			self.count = 0

	user = User()

	#ENV.PROGRAM = ENV.SnapProgram()
	
	TIMERS = ENV.SnapTimers()
	TIMERS.start(user.timeout, seconds=1, repeat=True)

	while user.count < 10:
		# this runs at full speed...
		ENV.__PRIVATE__['__MAINLOOP_NODE__'].next()

	ENV.snap_out('finished ok.')

