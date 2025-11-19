


def build(ENV):

	SnapMessage = ENV.SnapMessage

	SnapTexture = ENV.SnapTexture
	#snap_incoming = ENV.snap_incoming
	#snap_out = ENV.snap_out
	#snap_warning = ENV.snap_warning

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLTexture(SnapTexture):

		__slots__ = []

		"""
		QUALITIES = {
			'LOW':CAIRO_FILTER_FAST,
			'NORMAL':CAIRO_FILTER_GOOD,
			'MEDIUM':CAIRO_FILTER_GOOD,
			'HIGH':CAIRO_FILTER_BEST,

			CAIRO_FILTER_FAST:'LOW',
			CAIRO_FILTER_GOOD:'MEDIUM',
			CAIRO_FILTER_BEST:'HIGH',
			}

		EXTENSIONS = {
			'REPEAT':CAIRO_EXTEND_REPEAT,
			'TILE':CAIRO_EXTEND_REPEAT,
			'REFLECT':CAIRO_EXTEND_REFLECT,
			'MIRROR':CAIRO_EXTEND_REFLECT,
			'HOLD':CAIRO_EXTEND_PAD,
			'PAD':CAIRO_EXTEND_PAD,
			None:CAIRO_EXTEND_NONE,

			CAIRO_EXTEND_NONE:None,
			CAIRO_EXTEND_REPEAT:'REPEAT',
			CAIRO_EXTEND_REFLECT:'MIRROR',
			CAIRO_EXTEND_PAD:'PAD',
			}
		"""

		#@snap_incoming
		#def CHANGED(self, SOURCE, *args, **kwargs):
		#	if SOURCE is self._image_:
		#		self.update()

		# no need for CHANGED_DATA (doesn't require reconfig)
		"""
		def quality(self):
			try:
				return self.QUALITIES[self._config_['quality']]
			except:
				return 'LOW'

		def extend(self):
			try:
				return self.EXTENSIONS[self._config_['extend']]
			except:
				return None
		"""

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapOpenGLEngine"""
				return ENGINE

		@ENV.SnapProperty
		class __engine_data__:

			def get(self, MSG):
				"""()->?"""
				# TODO

			#def set(self, MSG):
			#	"""(?)"""

		@ENV.SnapProperty
		class image:
			def get(self, MSG):
				"""()->SnapOpenGLImage"""
				return self.__snap_data__['image']

			def set(self, MSG):
				"""(SnapOpenGLImage!)"""
				image = MSG.args[0]
				if not image:
					self.__snap_data__['image'] = None
				else:
					qimage = image['__engine_data__']
					if not qimage:
						ENV.snap_warning('no qimage on texture image')
					#self['__engine_data__'] = Qt5.QColor(0,0,0) # ? # TODO make a default image?

					self.__snap_data__['image'] = image # TODO re-create __engine_data__?

					"""
					# XXX TODO skip pixmap, just make this a dummy and use the QImage directly when rendering...
					pixmap = self['__engine_data__']
					if not pixmap:
						pixmap = self['__engine_data__'] = Qt5.QPixmap(image['width'], image['height'])
					pixmap.convertFromImage(qimage)
					"""
					
				self.changed(image=image)

				

		@ENV.SnapChannel
		def update(self, MSG):
			self['image'] = self['image']

			"""
			image = self['image']
			if not image:
				self['__engine_data__'] = Qt5.QColor(0,0,0)
				return None
			qimage = image['__engine_data__']
			if not qimage:
				ENV.snap_warning('no qimage on texture')
				return
			#assert image_surface, 'no image surface on Image!'

			# XXX TODO skip pixmap, just make this a dummy and use the QImage directly when rendering...
			pixmap = self['__engine_data__']
			if not pixmap:
				pixmap = self['__engine_data__'] = Qt5.QPixmap(image['width'], image['height'])
			pixmap.convertFromImage(qimage)

			#config = self._config_ or {}
		
			#extend = config.get('extend', CAIRO_EXTEND_NONE)
			#quality = config.get('quality', CAIRO_FILTER_FAST)

			#cairo_pattern_set_extend(surface, extend)
			#cairo_pattern_set_filter(surface, quality)
			#snap_emit(self, "CHANGED")
			self.changed_data.emit()
			self.changed(image=image) # TODO changed?
			"""

		"""
		def set(self, MSG):

			changed = False

			for attr,value in MSG.kwargs.items():

				if attr == 'image':
					self.data()['image'] = value
					#ENV.snap_out('image assigned', value)
					changed = True

				elif attr == 'extend' or attr == 'quality':
					raise NotImplementedError(attr)

					""
					mapping = self.EXTENSIONS if attr == 'extend' else self.QUALITIES
					config = self._config_ or {}
					if value:
						if value.upper() not in mapping:
							warning(attr, 'invalid option', repr(value))
						else:
							config[attr] = mapping[value]

					else:
						if attr in config:
							del config[attr]

					if config:
						self._config_ = config
					else:
						self._config_ = None
					
					changed = True
					""

				else:
					SnapTexture.set(self, SnapMessage(**{attr:value}))

			if changed:
				self.update()
		"""

		def __init__(self, image=None, **SETTINGS):
			SnapTexture.__init__(self, image=image, **SETTINGS)

			#SNAP_INIT(self, SETTINGS,
			#	'extend', 'quality')

	ENGINE.SnapOpenGLTexture = SnapOpenGLTexture
	return SnapOpenGLTexture

