
def build(ENV):

	class SnapRelativeColor(SnapColor):

		__slots__ = []

		# TODO this is same as color (where the color is used to represent a change (from 0)
		#	-- but when the engine data is accessed, we add the offset and then return the result
		#	-- so even engine data will store the color locally in list format, and keep an engine data as well (for efficiency) -- then just set it (r + r % 255, ...) and return it -- maybe indicate if it has changed or not for efficiency?

		def __init__(self, **SETTNGS):
			SnapColor.__init__(self, **SETTINGS)

	ENV.SnapRelativeColor = SnapRelativeColor
