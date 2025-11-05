
from weakref import ref as weakref_ref

from types import FunctionType, MethodType, GeneratorType

def build(ENV):

	SnapNode = ENV.SnapNode
	SnapTimers = ENV.SnapTimers

	SnapBoundChannel = ENV.SnapBoundChannel

	# TODO it's either an object and attr, or a generator...  if it's callable then return means we switch to generator eval until complete then we can go back to function eval (if it was a function)

	"""
	def processing(TIMER):
		# this would be assigned to timer, just keep calling forever, if it returns start a new one...
		# timer quits when INSTANCE weakref is None, or error occurs in call, or repeat is False

		# think of this as 'one complete processing', which means firing off the generator on each timeout if there is one

		while 1:

			yield

			#kwargs = {'elapsed':TIMER['elapsed'], 'interval':TIMER['interval']} if TIMER['with_arguments'] else {}

			#if TIMER['paused']:
			#	return

			WEAKREF,ATTR,GENERATOR = TIMER['object']

			if WEAKREF is None:
				'generator or quit?'

			INSTANCE = WEAKREF()

			if WEAKREF is None or WEAKREF() is None:

			if CALLABLE is None:
				return

			if isinstance(CALLABLE, GeneratorType):
				_return = CALLABLE # drop down to generator evaluation

			else:

				if isinstance(CALLABLE, SnapBoundChannel):
					node,channel,method = CALLABLE.__data__
					if method is None:
						#TIMER['processing'] = None
						return # if channel doesn't exist then there is nothing to call, but ignore silently?

					#ENV.snap_out('call channel', CALLABLE, node, channel)

				# MethodType, FunctionType allowed as well... (or anything with a __call__ really)
				_return = CALLABLE()#.__direct__(MSG)

				if not isinstance(_return, GeneratorType):
					if TIMER['repeat']:
						continue
					return

			# if the method returns a generator type (uses yield) then we keep processing it until it is complete...
			# it is the user's job to make sure the processing does not take a long time
			# quit by returning from the generator

			while 1:
				
				try:
					next(_return)
				except StopIteration:
					#TIMER['processing'] = None
					return # no error
				#except Exception as e:
				#	ENV.snap_error(node, channel, 'error >>')
				#	ENV.snap_print_exception(e)
				#	ENV.snap_print_stack()
				#	return

				yield
	"""

	class SnapTimer(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class object:

			def get(self, MSG):
				"()->object"
				# TODO retrieve the orginal object (getattr...) if applicable, either INSTANCE.attr, generator, or INSTANCE()

				OBJECT_LIST = self.__snap_data__['object']
				if OBJECT_LIST:
					WEAKREF,ATTR,GENERATOR = OBJECT_LIST
					INSTANCE = None
					if WEAKREF is not None:
						INSTANCE = WEAKREF()

					if ATTR is not None and INSTANCE is not None:
						return getattr(INSTANCE, ATTR)

					elif INSTANCE is not None:
						return INSTANCE

					elif GENERATOR is not None:
						return GENERATOR

					else:
						raise ValueError('???', OBJECT_LIST)

				return None

			def set(self, MSG):
				"(object!)"
				obj = MSG.args[0]

				if isinstance(obj, SnapBoundChannel):
					# includes SnapProperty and SnapChannel
					instance,attr,method = obj.__data__
					assert method is not None, 'cannot call channel("{}") without a function'.format(attr)
					generator = None
	
				elif isinstance(obj, MethodType):
					instance = getattr(obj, '__self__', getattr(obj, 'im_self', None))
					attr = obj.__name__
					generator = None

				elif isinstance(obj, FunctionType):
					instance = obj
					attr = None
					generator = None

				elif isinstance(obj, GeneratorType):
					instance = attr = None
					generator = obj

				else:
					raise TypeError(type(obj))

				current = self.__snap_data__['object']
				self.__snap_data__['object'] = [weakref_ref(instance) if instance is not None else None, attr, generator]
				if current is not None and (current[0] is obj or (current[1] and getattr(current[0], current[1]) is obj)):
					pass
				else:
					self.changed(object=obj)

		@object.alias
		class node: pass

		@object.alias
		class callable: pass

		@ENV.SnapProperty
		class elapsed:

			def get(self, MSG):
				"()->float"
				return self.__snap_data__['elapsed'] or 0.

			set = None

		@ENV.SnapProperty
		class finished:

			def get(self, MSG):
				"()->bool"

				if self.__snap_data__['paused'] is not None:
					# if pause has status we're still in play
					return False

				if ENV.mainloop.__data__[0].__snap_listeners__.has_node(self):
					# if we're listening to mainloop we're in play
					return False				

				return True

		@ENV.SnapProperty
		class running:

			def get(self, MSG):
				"()->bool"
				return not self['finished']

		# TODO duration?

		@ENV.SnapProperty
		class interval:
			# NOTE: user can change interval while timer is running...

			def get(self, MSG):
				"()->float"
				return self.__snap_data__['interval'] or 0.

			def set(self, MSG):
				"(int|float!)"
				value = MSG.args[0]
				current = self['interval']
				if value is None:
					value = 0.
				value = float(value)
				assert value >= 0., 'cannot be negative'
				self.__snap_data__['interval'] = value
				if value != current:
					self.changed(interval=value)

		@interval.alias
		class seconds: pass

		@interval.alias
		class s: pass # seconds

		@ENV.SnapProperty
		class frames_per_second:

			def get(self, MSG):
				"()->int|float"
				interval = self['interval']
				if interval < ENV.SNAP_DOUBLE_MIN:
					return 0
				else:
					return 1.0 / interval

			def set(self, MSG):
				"(int|float!)"
				frames = MSG.args[0]
				if frames is None:
					frames = 0

				if frames < ENV.SNAP_DOUBLE_MIN:
					self['interval'] = ENV.SNAP_DOUBLE_MAX
				else:
					self['interval'] = 1. / frames

		@frames_per_second.alias
		class rate: pass					

		@frames_per_second.alias
		class fps: pass


		@ENV.SnapProperty
		class milliseconds:

			def get(self, MSG):
				"()->float"
				return self['interval'] / 1000.0

			def set(self, MSG):
				"(int|float!)"
				value = MSG.args[0]
				if value is None:
					value = 0
				self['interval'] = value * 0.001

		@milliseconds.alias
		class millisecs: pass

		@milliseconds.alias
		class ms: pass

		@ENV.SnapProperty
		class microseconds:

			def get(self, MSG):
				"()->float"
				return self['interval'] / 1000000.0

			def set(self, MSG):
				"(float|int!)"
				value = MSG.args[0]
				if value is None:
					value = 0
				self['interval'] = value * 0.000001

		@microseconds.alias
		class microsecs: pass

		@microseconds.alias
		class usecs: pass

		@ENV.SnapProperty
		class nanoseconds:

			def get(self, MSG):
				"()->float"
				return self['interval'] / 1000000000.0

			def set(self, MSG):
				"(float|int!)"
				value = MSG.args[0]
				if value is None:
					value = 0
				self['interval'] = value * 0.000000001


		@nanoseconds.alias
		class nanosecs: pass

		@nanoseconds.alias
		class ns: pass



		@ENV.SnapProperty
		class repeat:

			def get(self, MSG):
				"()->bool"
				return self.__snap_data__['repeat'] is not False # None is True

			def set(self, MSG):
				"(bool!)"
				value = bool(MSG.args[0])
				current = self.__snap_data__['repeat'] is True
				self.__snap_data__['repeat'] = value
				if current != value:
					self.changed(repeat=value)

		@ENV.SnapProperty
		class paused:
			def get(self, MSG):
				"()->bool"
				return self.__snap_data__['paused'] is True

			def set(self, MSG):
				"(bool!)"
				value = bool(MSG.args[0])
				current = self['paused']
				if value != current:
					if value:
						self.pause()
					else:
						self.start()
					self.changed(paused=value)

		@ENV.SnapChannel
		def __timeout__(self, MSG):
			"()"

			data = self.__snap_data__

			elapsed = data['elapsed'] = self['elapsed'] + SnapTimers.ELAPSED_TIME
			if elapsed < self['interval']:
				#ENV.snap_out('not expired', elapsed)
				return

			# timer has 'expired', call one iteration (either a call() or a generator next())
			#if data['object'][1] != 'render':
			#	ENV.snap_warning('__timeout__', elapsed, self['interval'], data['object'])

			OBJECT_LIST = data['object']
			if OBJECT_LIST is None:
				return self.stop()

			WEAKREF,ATTR,GENERATOR = OBJECT_LIST
			CALLABLE = None
			if WEAKREF is not None:
				CALLABLE = WEAKREF()

			if GENERATOR is None:

				if CALLABLE is None:
					return self.stop()

				elif ATTR is not None:
					CALLABLE = getattr(CALLABLE, ATTR)

				#try:
				_return = CALLABLE()
				#except Exception as e:
				#	ENV.snap_print_exception(e)
				#	ENV.snap_error(self, CALLABLE, ATTR)
				#	return self.stop()

				if isinstance(_return, GeneratorType):
					GENERATOR = OBJECT_LIST[-1] = _return

			# catch the generator at the bottom there ^, otherwise this would be 'else'
			if GENERATOR is not None:
				try:
					next(GENERATOR)
				except StopIteration:
					#TIMER['processing'] = None
					OBJECT_LIST[-1] = None # clear generator

			if not self['repeat']:
				return self.stop()
					# not an error, go back to callable on next iteration if there is one
				# we let other errors handle by the mainloop so we get better debug...
				#except Exception as e:
				#	ENV.snap_error(node, channel, 'error >>')
				#	ENV.snap_print_exception(e)
				#	ENV.snap_print_stack()
				#	return

			# # always reset to 0 (this means timers won't be very accurate BUT if a timer over-expires it won't spam!

			data['elapsed'] = 0. # reset

		@ENV.SnapChannel
		def start(self, MSG):
			"()"
			# TODO set properties?

			if MSG.args:
				assert len(MSG.args) == 1, 'only one callable can be assigned to a timer'
				self['object'] = MSG.args[0]

			if MSG.kwargs:
				self.set(**MSG.kwargs)

			del self.__snap_data__['paused']
			ENV.mainloop.listen(self.__timeout__)
			self.start.emit()

		@ENV.SnapChannel
		def pause(self, MSG):
			"()"
			self.__snap_data__['paused'] = True
			ENV.mainloop.ignore(self.__timeout__)
			self.pause.emit()

		@ENV.SnapChannel
		def stop(self, MSG):
			"()"
			#del self.__snap_data__['object']
			del self.__snap_data__['paused']
			self.__snap_data__['elapsed'] = 0.
			ENV.mainloop.ignore(self.__timeout__)
			self.stop.emit()
			self.finished.emit()

		@stop.alias
		class cancel: pass




		# TODO draw/lookup so it can be rendered?  -- create shader in draw if doesn't exist


		def __init__(self, CALLABLE, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if CALLABLE is not None:
				self['object'] = CALLABLE
				self.start()

	ENV.SnapTimer = SnapTimer

def main(ENV):

	build(ENV)

	SnapNode = ENV.SnapNode

	class Test(SnapNode):

		def method_timeout_test(self, *a, **k):
			ENV.snap_out('method timeout test', a, k)

		def __init__(self):
			SnapNode.__init__(self)

			#t = ENV.SnapTimer()

	# TODO run mainloop and test timer timeout, change the rate

	# TODO do weakref test with method, can timer not keep object alive?  -- store method as just the name, redo the lookup?  keep weakref to the node?

	ENV.__run_gui__(Test)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())
