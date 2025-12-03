
import numpy

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glGenTextures = OpenGL.glGenTextures
	glTexParameterf = OpenGL.glTexParameterf
	glDeleteTextures = OpenGL.glDeleteTextures
	glBindTexture = OpenGL.glBindTexture
	glGetTexImage = OpenGL.glGetTexImage
	glTexImage2D = OpenGL.glTexImage2D

	GL_TEXTURE_2D = OpenGL.GL_TEXTURE_2D
	GL_BGRA = OpenGL.GL_BGRA
	GL_RGBA = OpenGL.GL_RGBA
	GL_UNSIGNED_BYTE = OpenGL.GL_UNSIGNED_BYTE
	GL_TEXTURE_WRAP_S = OpenGL.GL_TEXTURE_WRAP_S
	GL_TEXTURE_WRAP_T = OpenGL.GL_TEXTURE_WRAP_T
	GL_CLAMP_TO_EDGE = OpenGL.GL_CLAMP_TO_EDGE
	GL_TEXTURE_MIN_FILTER = OpenGL.GL_TEXTURE_MIN_FILTER
	GL_TEXTURE_MAG_FILTER = OpenGL.GL_TEXTURE_MAG_FILTER
	GL_LINEAR = OpenGL.GL_LINEAR
	GL_MIRRORED_REPEAT = OpenGL.GL_MIRRORED_REPEAT
	GL_REPEAT = OpenGL.GL_REPEAT


	SnapImage = ENV.SnapImage
	SnapBytes = ENV.SnapBytes

	SnapMessage = ENV.SnapMessage

	snap_extents_t = ENV.snap_extents_t

	ENGINE = ENV.graphics.__current_graphics_build__


	def numpy_to_glimage(NUMPY, ID):

		"""
		size = QIMAGE.size()
		w,h = size.width(),size.height()
		img = QImage(NUMPY.data, w, h, w*4, QImage.Format_ARGB32)

		# NOTE: if QImage is already being painted to this will fail, but we shouldn't be changing the pixels of an image that is being actively rendered onto!
		ptr = QPainter(QIMAGE)
		ptr.setCompositionMode(QPainter.CompositionMode_Source) # just a direct copy, replace the pixel with the exact value in the source
		ptr.drawImage(0,0, img)
		ptr.end()
		"""
		raise NotImplementedError()

		return ID

	class SnapOpenGLImage(SnapImage):

		__slots__ = []

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapOpenGLEngine"""
				return ENGINE

		@ENV.SnapProperty
		class __engine_data__:
			def get(self, MSG):
				"()->int"
				ID = self.__snap_data__['__engine_data__']
				if ID is None:
					#pixels = self.__snap_data__['pixels']
					#if pixels is None:
					#	pixels = self.__snap_data__['pixels'] = SnapBytes(size=4)
					ID = self.__snap_data__['__engine_data__'] = glGenTextures(1)
					# TODO verify ID?
				return ID



		@ENV.SnapProperty
		class pixels:
			# https://www.qtcentre.org/threads/32932-PyQt-code-to-draw-image-from-raw-data?s=0378cf3aaec050b6e0d662cf49c73f94&p=156183#post156183

			def get(self, MSG):
				"""()->SnapBytes"""
				# TODO pixels(self, MSG): pull QIMage.constBits() into pixels buffer?  or make new buffer...
				# https://medium.com/@bgallois/numpy-ndarray-qimage-beware-the-trap-52dcbe7388b9
				"""
				def getImage(pixmap):
				   qimage = pixmap.convertToFormat(QImage.Format_RGB888)
				   array = np.ndarray((qimage.height(), qimage.width(), 3), buffer=qimage.constBits(), strides=[qimage.bytesPerLine(), 3, 1], dtype=np.uint8)
				   return array
				"""

				pixels = self.__snap_data__['pixels']
				if pixels is None:
					w,h = self['size']
					fmt = 4 # TODO
					#pixels = SnapBytes(size=w*h*4)
					pixels = SnapBytes()
					pixels.realloc(w*h*4)
					# but we don't assign locally
				else:
					ENV.snap_warning('pixels exist')

				ID = self['__engine_data__']

				glBindTexture(GL_TEXTURE_2D, ID)

				#ENV.snap_out('pixels data', pixels['data'])

				glGetTexImage(
					GL_TEXTURE_2D,
					0, # mipmap level
					GL_RGBA, # GL_BGRA ? TODO when saving
					GL_UNSIGNED_BYTE,
					pixels['data'],
					)

				glBindTexture(GL_TEXTURE_2D, 0)

				#arr = np.frombuffer(p, dtype=np.uint8).reshape(HEIGHT, WIDTH, 4)
				#arr[:] = arr[:,:, [2,1,0,3]] # BGRA
				#arr = arr.reshape(HEIGHT * WIDTH * 4)

				#pixels['data'][:] = np.frombuffer(p, dtype=np.uint8)

				#ENV.snap_out("pixels", pixels['data'], self['size'])

				return pixels

		def draw(self, CTX):
			# hard coded here (no shader program)

			#ENV.snap_error('image DRAW!')

			# TODO draw image using pre-existing unit rect?  set matrix to fill it?

			#e = self['extents']

			pass

		def lookup(self, CTX):
			# either use the extents or render and check the alpha of the image...
			# we always have to render to consider clipping!  so either render as solid rect or image with the alpha...
			pass # TODO

		def _assign(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):

			engine_data = self['__engine_data__']

			#existing_pixels = self.__snap_data__['pixels'] # SnapBytes if not None

			ext = self['extents']
			if ext is None:
				w = h = 0
			else:
				w,h = self['size']
			#existing_byte_count = len(existing_pixels) if existing_pixels is not None else 0
			existing_byte_count = w * h * 4

			HEIGHT = int(HEIGHT)
			WIDTH = int(WIDTH)

			byte_count = int(self._calc_bytes(WIDTH, HEIGHT, BITS_PER_PIXEL))
			changed = not existing_byte_count or existing_byte_count != byte_count
			if changed:

				#if existing_pixels is None:
				#	existing_pixels = self.__snap_data__['pixels'] = SnapBytes()

				#existing_pixels.realloc(HEIGHT * WIDTH * 4)

				if BITS_PER_PIXEL == 32:
					engine_format = GL_RGBA
				else:
					raise TypeError('unsupported format', repr(FORMAT), BITS_PER_PIXEL)

			glBindTexture(GL_TEXTURE_2D, engine_data)

			# TODO: query Image api to get settings
			#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
			#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

			#ENV.snap_out('existing pixels', self, existing_pixels['data'].shape, WIDTH, HEIGHT)

			# TODO GL_BGRA?
			if BYTES is not None:
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, WIDTH,HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, BYTES['data'].data) # flipped in Y
			else:
				#arr = numpy.zeros((HEIGHT*WIDTH*4), dtype=numpy.uint8)
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, WIDTH,HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)#arr.data) # flipped in Y

			glBindTexture(GL_TEXTURE_2D, 0)

			self.__snap_data__['format'] = FORMAT
			self.__snap_data__['extents'] = snap_extents_t(0,0,0, WIDTH,HEIGHT,1)




		def __init__(self, **SETTINGS):
			SnapImage.__init__(self, **SETTINGS)

			#if not self._snap_engine_data_:
			#	snap_warning('no engine data', type(self._pixels_))

			# TODO so use a QPixmap for the image engine data, use QImage for manipulations?

		def __del__(self):
			gl = self.__snap_data__['__engine_data__']
			if gl is not None:
				glDeleteTextures(1, [gl])
				del self.__snap_data__['__engine_data__']

	ENGINE.SnapOpenGLImage = SnapOpenGLImage
	return SnapOpenGLImage

def main(ENV):

	import os
	THISDIR = os.path.realpath(os.path.dirname(__file__))

	GFX = ENV.GRAPHICS

	#os.path.join(ENV.SNAP_PATH, 

	asset = os.path.join(ENV.SNAP_PATH, 'demo/snap/graphics/gtk-hamster experiments/assets/oxy.png')

	img = GFX.Image(filepath=asset)


	img.save(os.path.join(THISDIR, 'SnapOpenGLImage_test.png'))

	#from snap.core import SNAP_GLOBAL_ENV as ENV
	#from snap import extern, graphics
	#extern.build(ENV)
	#graphics.build(ENV)
	#build(ENV)
	''

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OPENGL'))

