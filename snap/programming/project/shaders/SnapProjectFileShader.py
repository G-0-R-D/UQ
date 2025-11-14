
def build(ENV):

	SnapShader = ENV.SnapShader

	class SnapProjectFileShader(SnapShader):

		__slots__ = []

		@ENV.SnapProperty
		class module:

			def get(self, MSG):
				"()->dict"
				return self.__snap_data__['module']

			def set(self, MSG):
				"(dict!)"
				module = MSG.args[0]
				if module is not None:
					assert isinstance(module, dict) and 'filepath' in module
				self.__snap_data__['module'] = module
				self.changed(module=module)

		@ENV.SnapChannel
		def changed(self, MSG):
			"()"
			return SnapShader.changed(self, MSG)

		@ENV.SnapChannel
		def update(self, MSG):
			"()"
			return SnapShader.update(self, MSG)

		def draw(self, CTX):
			'' # TODO just colored block for extents with filename?

		def lookup(self, CTX):
			'register the module as subelement -- and the component that is clicked if it is open and has components...'

		def __init__(self, **SETTINGS):
			SnapShader.__init__(self, **SETTINGS)

	ENV.SnapProjectFileShader = SnapProjectFileShader
