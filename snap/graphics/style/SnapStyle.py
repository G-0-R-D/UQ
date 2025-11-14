
def build(ENV):

	SnapNode = ENV.SnapNode

	GFX = ENV.GRAPHICS

	class SnapStyle(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class base_color:

			def get(self, MSG):
				"()->SnapColor"
				# TODO

			def set(self, MSG):
				"(SnapColor!)"
				color = MSG.args[0]
				# TODO

		# TODO if item is missing, then create new default for it if there is one?  or return the default assigned for it...?  crawl mro until a default is found...?

		# TODO we can register defaults for any shader property, under an appropriate name...?

		# TODO also do defaults for things like colors: BLACK, RED, etc...

		# TODO support loading presets in full or part, so we can just replace a few entries if desired...
		@ENV.SnapChannel
		def load(self, MSG):
			''

		@ENV.SnapChannel
		def reset(self, MSG):
			'' # TODO reset to default profile?
				

	ENV.SnapStyle = SnapStyle
	ENV.STYLE = SnapStyle()
