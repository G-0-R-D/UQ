
from types import MethodType
from weakref import ref as weakref_ref

from collections import namedtuple
DATA = namedtuple('__data__', ['instance', 'channel', 'callable']) # TODO use this instead?

def build(ENV):

	SnapMessage = ENV.SnapMessage

	class SilentLock(object):
		# https://book.pythontips.com/en/latest/context_managers.html

		# TODO use this to replace the listeners list itself...  then listen/ignore would redirect to here (and subsequent locks won't get messages?  we can intercept them...)

		__slots__ = ['__data__', '__weakref__']

		def handle(self, MODE, MSG):
			pass

		def release(self):

			INSTANCE,CHANNEL,CALLABLE = self.__data__

			blocked = INSTANCE.__snap_data__.get('__blocked__')
			if blocked is None:
				return

			channel = blocked.get(CHANNEL)
			if channel is None:
				return

			channel = [wk for wk in channel if wk() is not None and wk() is not self]
		
			if not channel:
				del blocked[CHANNEL]
			else:
				blocked[CHANNEL] = channel

			if not blocked:
				del INSTANCE.__snap_data__['__blocked__']

		def __enter__(self):
			return self

		def __exit__(self, TYPE, VALUE, TRACEBACK):
			self.release()

		def __init__(self, INSTANCE, CHANNEL, CALLABLE):
			self.__data__ = (INSTANCE, CHANNEL, CALLABLE)

			blocked = INSTANCE.__snap_data__.get('__blocked__', {})
			channel = blocked.get(CHANNEL, [])
			assert self not in channel, 'channel lock already in channel?'
			channel.append(weakref_ref(self)) # use weakref so it doesn't keep the lock alive
			blocked[CHANNEL] = channel
			INSTANCE.__snap_data__['__blocked__'] = blocked

		def __del__(self):
			self.__exit__(None, None, None)

	class AggregatorLock(SilentLock):

		__slots__ = ['__accum__']

		def handle(self, MODE, MSG):
			msg = self.__accum__.get(MODE, SnapMessage())
			msg.args += MSG.args # or msg.args = MSG.args?
			msg.kwargs.update(MSG.kwargs)

			INSTANCE,CHANNEL,CALLABLE = self.__data__
			msg.source = INSTANCE
			msg.channel = CHANNEL
			self.__accum__[MODE] = msg

		def release(self):
			SilentLock.release(self)

			INSTANCE,CHANNEL,CALLABLE = self.__data__

			# TODO if another aggregator lock is still in the channel blocked then don't emit (just do one emission on longest lock?)

			# TODO put the silencing/aggregating behaviour onto the options of the channel or property?  so when the property is called it will do it first internally?

			if self.__accum__:
				for mode,msg in self.__accum__.items():
					getattr(getattr(INSTANCE, CHANNEL), mode)(msg)
			self.__accum__ = None

		def __init__(self, *a, **k):
			SilentLock.__init__(self, *a, **k)

			self.__accum__ = {
				#'__emit__':SnapMessage(),
				#'__send__':SnapMessage(),
			}
		
	class SnapBoundChannel(object):
		# thinking of the method as more of a "channel" of communication which basically means same name = same channel
		# but channels of different names can connect together...

		__slots__ = ['__data__', '__weakref__']

		@property
		def called(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			assert '.' not in ATTR, 'sub channels are only one layer down'
			return SnapBoundChannel(INSTANCE, ATTR + '.called', None)

		# TODO def check_compat(BoundChannel()) to check if connection is valid?

		def aggregate(self):
			return AggregatorLock(*self.__data__)

		def aggregator(self):
			return self.aggregate()

		def silent(self):
			return SilentLock(*self.__data__)

		def silence(self):
			return self.silent()

		def __negotiate__XXX(self, SOURCE, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL):
			'access and get the docstring if spec is not defined for each method, make SnapArgConverter if necessary to remap arguments otherwise just pass back None?'
			# XXX put this somewhere else, as a standalone operator, and break it into steps: acquire spec args (from __snap_data__ or docstring)

			# TODO use spec like 'SnapInput(int,float,...,key=value, options(...), required(names...?))
			# TODO SnapMessage can also unpack/verify args based on the spec?

			# channel represents event or property access (all connections, data is protected)

			# spec options from old design:
			# return_value = 'type(...)' string of single type
			# sync = True|False (for output, if it is emit or send)
			# required = list of index|name of required arguments
			# sets = list of lists of index|name (like required, args that should be sent together)
			# output = SnapOutput(...)
			# strict = list of index|name of arguments that must be only the specified type (not a subclass)

			return None # args are compatible


		def __connect__(self, LISTENER, INPUT_CHANNEL, converter=None):

			SOURCE,OUTPUT_CHANNEL,METHOD = self.__data__

			assert isinstance(OUTPUT_CHANNEL, str) and isinstance(INPUT_CHANNEL, str), 'channels must be strings'
			assert isinstance(SOURCE, ENV.SnapNode) and isinstance(LISTENER, ENV.SnapNode), 'listeners must be SnapNode type'
			
			'verify self.output is compatible with LISTENER.input...' # TODO NOTE: still allow incompatibles to connect, but make it clear they aren't compatible


			# TODO negotiate?  arg compat?
			# TODO converter is callable that does filtering of arguments for compatibility if necessary (use exec to create?)  -- logic elsewhere

			#L = (weakref_ref(LISTENER), INPUT_CHANNEL, converter)#self.__negotiate__(SOURCE, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL))

			listeners = getattr(SOURCE, '__snap_listeners__', None)
			if listeners is None:
				listeners = SOURCE.__snap_listeners__ = ENV.SnapNodeListeners()

			return listeners.connect(OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL, converter)


		def __disconnect__(self, LISTENER, INPUT_CHANNEL):

			SOURCE,OUTPUT_CHANNEL,METHOD = self.__data__

			if getattr(SOURCE, '__snap_listeners__', None) is None:
				return None

			SOURCE.__snap_listeners__.disconnect(OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL)

			if SOURCE.__snap_listeners__.unused():
				delattr(SOURCE, '__snap_listeners__')

			return None


		def __emit__(self, MSG):

			INSTANCE,CHANNEL,METHOD = self.__data__

			listeners = getattr(INSTANCE, '__snap_listeners__', None)
			if listeners is not None and CHANNEL in listeners.channels:

				try:
					ENV.__snap_queue_send__(INSTANCE, CHANNEL, MSG)
				except:
					ENV.snap_warning('ENV cannot queue send (emit)?')
					self.__send__(MSG)

			return None


		def __send__(self, MSG):

			INSTANCE,OUTPUT_CHANNEL,METHOD = self.__data__

			listeners = getattr(INSTANCE, '__snap_listeners__', None)
			if listeners is not None:
				return listeners.send(INSTANCE, OUTPUT_CHANNEL, MSG)
			return None



		def listen(self, LISTENER_BOUND_CHANNEL, converter=None):

			assert isinstance(LISTENER_BOUND_CHANNEL, SnapBoundChannel), 'requires SnapBoundChannel (access the channel as an attribute first)'

			LISTENER,INPUT_CHANNEL,METHOD = LISTENER_BOUND_CHANNEL.__data__

			return self.__connect__(LISTENER, INPUT_CHANNEL, converter=converter)

		def ignore(self, LISTENER_BOUND_CHANNEL):

			assert isinstance(LISTENER_BOUND_CHANNEL, SnapBoundChannel), 'requires SnapBoundChannel'

			LISTENER,INPUT_CHANNEL,METHOD = LISTENER_BOUND_CHANNEL.__data__

			return self.__disconnect__(LISTENER, INPUT_CHANNEL)

		def emit(self, *a, **k):
			return self.__emit__(SnapMessage(*a, **k))

		def send(self, *a, **k):
			return self.__send__(SnapMessage(*a, **k))


		def __call__(self, *a, **k):
			return self.__direct__(SnapMessage(*a, **k))

		def __direct__(self, MSG):
			# this is the input operation for a channel (call the method with the message)
			# send MSG directly to the callable, as is
			INSTANCE,ATTR,CALLABLE = self.__data__
			if CALLABLE is not None:
				#_return = CALLABLE(INSTANCE, *MSG.args, **MSG.kwargs) # TODO ?  re-use message?  but we don't know what type of __call__ it is and __call__ takes (*a, **k)...
				_return = CALLABLE.__direct__(INSTANCE, MSG)
				self.called.emit()
				return _return

			# we don't want to be able to call methods that don't exist (but we can still send/emit to their listeners...)
			raise AttributeError(INSTANCE.__class__.__name__, ATTR)



		# TODO use __setitem__ api to assign args?  can do it in __init__ like self.channel.set_spec(SnapProperty(), ...)?

		def __repr__(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			return '<' + self.__class__.__name__ + '(' + str(CALLABLE) + ')>'

		def __init__(self, INSTANCE, CHANNEL, CALLABLE):
			self.__data__ = (INSTANCE, CHANNEL, CALLABLE)

	ENV.SnapBoundChannel = SnapBoundChannel


	class SnapBoundProperty(SnapBoundChannel):

		@property
		def accessed(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			assert '.' not in ATTR, 'sub channels are only one layer down'
			return SnapBoundChannel(INSTANCE, ATTR + '.accessed', None)

		@property
		def assigned(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			assert '.' not in ATTR, 'sub channels are only one layer down'
			return SnapBoundChannel(INSTANCE, ATTR + '.assigned', None)

		@property
		def deleted(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			assert '.' not in ATTR, 'sub channels are only one layer down'
			return SnapBoundChannel(INSTANCE, ATTR + '.deleted', None)

		@property
		def attachable(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			return getattr(CALLABLE, 'attached', None) is not None

		def attached(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			return CALLABLE.attached(INSTANCE)

		def get(self, *a, **k):
			# TODO should this call __getitem__ and then __getitem__ calls self.__get__? XXX __getitem__ would forward to CALLABLE directly if it has the method, otherwise assumes it is a passthrough...
			INSTANCE,ATTR,CALLABLE = self.__data__
			if a or k:
				KEY = (ATTR, SnapMessage(*a, **k))
			else:
				KEY = ATTR
			return INSTANCE.__getitem__(KEY) # -> goes to CALLABLE.__HANDLERS__['get'] (if it has one), or to default access (if permitted)

		#def __get__(self, MSG):
		#	INSTANCE,ATTR,CALLABLE = self.__data__
		#	return CALLABLE.get(MSG)

		def set(self, VALUE, *a, **k):
			INSTANCE,ATTR,CALLABLE = self.__data__
			if a or k:
				KEY = (ATTR, SnapMessage(*a, **k))
			else:
				KEY = ATTR
			return INSTANCE.__setitem__(KEY, VALUE) # -> goes to CALLABLE.__HANDLERS__['set'] or default access

		def delete(self, *a, **k):
			INSTANCE,ATTR,CALLABLE = self.__data__
			if a or k:
				KEY = (ATTR, SnapMessage(*a, **k))
			else:
				KEY = ATTR
			return INSTANCE.__delitem__(KEY) # -> goes to CALLABLE.__HANDLERS__['delete'] or default access

		def __call__(self, *a, **k):
			return self.__direct__(SnapMessage(*a, **k))

		def __direct__(self, MSG):
			INSTANCE,ATTR,CALLABLE = self.__data__
			#return CALLABLE.__HANDLERS__['set'](INSTANCE, MSG)
			return CALLABLE.set(INSTANCE, MSG)

	ENV.SnapBoundProperty = SnapBoundProperty


