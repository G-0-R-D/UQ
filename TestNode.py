
def build(ENV):

	SnapContainer = ENV.SnapContainer
	
	#SnapEvent = ENV.SnapEvent
	#SnapProperty = ENV.SnapProperty
	#SnapAttachment = ENV.SnapAttachment

	class TestNode(SnapContainer):

		__slots__ = []

		def draw(self, CTX):
			#ENV.snap_out("test draw()")
			return SnapContainer.draw(self, CTX)

		def __init__(self):
			SnapContainer.__init__(self)


			GFX = ENV.GRAPHICS

			text = GFX.Text(text='sorry not implemented yet...\n')
			graphic = GFX.Spline(description=['L',0,0, 100,0, 100,100, 0,100], fill=GFX.Color(1., .5, .5, 1.))

			ENV.snap_out('text', text['text'], text['extents'][:])

			self.set(children=[text])

			#ENV.snap_test_out(self['item'] is graphic)
			#ENV.snap_out(self['item'])

			ENV.snap_out('render_items', list(self['render_items']))

			ENV.snap_out("init size", self['extents'][:])

			ENV.snap_out('test node init ok.')

	return TestNode
