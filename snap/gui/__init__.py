
def build(ENV):

	ENV.__build__('snap.gui.events')
	ENV.__build__('snap.gui.SnapGuiDummyWindow')
	ENV.__build__('snap.gui.SnapGuiWindowBase')
	ENV.__build__('snap.gui.SnapGuiBase')

	class SnapGui(object): # TODO SnapNode?

		__slots__ = []

		def load(self, name=None):

			assert getattr(ENV, 'GUI', None) is None, 'gui already initialized?'

			if name is None:
				name = 'QT5'
			name = name.upper()

			# TODO save built gui in a list?  XXX it's in the ENV.__BUILT_MODULES__ list...

			build = None

			if name == 'SDL':
				ENV.__build__('snap.gui.SDL.SnapSDL')
				built = ENV.SnapSDL()

			elif name == 'QT5':
				ENV.__build__('snap.gui.Qt5.SnapQt5')
				built = ENV.SnapQt5()

			else:
				raise NotImplementedError(name)

			ENV.GUI = built

			return built


		def start(self, user=None, **SETTINGS):
			'make sure not already running'
			# can run with no window open?
			raise NotImplementedError('deprecated')

			GUI = getattr(ENV, 'GUI', None)
			if GUI is None:
				GUI = self.load(None) # default

			window = GUI.Window(user=user) # TODO user in window?
			GUI.start_mainloop()

			if SETTINGS.get('headless', False):
				raise NotImplementedError()

				"""
				PROGRAM = MAIN_PROGRAM[0]
				MAINLOOP = PROGRAM.MAINLOOP
				MAINLOOP.start()
				refresh_msg = SnapMessage()
				while MAINLOOP.running():
					PROGRAM._snap_emit(refresh_msg)
				"""

		def preferred_engine(self):
			return ENV.GUI.preferred_engine()

	ENV.gui = SnapGui()
