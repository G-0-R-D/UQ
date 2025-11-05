
def build(ENV):

	snap_time = ENV.snap_time

	SnapMessage = ENV.SnapMessage

	SnapDevice = ENV.SnapDevice
	#SnapDeviceNode_emit_event = ENV.SnapDeviceNode_emit_event
	#SnapDeviceNode_emit_aggregate_event = ENV.SnapDeviceNode_emit_aggregate_event

	SnapDeviceInputAxis = ENV.SnapDeviceInputAxis
	SnapDeviceInputButton = ENV.SnapDeviceInputButton
	SnapDeviceGroup = ENV.SnapDeviceGroup


	# TODO use this for each axis, call it SnapDeviceInputWheelAxis
	class SnapDeviceInputWheelAxis(SnapDeviceInputAxis): # TODO make a generalized input of an axis that always returns to 0 after each value change...  (SnapDeviceInputAxisLever?)

		# TODO need better wheel api, make wheel a single structure?  listen to the inputs and re-emit local 'scroll' event?

		__slots__ = []

		# TODO scrolling is like a button push, it enters the value then returns to 0.0 (but silently)

		@ENV.SnapProperty
		class value:

			def set(self, MSG):
				"(float!)"

				SnapDeviceInputAxis.value.set(self, MSG)

				change = self['delta']
				if change != 0:
					self.motion.__send__(SnapMessage(action='motion', source=self))
				#if change > 0:
				#	self.up.__send__(SnapMessage(action='motion', source=self))
				#elif change < 0:
				#	self.down.__send__(SnapMessage(action='motion', source=self))

				self.__snap_data__['delta'] = self.__snap_data__['value'] = 0. # quietly back to 0

		# TODO horizontal scrolling!  maybe just support a vector in any direction and magnitude?
		# TODO implement a wheel with 2 InputAxes, so we can represent each axis direction (like position does)

		"""
		@ENV.SnapChannel
		def up(self, MSG):
			"()"
			self['value'] = 1.0

		@ENV.SnapChannel
		def down(self, MSG):
			"()"
			self['value'] = -1.0
		"""

		def __init__(self, **SETTINGS):
			SnapDeviceInputAxis.__init__(self, range=[-1.0, 1.0], **SETTINGS)


	class SnapDevicePointer(SnapDevice):

		__slots__ = []

		"""
		SnapDevicePointer

			Group("POSITION")
				Input("X")
				Input("Y")

			Group("BUTTONS")
				Input("LEFT")
					{Input("PRESSURE")}
				Input("MIDDLE")
					{Input("WHEEL MIDDLE")}
				Input("RIGHT")
				
			Group("WHEELS")
				Input("MIDDLE") // and parented to middle button

			Input("PRESSURE") // and parented to left button

		"""

		@ENV.SnapChannel
		def generate_eventXXX(self, MSG):

			EVENT = MSG.args[0]
			code, direction, pressure, global_position, time = MSG.unpack_kwargs('code', None, 'direction', None, 'pressure', None, 'global_position', None, 'time', None)
			EXTRAS = {k:v for k,v in MSG.kwargs.items() if k not in ('code','direction','pressure','global_position','time')}

			if time is None:
				time = snap_time()

			if EVENT == 'PRESS' or EVENT == 'RELEASE':

				if code is not None:
					button = self.find(code) # TODO find?
					if button:
						button.generate_event(EVENT, time=time, **EXTRAS)
					else:
						ENV.snap_warning("no button for \"%s\" event" % EVENT)

				else:
					ENV.snap_warning("no button code for pointer \"%s\" event" % EVENT)

			elif EVENT == "SCROLL": # TODO scroll is 'motion' and gets reset after each?

				if direction is None:
					ENV.snap_warning("no direction for scroll event!")

				else:

					# scroll first wheel
					if code is not None:
						wheel = self.find(code)
						# TODO verify is wheel? how?
					else:
						wheel = self.find("WHEELS", "MIDDLE")

					if not wheel:
						ENV.snap_warning("no wheel for scroll event!")
					else:
						# verify is a wheel?

						# normalized values
						if direction > 0: direction = 1.
						else: direction = -1.
				
						wheel.set(value=direction, time=time)

						wheel.__emit_event__("MOTION", direction=direction, time=time, **extras)

						wheel.set(value=0.0) # reset to 0 after event completes

			elif EVENT == "PRESSURE":

				if pressure is not None:
					pressure_input = self.find("BUTTONS", "LEFT", "PRESSURE")
					if not pressure_input:
						ENV.snap_warning("no pressure input found on pointer")
					else:
						pvalue = pressure_input.value()
						if pvalue is not None and pvalue == pressure:
							pass # no change
						else:
							pressure_input.set(value=pressure, time=time)
							pressure_input.__emit_event__("CHANGE", pressure=pressure, time=time, **extras) # what to call event? "CHANGE" or "MOTION"?  general "CHANGE" should probably be used when a more specific name doesn't fit...

				else:
					ENV.snap_warning("no pressure in pressure event!")

			elif EVENT == "MOTION":
				# position global(x,y)

				position = self.find("POSITION")
				if not position:
					ENV.snap_warning("no position on pointer for motion event")
				else:
					x_input = position.find("X")
					y_input = position.find("Y")

					if not (x_input and y_input):
						ENV.snap_warning("no x,y inputs on position", position)
					else:
						# send
						if not global_position:
							ENV.snap_warning("MOTION requires \"global_position\" argument")
						else:
							position.set(time=time)
							x_input.set(value=global_position[0], time=time)
							y_input.set(value=global_position[1], time=time)

							self.__emit_aggregate_event__([x_input, y_input], "MOTION", **extras)

			else:
				ENV.snap_warning("undefined pointer event", EVENT)

			return None


		def __init__(self, *description, **SETTINGS):
			SnapDevice.__init__(self, **SETTINGS)

			#if self['_inputs_by_id_']:
			#	ENV.snap_warning("pointer device already has configuration, must be cleared before configuring (or create new device)")
			#	return None

			# if no defaults provided then use a default configuration

			def fake_codes():
				# TODO proper map / device codes
				# NOTE: proper codes could be assigned after init, by accessing the inputs and assigning their codes, so we always start with fake codes?  might make code collisions problematic though...
				i = 0
				while 1:
					i += 1
					yield i
			fake_code = fake_codes()

			# TODO this should query that actual device info and generate inputs for it, but just doing this for now
			# -- arg should be device_id to generate inputs for...  (expected to be mouse, tablet, or touch type?)

			"""
			BUTTONS
				LEFT_BUTTON
					PRESSURE: range(0.,1.)
				MIDDLE_BUTTON
					WHEEL: range(-1,1.)
				RIGHT_BUTTON

			POSITION
				X
				Y

			WHEELS
				WHEEL # same wheel as middle button!  just listed in wheels grouping....

			PRESSURES:
				PRESSURE # same pressure
			"""

			WHEEL_X = SnapDeviceInputWheelAxis(name='x', code=next(fake_code))
			WHEEL_Y = SnapDeviceInputWheelAxis(name='y', code=next(fake_code))
			WHEEL = SnapDeviceGroup(name='wheel', children=[WHEEL_X, WHEEL_Y])
			WHEELS_GROUP = SnapDeviceGroup(name='wheels', children=[WHEEL])

			#WHEEL = SnapDeviceInputWheel(name='wheel', code=next(fake_code), range=[-1.,1.])
			PRESSURE = SnapDeviceInputAxis(name='pressure', code=next(fake_code), range=[0.,1.])
			PRESSURE_GROUP = SnapDeviceGroup(name='pressures', children=[PRESSURE])

			BUTTON_LEFT = SnapDeviceInputButton(name='left', code=next(fake_code), children=[PRESSURE], mode='TOGGLE')
			BUTTON_MIDDLE = SnapDeviceInputButton(name='middle', code=next(fake_code), children=[WHEEL], mode='TOGGLE')
			BUTTON_RIGHT = SnapDeviceInputButton(name='right', code=next(fake_code), mode='TOGGLE')
			BUTTONS_GROUP = SnapDeviceGroup(name='buttons', children=[BUTTON_LEFT, BUTTON_MIDDLE, BUTTON_RIGHT])

			X_AXIS = SnapDeviceInputAxis(name="x", code=next(fake_code))
			Y_AXIS = SnapDeviceInputAxis(name="y", code=next(fake_code))
			POSITION = SnapDeviceGroup(name='position', children=[X_AXIS, Y_AXIS])

			self['children'] = [BUTTONS_GROUP, POSITION, WHEELS_GROUP, PRESSURE_GROUP]

	ENV.SnapDevicePointer = SnapDevicePointer
	return SnapDevicePointer
			

def main(ENV):

	pointer = ENV.SnapDevicePointer()

	queue = [(0, pointer)]
	while queue:
		depth,node = queue.pop(0)
		print('.'*depth, node['name'], node['code'], node.__class__.__name__)
		
		queue = [(depth+1, i) for i in node['children']] + queue


