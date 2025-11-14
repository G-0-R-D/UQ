
def build(ENV):

	SnapMetrics = ENV.SnapMetrics

	class SnapEngineData(SnapMetrics):

		# for any type that stores graphic data (like paint, shape, etc...)

		# TODO class Render(SnapEvent): -> __snap_input__(self, CTX), __snap_output__(self, CTX)

		__slots__ = []

		@ENV.SnapProperty
		class __engine_data__:
			def get(self, MSG):
				"""()->?"""
				return self.__snap_data__['__engine_data__']

			def set(self, MSG):
				"""(?)"""
				self.__snap_data__['__engine_data__'] = MSG.args[0]

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapEngine"""
				return getattr(ENV, 'GRAPHICS', None)

			# TODO allow set, and return if assigned locally?

		@ENV.SnapChannel
		def changed_data(self, MSG): pass
			# to indicate a change that doesn't require reconfiguration (like image pixels change color but image stays same size and format)

		"""
		def __setitem__(self, KEY, VALUE):
			if KEY == '__engine_data__':
				pass

			return SnapMetrics.__setitem__(self, KEY, VALUE)
		"""


		#def __graphics__(self): # XXX deprecated since graphics are now tied to the ENV (different graphics require different task!)
		#	return getattr(ENV, 'GRAPHICS', None)

		# setattr(self, '_graphic_data_', value), not set()

		def __init__(self, **SETTINGS):
			SnapMetrics.__init__(self, **SETTINGS)

			#self['__engine_data__'] = None

		#def __delete__(self):
		#	#SnapMetrics.__delete__(self)
			
		#	#if self.data().get('engine_data'):
		#	#	ENV.snap_warning("memory leak: engine_data still remains!")
		#	return SnapMetrics.__delete__(self)


	ENV.SnapEngineData = SnapEngineData
