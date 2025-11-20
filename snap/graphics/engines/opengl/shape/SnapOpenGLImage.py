
from OpenGL.GL import *

def build(ENV):

	SnapImage = ENV.SnapImage
	SnapBytes = ENV.SnapBytes

	SnapMessage = ENV.SnapMessage

	snap_extents_t = ENV.snap_extents_t

	ENGINE = ENV.graphics.__current_graphics_build__

	if 1:#ENV.__SNAP_IS_PYTHON__:
		import numpy as np



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
				if pixels is not None:
					ID = self['__engine_data__']

					glBindTexture(GL_TEXTURE_2D, ID)

					glGetTexImage(
						GL_TEXTURE_2D,
						0, # mipmap level
						GL_BGRA, # GL_BGRA ?
						GL_UNSIGNED_BYTE,
						pixels['data'],
						)

					glBindTexture(GL_TEXTURE_2D, 0)

					#arr = np.frombuffer(p, dtype=np.uint8).reshape(HEIGHT, WIDTH, 4)
					#arr[:] = arr[:,:, [2,1,0,3]] # BGRA
					#arr = arr.reshape(HEIGHT * WIDTH * 4)

					#pixels['data'][:] = np.frombuffer(p, dtype=np.uint8)

				return pixels

		def draw(self, CTX):
			# hard coded here (no shader program)

			#ENV.snap_error('image DRAW!')

			# TODO draw image using pre-existing unit rect?  set matrix to fill it?

			#e = self['extents']

			#CTX['engine_context'].drawImage(QRectF(e[0], e[1], e[3]-e[0], e[4]-e[1]), self['__engine_data__'])
			#CTX['image'].save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/TestNode_in_image_draw.png')
			# TODO self.pixels is not being updated!  we need to get pixels from qimage?
			#CTX._image_.__engine_data__().save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/TestNode_in_image_draw.png')
			pass

		def lookup(self, CTX):
			# either use the extents or render and check the alpha of the image...
			# we always have to render to consider clipping!  so either render as solid rect or image with the alpha...
			pass # TODO

		def _assign(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):

			engine_data = self['__engine_data__']

			existing_pixels = self.__snap_data__['pixels'] # SnapBytes if not None

			existing_byte_count = len(existing_pixels) if existing_pixels is not None else 0

			byte_count = int(self._calc_bytes(WIDTH, HEIGHT, BITS_PER_PIXEL))
			changed = not existing_byte_count or existing_byte_count != byte_count
			if changed:

				if existing_pixels is None:
					existing_pixels = self.__snap_data__['pixels'] = SnapBytes()

				existing_pixels.realloc(HEIGHT * WIDTH * 4)

				if BITS_PER_PIXEL == 32:
					engine_format = GL_RGBA
				else:
					raise TypeError('unsupported format', repr(FORMAT), BITS_PER_PIXEL)

				HEIGHT = int(HEIGHT)
				WIDTH = int(WIDTH)

			glBindTexture(GL_TEXTURE_2D, engine_data)

			# TODO: query Image api to get settings
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

			ENV.snap_out('existing pixels', self, existing_pixels['data'].shape, WIDTH, HEIGHT)

			# TODO GL_BGRA?
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, WIDTH,HEIGHT, 0, GL_BGRA, GL_UNSIGNED_BYTE, existing_pixels['data'].data) # flipped in Y

			glBindTexture(GL_TEXTURE_2D, 0)

			self.__snap_data__['format'] = FORMAT
			self.__snap_data__['extents'] = snap_extents_t(0,0,0, WIDTH,HEIGHT,1)



		def _assignXXX(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):

			existing_pixels = self.__snap_data__['pixels'] # SnapBytes if not None
			#existing_pixels = getattr(self, '_ndarray_', None)

			#existing_pixels = getattr(self, '_pixels_', None)
			#existing_byte_count = int(getattr(self, '_byte_count_', 0) or 0)
			
			existing_byte_count = len(existing_pixels) if existing_pixels is not None else 0

			byte_count = int(self._calc_bytes(WIDTH, HEIGHT, BITS_PER_PIXEL))

			changed = not existing_byte_count or existing_byte_count != byte_count
			if changed:

				if existing_pixels is None:
					existing_pixels = self.__snap_data__['pixels'] = SnapBytes()

				#if 1:#XXX existing_pixels is None:
					#existing_pixels = ctypes.create_string_buffer(byte_count)
					#existing_pixels = np.ndarray((HEIGHT, WIDTH, 4), dtype=np.uint8)
				existing_pixels.realloc(HEIGHT * WIDTH * 4)

				#ctypes.resize(existing_pixels, byte_count)


				# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QImage.html#PySide2.QtGui.PySide2.QtGui.QImage.size

				if BITS_PER_PIXEL == 32:
					raise NotImplementedError() # TODO
					#engine_format = Qt5.QImage.Format_ARGB32
				else:
					raise TypeError('unsupported format', repr(FORMAT), BITS_PER_PIXEL)

				#surface = getattr(self, '_snap_engine_data_', None)
				#if surface:
				#	cairo_surface_destroy(surface)
				#	self._snap_engine_data_ = None
				HEIGHT = int(HEIGHT)
				WIDTH = int(WIDTH)

				#existing_pixels = data['pixels'] = np.ndarray((HEIGHT, WIDTH, 4), dtype=np.uint8)

				# stride = width * bytes per pixel (format)
				qimage = Qt5.QImage(existing_pixels['data'].data, WIDTH, HEIGHT, WIDTH * 4, engine_format)

				stride = qimage.bytesPerLine()
				assert stride * HEIGHT == byte_count, 'pixel misalignment {}'.format([stride * HEIGHT, byte_count])

				#self._pixels_ = existing_pixels
				self.__snap_data__['format'] = FORMAT
				self.__snap_data__['extents'] = snap_extents_t(0,0,0, WIDTH,HEIGHT,1)

				self.__snap_data__['__engine_data__'] = qimage

			#data['byte_count'] = byte_count # XXX ?  this is pixel count?  this is width * height * nchannels

			if BYTES is not None:
				# copy pixels
				#snap_memcpy(existing_pixels, PIXELS, byte_count);
				#ctypes.memmove(existing_pixels, PIXELS, byte_count)

				HEIGHT = int(HEIGHT)
				WIDTH = int(WIDTH)

				#arr = BYTES

				arr = BYTES['data'].reshape(HEIGHT, WIDTH, 4)
				arr[:] = arr[:,:, [2,1,0,3]] # BGRA
				arr = arr.reshape(HEIGHT * WIDTH * 4)

				existing_pixels['data'][:] = arr
			else:
				# assign as NULL
				#ctypes.memset(existing_pixels, 0, byte_count)
				#ENV.snap_out("existing pixels assign")
				existing_pixels['data'][:] = 0 # TODO clear to a color?

			# TODO update the QImage, make SnapContext.clear() a drawing operation?
			numpy_to_glimage(existing_pixels['data'], self['__engine_data__'])

			#out('pixels set', w,h, byte_count, ctypes.sizeof(existing_pixels), len(existing_pixels), len(existing_pixels.value))

			# TODO call emit with each arg set?
			self.changed(image=self, size=[WIDTH,HEIGHT], width=WIDTH, height=HEIGHT, format=FORMAT, pixels=BYTES)
			self.changed_data.emit()


		def __init__(self, **SETTINGS):
			SnapImage.__init__(self, **SETTINGS)

			#if not self._snap_engine_data_:
			#	snap_warning('no engine data', type(self._pixels_))

			# TODO so use a QPixmap for the image engine data, use QImage for manipulations?

		def __del__(self):
			gl = self.__snap_data__['__engine_data__']
			if gl:
				glDeleteTextures(1, gl)
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

