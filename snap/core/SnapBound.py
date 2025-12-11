

from types import MethodType
from weakref import ref as weakref_ref


def build(ENV):

	SnapMessage = ENV.SnapMessage

	snap_send_msg = ENV.snap_send_msg
	snap_emit_msg = ENV.snap_emit_msg

	snap_listen = ENV.snap_listen
	snap_ignore = ENV.snap_ignore

	class SnapBoundChannel(object):

		__slots__ = ['__data__', '__weakref__']

		"""
		@property
		def called(self):
			INSTANCE,CHANNEL_NAME,CALLABLE = self.__data__
			assert '.' not in CHANNEL_NAME, 'sub channels are only one layer down'
			return SnapBoundChannel(INSTANCE, CHANNEL_NAME + '.called', None)
		"""


		def listen(self, LISTENER, converter=None):
			if isinstance(LISTENER, SnapBoundChannel):
				LISTENER,INPUT_CHANNEL,_ = LISTENER.__data__
			else:
				assert callable(LISTENER), 'listener must be callable: ({})'.format(type(LISTENER))
				# LISTENER same
				INPUT_CHANNEL = self.__data__[1]

			SOURCE,OUTPUT_CHANNEL,_ = self.__data__

			return snap_listen(SOURCE, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL, converter=converter)

		def connect(self, LISTENER, converter=None):
			return self.listen(LISTENER, converter=converter)


		def ignore(self, LISTENER):

			if isinstance(LISTENER, SnapBoundChannel):
				LISTENER,INPUT_CHANNEL,_ = LISTENER.__data__
			else:
				# LISTENER same
				INPUT_CHANNEL = self.__data__[1]

			SOURCE,OUTPUT_CHANNEL,_ = self.__data__

			return snap_ignore(SOURCE, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL)

		def disconnect(self, LISTENER):
			return self.ignore(LISTENER)


		def emit_msg(self, MSG):
			INSTANCE,CHANNEL,METHOD = self.__data__
			return snap_emit_msg(INSTANCE, CHANNEL, MSG)

		__emit__ = emit_msg

		def emit(self, *a, **k):
			return self.__emit__(SnapMessage(*a, **k))



		def send_msg(self, MSG):
			INSTANCE,CHANNEL,METHOD = self.__data__
			return snap_send_msg(INSTANCE, CHANNEL, MSG)

		__send__ = send_msg

		def send(self, *a, **k):
			return self.send_msg(SnapMessage(*a, **k))


		def __call__(self, *a, **k):
			return self.__direct__(SnapMessage(*a, **k))

		def __call_direct__(self, MSG):
			# this is the input operation for a channel (call the method with the message)
			# send MSG directly to the callable, as is
			INSTANCE,ATTR,CALLABLE = self.__data__
			if CALLABLE is not None:
				_return = CALLABLE.__direct__(INSTANCE, MSG)
				#snap_emit_msg(INSTANCE, ATTR+'.called', SnapMessage())
				return _return


			# we don't want to be able to call methods that don't exist (but we can still send/emit to their listeners...)
			raise AttributeError(INSTANCE.__class__.__name__, ATTR)

		__direct__ = __call_direct__



		# TODO use __setitem__ api to assign args?  can do it in __init__ like self.channel.set_spec(SnapProperty(), ...)?

		def __repr__(self):
			INSTANCE,ATTR,CALLABLE = self.__data__
			return '<' + self.__class__.__name__ + '(' + str(CALLABLE) + ')>'

		def __init__(self, INSTANCE, CHANNEL, CALLABLE):
			self.__data__ = (INSTANCE, CHANNEL, CALLABLE)

	ENV.SnapBoundChannel = SnapBoundChannel


	class SnapBoundProperty(SnapBoundChannel):

		# XXX don't do subchannels, because calls don't have to go through the bound api!
		#	-- we could do this by making decorators on the channel decorator itself...  but then the decorator would need to be a SnapNode...
		"""
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
		"""

		def get(self, *a, **k):
			# TODO should this call __getitem__ and then __getitem__ calls self.__get__? XXX __getitem__ would forward to CALLABLE directly if it has the method, otherwise assumes it is a passthrough...
			INSTANCE,ATTR,CALLABLE = self.__data__
			return CALLABLE.get(INSTANCE, SnapMessage(*a, **k))
			#if a or k:
			#	KEY = (ATTR, SnapMessage(*a, **k))
			#else:
			#	KEY = ATTR
			#_return = INSTANCE.__getitem__(KEY) # -> goes to CALLABLE.__HANDLERS__['get'] (if it has one), or to default access (if permitted)
			#snap_emit_msg(INSTANCE, ATTR+'.accessed', SnapMessage())
			#return _return

		#def __get__(self, MSG):
		#	INSTANCE,ATTR,CALLABLE = self.__data__
		#	return CALLABLE.get(MSG)

		def set(self, *a, **k):
			INSTANCE,ATTR,CALLABLE = self.__data__

			return CALLABLE.set(INSTANCE, SnapMessage(*a, **k))
			#if a or k:
			#	KEY = (ATTR, SnapMessage(*a, **k))
			#else:
			#	KEY = ATTR
			#_return = INSTANCE.__setitem__(KEY, VALUE) # -> goes to CALLABLE.__HANDLERS__['set'] or default access
			#snap_emit_msg(INSTANCE, ATTR+'.assigned', SnapMessage())
			#return _return

		def delete(self, *a, **k):
			INSTANCE,ATTR,CALLABLE = self.__data__
			return CALLABLE.delete(INSTANCE, SnapMessage(*a, **k))
			#if a or k:
			#	KEY = (ATTR, SnapMessage(*a, **k))
			#else:
			#	KEY = ATTR
			#_return = INSTANCE.__delitem__(KEY) # -> goes to CALLABLE.__HANDLERS__['delete'] or default access
			#snap_emit_msg(INSTANCE, ATTR+'.deleted', SnapMessage())
			#return _return

		def __call__(self, *a, **k):
			return self.__call_direct__(SnapMessage(*a, **k))

		def __call_direct__(self, MSG):
			INSTANCE,ATTR,CALLABLE = self.__data__
			#return CALLABLE.__HANDLERS__['set'](INSTANCE, MSG)
			return CALLABLE.set(INSTANCE, MSG)

		__direct__ = __call_direct__

	ENV.SnapBoundProperty = SnapBoundProperty


