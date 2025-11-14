
# TODO the keys are just dicts: TODO or named tuple?
"""
key = dict(
	interpolation=<linear|bezier|...>,
	x=float,
	y=float,
	#selected=False # XXX just make selections of keys separately?  maybe also indicate the interpolation separately?  the key is just the x (time),y (value) graph representation of the key?  except bezier might need handles...  so we just add the 2 extra coordinates for each handle?
	#	-- do this like a spline description?  'L' for linear followed by keys, and then 'B' for bezier followed by the L C R coordinates?
	#	-- this is packed into a more efficient representation internally?
)
"""

# keys are assigned to an animation channel (which reduces to a fundamental type like a float or matrix or string... and then the channel sends the update to the targets it drives...)
# the timeline lists the channels with the keys...  and is used to set the time for all

# then we add them into a channel, the channel can drive a connectable?  or a compatible property?

# AnimationChannel = Spline, with 'type' attached and targets to send changes in type to (type has to map to keys somehow)


# TODO scenes have timeline, tracks can be represented with image planes...  so we can composite right into the scene...

# 2 types of animation: timeline (at this time, set the value) or progressive (keep on iterating through the keys until finished)
#	-- do progressive by creating temporary timeline?  set the start offset to the start time?  or just init it, and then keep advancing it...

# so there is a global timeline for the scene/env, and then there are subtimelines that have offsets (or define a global start/end relative to global timeline)
#	-- temporary timelines for application animations can be set to start at the start time, and then we can just set next/current frame...
# TODO make a new timeline for each mainloop iteration!  then add all the new elements to it, and play it out...

# TODO make interpolation a normalized representation of a channel curve, a spline, and then map that normalized range to the timeline range when assigning it to a channel?

# TODO calculate inbetween frames once they are loaded...  have current section, previous section, and next section?  or maybe just calculate from current position on demand?  just calculate next position based on current value, and next value (depending on direction)
#	-- calculation is just 'linear', 'bezier', 'smooth', 'constant'
#	-- TODO bezier can 'break' the handles so they move independently?  creating a hard v possibility...  'locked' property


def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapAnimationChannel(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class targets:

			def get(self, MSG):
				"()->list(*SnapNode)"
				return self.__snap_data__['targets']

			def set(self, MSG):
				'list(*SnapNode)"
				# TODO targets need to be nodes that wrap whole nodes or callable (channel/property) -- so the translation is a separate step?

				self.changed(targets=None) # TODO

		# TODO target?

		# TODO curve extend mode before and after range?  extrapolation

		@ENV.SnapProperty
		class keys:

			def get(self, MSG):
				"()->list"
				# TODO

			def set(self, MSG):
				"()"
				# TODO we can assign a spline and generate the keys from it based on timeline range?  or we can assign keys directly?
				# use a description like spline accepts?

		# TODO datatype?  we have to map the key values (floats) to the animatable property (which gets sent to the targets upon change)

		# TODO make renderable, and if it is rendered then create a display for it...

		def __init__(self, *targets, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			if targets:
				self['targets'] = self['targets'] + targets
