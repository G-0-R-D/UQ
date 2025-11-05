
def build(ENV):

	class SnapTextMarkups(object):

		__slots__ = ['__parent__']

		def nearest(self, INDEX):
			'' # TODO make this a middle out?

		def define(self, INDEX, **SETTINGS):
			''

		def remove(self, INDEX, *NAMES):
			''

		def move(self, CURRENT_INDEX, NEW_INDEX, *NAMES):
			'' # overlapping names are overwritten

		def clear_channels(self, *NAMES):
			'' # TODO and within span range?

		def __setitem__(self, KEY, VALUE):
			'' # TODO if key is int and value is dict?

		def __getitem__(self, KEY):
			'' # if is int or slice then return within range?

		def __init__(self, PARENT):

			# TODO maybe the better model is just (index, {**SETTINGS}) ?  then we can just binary search?  and iterate much easier than a dictionary...  then we make it possible to iterate through just a single channel?

			self.__parent__ = PARENT

	ENV.SnapTextMarkups = SnapTextMarkups
