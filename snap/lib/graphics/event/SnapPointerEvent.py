
def build(ENV):

	SnapPointerHotkey = ENV.SnapPointerHotkey

	class SnapPointerClickedEvent(SnapPointerHotkey):

		__slots__ = []

	ENV.SnapPointerClickedEvent = SnapPointerClickedEvent

	class SnapPointerDoubleClickedEvent(SnapPointerClickedEvent):

		__slots__ = []

		@ENV.SnapProperty
		def count:

			def get(self, MSG):
				return 2

			set = None

	ENV.SnapPointerDoubleClickedEvent = SnapPointerDoubleClickedEvent
