
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapEventManager(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class directory:
			'' # dict of events and listeners...

		@ENV.SnapChannel
		def global_device_event(self, MSG):
			return self.event('global_device_event', MSG)
			
		# called by parent...
		def local_device_event(self, PARENT, MSG):
			'' # this one gets sent from SnapContainer.device_event -> SnapContainer['events'].local_device_event(self, MSG)

		def event(self, EVENT, MSG):
			# this design allows for custom events in event handlers, without the event manager having to know what they are...
			status = self['next'].event(EVENT, MSG)
			if status is True:
				'proceed to next, or emit if complete'
			elif status is False:
				'fail, back to start'
			elif status is None:
				'nothing, try again later' # -> maybe send to own method to potentially cancel on unhandled event?
			else:
				raise ValueError(repr(status))


		def define(self, NAME, EVENT):
			'' # EVENTS are to fire in order (like ctrl + v)
			# TODO options can be 'no fail' where it just keeps going no matter what... XXX options will be combo types...

		def undefine(self, NAME):
			''


		def connect(self, NAME, CALLABLE):
			ENV.snap_debug('connect', NAME, CALLABLE)
			# TODO can support multiple connections per-channel...
			# use weakrefs, check if is SnapBoundChannel or not, etc...
			# TODO support '.' to indicate a sub-property of the event that should be listened to for the data?

			#self.changed(connect=NAME, callable=CALLABLE)

		def disconnect(self, NAME, CALLABLE):
			''

	ENV.SnapEventManager = SnapEventManager


def main(ENV):

	SnapContainer = ENV.SnapContainer

	class Test(SnapContainer):

		@property
		def events(self):
			em = self.__snap_data__['__event_manager__']
			if em is None:
				em = self.__snap_data__['__event_manager__'] = ENV.SnapEventManager()
			return em

		def method(self, MSG):
			''

		@ENV.SnapChannel
		def channel(self, MSG):
			''

		def __init__(self):
			SnapContainer.__init__(self)

			#self.events.connect('name',callback|channel)
			self.events.connect('method_event', self.method)
			self.events.connect('channel_event', self.channel)
			# TODO self.events.define('method_event', EventCombo(...))
			# TODO EventCombo are types for Ordered (first to last), Any/All (any order, True once all succeed), or StrictOrdered(ignores=...)

	ENV.__run_gui__(Test)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv())
