

def build(ENV):

	SnapPaint = ENV.SnapPaint

	SnapMessage = ENV.SnapMessage

	class SnapTexture(SnapPaint):

		__slots__ = []

		#__slots__ = ['_image_', '_config_']

		@ENV.SnapProperty
		class image:

			def get(self, MSG):
				"""()->SnapImage"""
				return self.__snap_data__['image']

			def set(self, MSG):
				"""(SnapImage)"""

				existing = self.__snap_data__['image']
				if existing is not None:
					existing.changed.ignore(self.changed)
					existing.changed_data.ignore(self.changed_data)

				image = MSG.args[0]
				if image is not None:
					assert isinstance(image, ENV.SnapImage), 'not an image: {}'.format(repr(type(image)))
					image.changed.listen(self.changed)
					image.changed_data.listen(self.changed_data)

				self.__snap_data__['image'] = image


		@ENV.SnapChannel
		def changed_data(self, MSG): # XXX drop this, just use changed and look for extents change or not?
			'pixels changed, in-place' # TODO changed = extents changed, otherwise is changed_data implicitly?  ie. don't need changed_data?

		@ENV.SnapChannel
		def changed(self, MSG):

			if MSG.source is self['image']:
				'subclass might need to update data'
				#ENV.snap_out('update()')
				#self.update()

			return SnapPaint.changed(self, MSG)

		@ENV.SnapChannel
		def update(self, MSG):
			pass

		# TODO elif CHANNEL == 'config'?

		@ENV.SnapChannel
		def set(self, MSG):
			"""(image=SnapImage)"""
			return SnapPaint.set(self, MSG)

		def __init__(self, image=None, **SETTINGS):
			SnapPaint.__init__(self, **SETTINGS)

			#self['image'] = None
			self['__config__'] = None # dict if used (with engine type values)

			if image is not None:
				self['image'] = image


	ENV.SnapTexture = SnapTexture

