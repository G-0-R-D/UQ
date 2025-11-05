
def build(ENV):

	SnapNode = ENV.SnapNode

	SnapMessage = ENV.SnapMessage

	#SnapEvent = ENV.SnapEvent
	#SnapProperty = ENV.SnapProperty
	#SnapOutput = ENV.SnapOutput

	class SnapPrimitive(SnapNode):

		# a primitive is any type that represents basic bytes / data, rather than another SnapNode...

		__slots__ = []

		# TODO SNAP_STRICT_PROPERTIES (only allow designated properties)

		"""
		@property
		def data(self):
			if self.__snap_data__ is None:
				self.__snap_data__ = {}
			if '__data__' not in self.__snap_data__:
				self.__snap_data__['__data__'] = None
			return self.__snap_data__['__data__'] # single value, not dict
		"""
		@ENV.SnapProperty
		class data:

			def get(self, MSG):
				"""()->?"""
				return self.__snap_data__['data']

			def set(self, MSG):
				"""(?)"""
				data = MSG.args[0]
				existing = self.__snap_data__['data']
				self.__snap_data__['data'] = data
				if existing is not data:
					self.changed(data=data)

			def delete(self, MSG):
				del self.__snap_data__['data']


		def __compare__(self, OTHER):

			if isinstance(OTHER, SnapPrimitive):
				self_comp = self['data']
				other_comp = OTHER['data']
			else:
				self_comp = id(self)
				other_comp = id(OTHER)

			if self_comp == other_comp:
				return 0
			elif self_comp < other_comp:
				return -1
			else:
				return 1

		# comparison operators

		def __lt__(self, OTHER): # <
			return self.__compare__(OTHER) < 0

		def __le__(self, OTHER): # <=
			return self.__compare__(OTHER) <= 0

		def __gt__(self, OTHER): # >
			return self.__compare__(OTHER) > 0

		def __ge__(self, OTHER): # >=
			return self.__compare__(OTHER) >= 0

		def __eq__(self, OTHER): # ==
			return self.__compare__(OTHER) == 0

		def __ne__(self, OTHER): #!=
			return self.__compare__(OTHER) != 0



		def __call__(self, *a, **k):
			#assert not (MSG.args or MSG.kwargs), 'no arguments supported in __call__'
			#return self.__snap_input__(self, "value", SnapMessage())
			#return self.data
			raise NotImplementedError('__call__')

		def __bool__(self):
			return bool(self['data'])


		def __init__(self, data=None):
			SnapNode.__init__(self)

			if data is not None:
				self['data'] = data

		def __delete__(self):
			''#self.__snap_data__ = None

		"""
		def __snap_description__(self):
			return {
				#'value':SnapProperty('(value=SnapNode)', return_value=None, output=SnapOutput()),
				'data':SnapProperty(None, return_value=None, output=SnapOutput('()')),
				'set':SnapEvent('(data=SnapNode)', output=SnapOutput('(data=SnapNode)')),
				'changed':SnapEvent(None, output=SnapOutput('(data=SnapNode)')),
			}
		"""

	ENV.SnapPrimitive = SnapPrimitive

