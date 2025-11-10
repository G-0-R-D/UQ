
def build(ENV):

	SnapEvent = ENV.SnapEvent

	class SnapEventCombo(SnapEvent):

		__slots__ = []

		def get(self, NAME):
			''

		def set(self, *EVENTS, **SETTINGS):
			'' # EVENTS are in-order of occurrence...

		# TODO use __getitem__, __setitem__ to manage?  access by index...

		"""
		@ENV.SnapProperty
		class interactions:
			# just a list of 'hotkeys' or other interactions that must all evaluate to true (in order) to "succeed" or send()

			def get(self, MSG):
				"()->SnapInteract[]"
				''

			def set(self, MSG):
				"(SnapInteract[])"
		"""

		# TODO local and global events come into this, and then we send them to the 'next' waiting to evaluate, or bust...?
		#	-- there might be different combo logic as well, make more classes as they are discovered...

		# the interaction combos get assigned to properties, and then the triggering of the combo (at least locally) happens in a hard-coded way, where the device_event() of the container would forward events to the properties...  with default behaviour supported...

	"""
	user can listen to combo (argumentless event), or to a specific interaction node to get it's argument (when the event succeeds)
		-- listen to combo, but you can set which element the output argument comes from, if desired...

	interaction combo property can connect the device_event to combo?  or should they register to a list that device_event can find?  or should device_event just scan for SnapInteractCombo properties? (slow)
		-- class can implement device_event handler that forwards the events to the combos!
	"""

	ENV.SnapEventCombo = SnapEventCombo


