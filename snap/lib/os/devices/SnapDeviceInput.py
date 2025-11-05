

def build(ENV):

	snap_time = ENV.snap_time

	SnapNode = ENV.SnapNode
	SnapDeviceNode = ENV.SnapDeviceNode

	SnapMessage = ENV.SnapMessage

	snap_device_event = ENV.snap_device_event

	class SnapDeviceInput(SnapDeviceNode):

		__slots__ = []

		#def code(self, MSG):
		#	self.data().get('code', -1)

		#def value(self, MSG):
		#	self.data().get('value', 0.0)


		@ENV.SnapProperty
		class delta:

			def get(self, MSG):
				"""()->float"""
				return self.__snap_data__['delta'] or 0.

		@delta.shared
		class change: pass

		@ENV.SnapProperty
		class code:

			def get(self, MSG):
				"""()->int"""
				_return = self.__snap_data__['code']
				if _return is None:
					return -1
				return _return

			# set not in user domain

		@ENV.SnapProperty
		class value:

			def get(self, MSG):
				"""()->float"""
				return self.__snap_data__['value'] or 0.0

			def set(self, MSG):
				"(float!)"

				time = snap_time()
				self.__snap_data__['last_time'] = time

				value = MSG.args[0]
				if not value:
					value = 0.
				value = float(value)

				previous_value = self.__snap_data__['value'] or 0.

				self.__snap_data__['value'] = value

				change = value - previous_value

				self.__snap_data__['delta'] = change

				if change != 0:
					self.changed(value=value, delta=change, time=time)


		"""
		def __setitem__(self, KEY, VALUE):

			if KEY == 'code':

				prev = SnapDeviceNode.__getitem__(self, 'code')
				if prev is None or prev != VALUE:
					SnapNode.__setitem__(self, 'code', VALUE)
					self.changed.send(code=VALUE)

				return None

			elif KEY == 'value':
				VALUE = float(VALUE) if VALUE is not None else 0.0
				return SnapNode.__setitem__(self, 'value', VALUE)

			return SnapDeviceNode.__setitem__(self, KEY, VALUE)
		"""

		def __repr__(self):
			value = str(self['value'])
			name = self['name']
			if name is not None:
				value += ', ' + repr(name)
			return '<{}[{}]({}) {}>'.format(self.__class__.__name__, self['code'], value, hex(id(self)))

		def __init__(self, code=None, value=None, **SETTINGS):
			SnapDeviceNode.__init__(self, **SETTINGS)

			if code is not None:
				self.__snap_data__['code'] = int(code)
			if value is not None:
				self.__snap_data__['value'] = float(value)


	ENV.SnapDeviceInput = SnapDeviceInput

	class SnapDeviceInputButton(SnapDeviceInput):

		__slots__ = []

		#MODE_NORMAL = 0
		#MODE_TOGGLE = 1
		#REPEAT_INTERVAL = .5 # 500ms (100ms - 900ms is common double click range)

		#def count(self, MSG):
		#	return self.data().get('count',0)

		#def state(self, MSG):
		#	value = self.value()
		#	return True if value is not None and value >= .5 else False

		#def mode(self, MSG):
		#	mode = self.data().get('mode')
		#	return mode if mode is not None else self.MODE_NORMAL

		@ENV.SnapProperty
		class repeat_interval:

			def get(self, MSG):
				"""()->float"""
				interval = self.__snap_data__['repeat_interval']
				if interval is not None:
					return interval
				return .5 # 500ms (100-900ms is common double click range)

			def set(self, MSG):
				"""(float|int!)"""
				interval = MSG.args[0]
				if interval is not None:
					assert isinstance(interval, (float, int)), 'repeat_interval must be float, not: {}'.format(type(interval))
					interval = float(interval)

				self.__snap_data__['repeat_interval'] = interval
				self.changed(repeat_interval=interval)
				

		@ENV.SnapProperty
		class state:

			def get(self, MSG):
				"""()->bool"""
				value = self['value']
				return True if value is not None and value >= .5 else False

		@ENV.SnapProperty
		class count:

			def get(self, MSG):
				"""()->int"""
				return self.__snap_data__['count'] or 0

		@ENV.SnapProperty
		class mode:

			def get(self, MSG):
				"""()->str"""
				return (self.__snap_data__['mode'] or 'NORMAL').upper()

			def set(self, MSG):
				"""(str!)"""
				mode = MSG.args[0]
				if mode is None:
					mode = 'NORMAL'
				else:
					assert isinstance(mode, str), 'mode must be string'
					mode = mode.upper()
					assert mode in ('NORMAL', 'TOGGLE'), 'unrecognized mode {}'.format(repr(mode))
				self.__snap_data__['mode'] = mode
				self.changed(mode=mode)


		@ENV.SnapProperty
		class value:

			def set(self, MSG):
				"(float!)"

				value = MSG.args[0]
				if not value:
					value = 0.0

				value = max(min(value, 1.0), 0.0)

				curr_value = self['value']

				if value == curr_value:
					# non-event (prevent spam)
					return None

				last_time = self['last_time']

				SnapDeviceInput.value.set(self, SnapMessage(value)) # self.changed(value)

				mode = self['mode']

				if value == 1.0:
					'press event'

					count = self['count']
					if not count or not self['last_time'] - last_time < self['repeat_interval']:
						count = self.__snap_data__['count'] = 1
					else:
						count += 1
						self.__snap_data__['count'] = count
						

					submsg = SnapMessage(action='press', source=self, count=count)
					submsg.channel = 'press'
					submsg.source = self

					self.press.__send__(submsg)

					snap_device_event(self, submsg)

					if mode != 'TOGGLE':
						self['value'] = 0.0 # triggers release event

				elif value == 0.0:
					'release event'
					submsg = SnapMessage(action='release', source=self)
					submsg.channel = 'release'
					submsg.source = self

					self.release.__send__(submsg)

					snap_device_event(self, submsg)

	
		@ENV.SnapChannel
		def press(self, MSG):
			"()"
			self['value'] = 1.0

		@ENV.SnapChannel
		def release(self, MSG):
			"()"
			self['value'] = 0.0		


		def __init__(self, **SETTINGS):
			SnapDeviceInput.__init__(self, **SETTINGS)


	ENV.SnapDeviceInputButton = SnapDeviceInputButton
			

	class SnapDeviceInputAxis(SnapDeviceInput):
		# a ranged value, possibly clamped (try to map from 0.0->1.0 or -1.0->1.0 depending on what makes sense)

		__slots__ = []

		#def change(self, MSG):
		#	return self.data()['change']
		#delta = change

		#def range(self, MSG):
		#	return self.data()['range'][:]

		@ENV.SnapProperty
		class delta:

			def get(self, MSG):
				"""()->float"""
				return self.__snap_data__['delta'] or 0.

		@delta.shared
		class change: pass
				

		@ENV.SnapProperty
		class range:

			def get(self, MSG):
				"""()->list(float, float)"""
				return self.__snap_data__['range']# or [0.,1.])[:2]

			def set(self, MSG):
				"(list(float|int,float|int))"
				rnge = MSG.args[0]
				if rnge is None:
					self.__snap_data__['range'] = None
				else:
					minimum = float(rnge[0]) if rnge[0] is not None else None
					maximum = float(rnge[1]) if rnge[1] is not None else None

					self.__snap_data__['range'] = [minimum, maximum]


				# non-event if it stays the same, the value assign will clamp to new range...
				self['value'] = self['value']

				self.changed(range=rnge)

		@ENV.SnapProperty
		class max:
			def get(self, MSG):
				"()->float"
				r = self['range']
				if r:
					return r[-1]
				return None

			def set(self, MSG):
				"(float!)"
				value = MSG.args[0]
				if value is not None:
					value = float(value)
				r = self['range']
				if r:
					r[-1] = value
				else:
					r = [None, value]
				self['range'] = r

		@ENV.SnapProperty
		class min:
			def get(self, MSG):
				"()->float"
				r = self['range']
				if r:
					return r[0]
				return None

			def set(self, MSG):
				"(float!)"
				value = MSG.args[0]
				if value is not None:
					value = float(value)
				r = self['range']
				if r:
					r[0] = value
				else:
					r = [value, None]
				self['range'] = r

		@ENV.SnapProperty
		class value:

			def set(self, MSG):
				"(float!)"
				value = MSG.args[0]

				curr_value = self['value']
				if value == curr_value:
					return None

				if value is None:
					value = 0.

				rnge = self['range']
				if rnge is not None:

					if rnge[0] is not None:
						value = max(rnge[0], value)
					if rnge[1] is not None:
						value = min(rnge[1], value)

				value = float(value)

				SnapDeviceInput.value.set(self, SnapMessage(value))

				submsg = SnapMessage(action='motion', source=self)
				submsg.channel = 'motion'
				submsg.source = self

				self.motion.__send__(submsg)

				snap_device_event(self, submsg)

				self.__snap_data__['delta'] = 0
				# self.__snap_data__['value'] = 0

				#self.changed(delta=delta, change=delta, value=value)

		@ENV.SnapChannel
		def motion(self, MSG):
			"()"
			# emit only; use by assigning to self['value']
			raise NotImplementedError('motion event is emit only')


		def __init__(self, range=None, value=None, **SETTINGS):
			SnapDeviceInput.__init__(self, range=range, value=value, **SETTINGS)



	ENV.SnapDeviceInputAxis = SnapDeviceInputAxis





