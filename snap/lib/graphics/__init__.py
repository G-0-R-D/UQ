
def build(ENV):

	B = ENV.__build__

	B('snap.lib.graphics.SnapMatrix')
	B('snap.lib.graphics.SnapMetrics')
	#SnapSpace, XXX SnapTask will fill this role

	B('snap.lib.graphics.SnapEngineData')

	# paint
	B('snap.lib.graphics.paint.SnapPaint')
	B('snap.lib.graphics.paint.SnapColor')
	B('snap.lib.graphics.paint.SnapGradient')
	B('snap.lib.graphics.paint.SnapTexture')

	# shape
	B('snap.lib.graphics.shape.SnapShape')
	B('snap.lib.graphics.shape.SnapImage')
	B('snap.lib.graphics.shape.SnapMesh')
	B('snap.lib.graphics.shape.SnapSpline')
	B('snap.lib.graphics.shape.text.SnapTextMetrics')
	B('snap.lib.graphics.shape.text.SnapTextMarkups')
	B('snap.lib.graphics.shape.SnapText')

	B('snap.lib.graphics.shader.SnapShader')
	# TODO composite, particle, ... TODO implemented as containers with specific shader programs

	B('snap.lib.graphics.SnapContext')

	B('snap.lib.graphics.SnapEngine')

	#imp('snap.lib.graphics.SnapTransformable')
	B('snap.lib.graphics.SnapContainer')
	B('snap.lib.graphics.SnapCamera')
	B('snap.lib.graphics.SnapWindow')

	# NOTE: engine is initialized separately as it must be selected

	class SnapGraphics(object):

		__slots__ = ['QT5', 'OPENGL',
			'__current_graphics_build__']

		# TODO use __getattr__ and load a graphics engine when accessed? XXX better to explicitly load it first...

		def load(self, name=None):

			if name is None:
				name = 'QT5'
			name = name.upper()

			init = getattr(self, name, None)
			if init is not None:
				# NOTE: user can still build a custom engine by loading it and then initializing the SnapXEngine(**k) with custom settings
				return init

			if name == 'QT5':
				engine = B('snap.lib.graphics.engines.qt5.SnapQt5Engine')

			elif name == 'OPENGL':
				engine = B('snap.lib.graphics.engines.opengl.SnapOpenGLEngine')

			else:
				raise NotImplementedError(name)

			init = engine()

			setattr(self, name, init)

			if getattr(ENV, 'GRAPHICS', None) is None:
				ENV.snap_out("init graphics", init)
				ENV.GFX = ENV.GRAPHICS = init

			return init

	ENV.graphics = SnapGraphics()
