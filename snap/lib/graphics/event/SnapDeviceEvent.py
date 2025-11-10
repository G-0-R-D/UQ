
def build(ENV):

	SnapEvent = ENV.SnapEvent

	class SnapDeviceEvent(SnapEvent):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapEvent.__init__(self, **SETTINGS)

	ENV.SnapDeviceEvent = SnapDeviceEvent
