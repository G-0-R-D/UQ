
# TODO just subclass SnapWindow and add in ability to add elements from scene, render as code nodes, etc...


def build(ENV):

	SnapWindow = ENV.SnapWindow

	class UQWindow(SnapWindow):

		# NOTE: if you don't want a new ENV then use a new SnapWindow and just add the UQGraphics to it...

		__slots__ = []

		@ENV.SnapProperty
		class style:

			'' # TODO set/get strings of names to use maybe as dict?  key:value? '<Type>':'<Shader name>'?
			# TODO sub env would use same graphics as parent?  so same shaders as parent would be ok too?  so style looks up locally or gets from parent ENV.STYLING?  XXX not safe, we want contained ENV...  so window has to have it's own defaults for style, just use names, and we can register new shaders for names if we want to, create new themes...  -- override on the them per-name!

		def __init__(self, **SETTINGS):
			SnapWindow.__init__(self, **SETTINGS)

			# TODO window gets STYLE?  window makes new ENV child instance, assigns own style to it?  creates graphics through own interface, and so can assign own sub ENV to them...
			#	-- NOTE: types will still be the same otherwise, only style would change... XXX nope, they would need to be rebuilt to point to the same ENV!  maybe when the window creates it's graphics it will use the ENV.STYLING['windows'][self] to get the style sheet for the graphic, and then assign the shader to the graphic from there?  and if no local is assigned it uses the global assign?
			# XXX except a UQWindow actually should have and represent it's own ENV!  (one ENV per space! -- and execution then happens per-window too)

			# TODO create internal graphics with local ENV

			# TODO register self with local ENV as APPLICATION?

			# TODO make subcomponents run in full screen (locally), esc to minimize back into scene?  or be able to subdivide the window into 'purposes'?  like how blender has pre-made window layouts?

	ENV.UQWindow = UQWindow

