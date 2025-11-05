
# This is the main program logic when running the gui version of snap...  the scene where you can connect nodes together and all that

def build(ENV):

	# TODO build all the UQ components here?

	UQWindow = ENV.UQWindow

	class UQApplication(UQWindow):

		__slots__ = []

		@ENV.SnapProperty
		class render_itemsX:
			def get(self, MSG):

				# TODO return list with HUD, ..., and then actual render items...

				return []

		def load(self, MSG):

			print('load')

			n = ENV.__build__('UQ.TestNode')()
			self.set(item=n)


			win = ENV.GUI['windows'][0]
			ENV.snap_out('win', win)
			#win.fit_to_user_content()
			#win.center()



		def __init__(self):
			UQWindow.__init__(self)


			# TODO ability to add nodes into 'scene'
			#	-- pan around scene with camera

			# TODO text based search to add nodes into scene (wrap into graphical SnapNodeGraphic)
			#	-- using gadgets for the text entry and all that...

			# TODO want ability to attach/remove device input from a node in the scene, so we can 'use it' or stop...  like a videogame

			ENV.TASKS.callback(self.load)

	#ENV.UQApplication = UQApplication # XXX not visible (there can be only one)
	return UQApplication

