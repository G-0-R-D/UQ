
# TODO
"""
break each input into it's own node (keyboard key press, release, mouse motion, press etc...)
then if the args are going to the connected component we save them to send?  with possible converter...  all device inputs are floats...

if we want hotkeys without anything between we can listen to all and break if it isn't a supported (next) event...

assign the hotkey combos as lists, and connect them to the desired property/channel yourself
	- list of combos, each combo can have multiply hotkeys or inputs...

"""

def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapEvent(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class successful:

			# set when event triggers, as a way to communicate to event manager...

			def get(self, MSG):
				"()->bool"
				return bool(self.__snap_data__['successful'])

		def global_device_event(self, MSG):
			pass # this one listens to global device events

		def local_device_event(self, PARENT, MSG):
			# SnapContainer.device_event() -> calls SnapContainer.interactions.local_device_event() which forwards to all of it's assigned events
			pass

	ENV.SnapEvent = SnapEvent
