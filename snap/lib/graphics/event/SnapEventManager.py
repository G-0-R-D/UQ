
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapEventManager(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class directory:
			'' # dict of events and listeners...

		@ENV.SnapChannel
		def global_device_event(self, MSG):
			'' # this one listens to global devices

		def local_device_event(self, PARENT, MSG):
			'' # this one gets sent from SnapContainer.device_event -> SnapContainer['events'].local_device_event(self, MSG)



		def assign(self, NAME, HANDLER):
			'' # assign the event handler to the name, when it fires it sends to listeners


		def connect(self, NAME, CALLABLE):
			ENV.snap_debug('connect', NAME, CALLABLE)
			# TODO can support multiple connections per-channel...
			# use weakrefs, check if is SnapBoundChannel or not, etc...
			# TODO support '.' to indicate a sub-property of the event that should be listened to for the data?

		def disconnect(self, NAME, CALLABLE):
			''

	ENV.SnapEventManager = SnapEventManager
