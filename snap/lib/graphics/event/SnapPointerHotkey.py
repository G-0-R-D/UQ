
def build(ENV):

	SnapDeviceEvent = ENV.SnapDeviceEvent

	class SnapPointerEvent(SnapDeviceEvent):

		__slots__ = []


# INPUTS ############################################

	ENV.SnapPointerEvent = SnapPointerEvent

	class SnapPointerButtonEvent(SnapPointerEvent):

		__slots__ = []

	ENV.SnapPointerButtonEvent = SnapPointerButtonEvent

	class SnapPointerMotionEvent(SnapPointerEvent):

		__slots__ = []

	ENV.SnapPointerMotionEvent = SnapPointerMotionEvent


	class SnapPointerWheelEvent(SnapPointerEvent):

		__slots__ = []

		@ENV.SnapProperty
		class scale:

			# so we can change the amount of the output (float)

			def get(self, MSG):
				"()->float"
				# TODO

			def set(self, MSG):
				"(int|float!)"
				# TODO

	ENV.SnapPointerWheelEvent = SnapPointerWheelEvent


# ABSTRACT EVENTS ############################################

	# clicked
	# double clicked (for convenience, clicked accepts a 'count' property)

	class SnapPointerClickedEvent(SnapPointerEvent):

		__slots__ = []

		@ENV.SnapProperty
		class count:

			def get(self, MSG):
				"()->int"
				return self.__snap_data__['count'] or 0

			def set(self, MSG):
				"(int!)"
				# TODO

	ENV.SnapPointerClickedEvent = SnapPointerClickedEvent

	class SnapPointerDoubleClickedEvent(SnapPointerClickedEvent):

		__slots__ = []

		@ENV.SnapProperty
		def count:

			def get(self, MSG):
				return 2

			set = None

	ENV.SnapPointerDoubleClickedEvent = SnapPointerDoubleClickedEvent
