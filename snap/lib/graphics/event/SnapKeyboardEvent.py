
def build(ENV):

	SnapDeviceEvent = ENV.SnapDeviceEvent

	class SnapKeyboardEvent(SnapDeviceEvent):

		__slots__ = []

	ENV.SnapKeyboardEvent = SnapKeyboardEvent

	class SnapKeyboardKeyEvent(SnapDeviceEvent):

		__slots__ = []

	ENV.SnapKeyboardKeyEvent = SnapKeyboardKeyEvent

