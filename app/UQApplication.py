
# This is the main program logic when running the gui version of snap...  the scene where you can connect nodes together and all that

def build(ENV):

	# TODO build all the UQ components here?

	UQWindow = ENV.UQWindow

	class UQApplication(UQWindow):

		__slots__ = []

		def load(self, MSG):

			GFX = ENV.GRAPHICS

			text = GFX.Text(text='sorry, not implemented yet...')
			w,h = text['size']
			ENV.snap_out('text size', w,h)
			rect = GFX.Spline(description=['L', 0,0, w,0, w,h, 0,h, 'C'], stroke=GFX.Color(0,0,0,1))
			
			self['children'] = [rect, text]

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

