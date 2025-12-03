
def build(ENV):

	ENV.__build__('snap.graphics.SnapMatrix')
	ENV.__build__('snap.graphics.SnapMetrics')
	#SnapSpace, XXX SnapTask will fill this role

	ENV.__build__('snap.graphics.SnapEngineData')

	# paint
	ENV.__build__('snap.graphics.paint.SnapPaint')
	ENV.__build__('snap.graphics.paint.SnapColor')
	ENV.__build__('snap.graphics.paint.SnapGradient')
	ENV.__build__('snap.graphics.paint.SnapTexture')

	# shape
	ENV.__build__('snap.graphics.shape.SnapShape')
	ENV.__build__('snap.graphics.shape.SnapImage')
	ENV.__build__('snap.graphics.shape.SnapMesh')
	ENV.__build__('snap.graphics.shape.SnapSpline')
	ENV.__build__('snap.graphics.shape.text.SnapTextMetrics')
	ENV.__build__('snap.graphics.shape.text.SnapTextMarkups')
	ENV.__build__('snap.graphics.shape.SnapText')

	ENV.__build__('snap.graphics.shader.SnapShader')
	# TODO composite, particle, ... TODO implemented as containers with specific shader programs

	ENV.__build__('snap.graphics.SnapContext')

	ENV.__build__('snap.graphics.SnapEngine')

	#imp('snap.graphics.SnapTransformable')
	ENV.__build__('snap.graphics.SnapAssetManager')
	ENV.__build__('snap.graphics.SnapContainer')
	ENV.__build__('snap.graphics.SnapCamera')
	ENV.__build__('snap.graphics.SnapWindow')

	# NOTE: engine is initialized separately as it must be selected

	class SnapGraphics(object):

		__slots__ = ['QT5', 'OPENGL',
			'__current_graphics_build__']

		# TODO use __getattr__ and load a graphics engine when accessed? XXX better to explicitly load it first...

		def __getitem__(self, KEY):

			if isinstance(KEY, str):
				KEY = KEY.upper()
				init = getattr(self, KEY, None)
				if init is not None:
					return init
				if KEY == 'QT5':
					engine = ENV.__build__('snap.graphics.engines.qt5.SnapQt5Engine')
				elif KEY == 'OPENGL':
					engine = ENV.__build__('snap.graphics.engines.opengl.SnapOpenGLEngine')
				else:
					raise NotImplementedError(KEY)

				init = engine()

				setattr(self, KEY, init)

				if getattr(ENV, 'GRAPHICS', None) is None:
					ENV.GFX = ENV.GRAPHICS = init

				return init

			raise KeyError(KEY)

		def load(self, name=None):

			if name is None:
				name = 'QT5'

			return self[name]


	ENV.graphics = SnapGraphics()
