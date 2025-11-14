
def build(ENV):

	ENV.__build__('snap.events.SnapEvent')
	#ENV.__build__('snap.interaction.SnapInteractCombo')

	#ENV.__build__('snap.events.SnapEventManager')





def main(ENV):

	if not getattr(ENV, 'SnapEvent', None):
		build(ENV)

	SnapContainer = ENV.SnapContainer

	#SnapInteractCombo = ENV.SnapInteractCombo

	class Test(SnapContainer):

		@ENV.SnapProperty
		class events:

			def get(self, MSG):
				"()->SnapEventManager"
				m = self.__snap_data__['events']
				if m is None:
					m = self.__snap_data__['events'] = ENV.SnapEventManager()
				return m

			def set(self, MSG):
				"(dict(str:SnapEvent|bool))"
				# TODO subclass should override to perform necessary hookups...

				# values:
				# False = disabled (clear the listeners, delete)
				# True = enabled, use default assign
				# SnapInteractCombo = use this one

				# subclass can just call the super, and then perform the necessary hookups after...?  but super won't know how to handle...

				"""
				user.__init__(interactions={'name':SnapInteractCombo(...)})
				user.interactions.get('name').listen(user.x)
				"""


		@ENV.SnapChannel
		def combo_update(self, MSG):
			"()"
			# get each update on the interactions...?  feedback?

		@ENV.SnapChannel
		def perform_action(self, MSG):
			"()"
			ENV.snap_out('action performed') # TODO change the hotkey to something else here
			# change the combo assignment for the action...

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"

			event_manager = self['events']
			if event_manager:
				event_manager.local_device_event(self, MSG)


		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			# TODO assign as well...
			self['events'].connect('name', self.perform_action)
			

	ENV.__run_gui__(Test, events={'action':True})

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())
