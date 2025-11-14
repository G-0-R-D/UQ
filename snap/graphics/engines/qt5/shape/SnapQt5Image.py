
# https://doc.qt.io/qtforpython-5/PySide2/QtCore/QTimer.html#PySide2.QtCore.PySide2.QtCore.QTimer.start
"""
Typically, the QImage class is used to load an image file, optionally manipulating the image data, before the QImage object is converted into a QPixmap to be shown on screen. Alternatively, if no manipulation is desired, the image file can be loaded directly into a QPixmap .
"""
# -- so I'm going with a QPixmap is a Texture (which is required to actually render/display the image), and QImage is an Image, hopefully that works out...
# TODO is it necessary to use QPixmap at all?  make texture just act as a dummy for now, and forward the QImage to the render?
def build(ENV):

	Qt5 = ENV.extern.Qt5
	QRectF = Qt5.QRectF
	QImage = Qt5.QImage
	QPainter = Qt5.QPainter

	SnapImage = ENV.SnapImage
	SnapBytes = ENV.SnapBytes

	SnapMessage = ENV.SnapMessage

	#snap_warning = ENV.snap_warning
	#snap_emit = ENV.snap_emit

	#snap_raw = ENV.snap_raw
	snap_extents_t = ENV.snap_extents_t

	ENGINE = ENV.graphics.__current_graphics_build__

	if 1:#ENV.__SNAP_IS_PYTHON__:
		import numpy as np



	def numpy_to_qimage(NUMPY, QIMAGE):

		size = QIMAGE.size()
		w,h = size.width(),size.height()
		img = QImage(NUMPY.data, w, h, w*4, QImage.Format_ARGB32)

		# NOTE: if QImage is already being painted to this will fail, but we shouldn't be changing the pixels of an image that is being actively rendered onto!
		ptr = QPainter(QIMAGE)
		ptr.setCompositionMode(QPainter.CompositionMode_Source) # just a direct copy, replace the pixel with the exact value in the source
		ptr.drawImage(0,0, img)
		ptr.end()

		return QIMAGE

	def qimage_to_numpy(QIMAGE, NUMPY):

		p = QIMAGE.constBits()
		p.setsize(QIMAGE.byteCount())
		local = np.frombuffer(p, dtype=np.uint8)

		if NUMPY is None:
			return local

		NUMPY[:] = local
		return NUMPY

	class SnapQt5Image(SnapImage):

		__slots__ = []

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE

		@ENV.SnapProperty
		class __engine_data__:
			def get(self, MSG):
				"""()->?"""
				qimage = self.__snap_data__['__engine_data__']
				if qimage is None:
					# NOTE: qimage needs to be locally assigned if it is used in a context!
					pixels = self.__snap_data__['pixels']
					if pixels is None:
						pixels = self.__snap_data__['pixels'] = SnapBytes(size=4)
					qimage = self.__snap_data__['__engine_data__'] = QImage(pixels['data'].data, 1,1, 4, QImage.Format_ARGB32)
				return qimage

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
				qimage = self['__engine_data__']
				pixels = self.__snap_data__['pixels']
				if pixels is not None:
					qimage = self['__engine_data__']
					# NOTE: when image is painted to the underlying buffer is copied...  so just always update the buffer just in case (XXX TODO FIXME: get rid of Qt backend!)
					qimage_to_numpy(qimage, pixels['data'])
				return pixels
				"""
				q = self['__engine_data__']
				if q is not None:
					assert q.format() == QImage.Format_ARGB32, 'qimage format is not ARGB; unsupported (TODO)'
					#ENV.snap_out("q is", q, q.width(), q.height(), q.format(), type(q.constBits()), q.bytesPerLine())
					p = q.constBits()
					p.setsize(q.height() * q.width() * 4)
					#B.__snap_data__ = np.ndarray((q.width() * q.height() * 4), buffer=p, strides=[q.bytesPerLine(), 4, 1], dtype=np.uint8)
					# https://stackoverflow.com/questions/45020672/convert-pyqt5-qpixmap-to-numpy-ndarray/50023229#50023229
					#numpy.array(qimg.constBits()).reshape(skimg.shape)
					arr = np.frombuffer(p, np.uint8).copy() # q.constBits() is read only
					view = arr.reshape(q.height(), q.width(), 4)
					view[:] = view[:,:, [2,1,0,3]] # BGRA
					return SnapBytes(data=arr) # NOTE: copy of the data
				return None #SnapImage.pixels(self, MSG)
				"""

		def draw(self, CTX):
			# hard coded here (no shader program)

			#ENV.snap_error('image DRAW!')

			e = self['extents']

			CTX['engine_context'].drawImage(QRectF(e[0], e[1], e[3]-e[0], e[4]-e[1]), self['__engine_data__'])
			#CTX['image'].save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/TestNode_in_image_draw.png')
			# TODO self.pixels is not being updated!  we need to get pixels from qimage?
			#CTX._image_.__engine_data__().save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/TestNode_in_image_draw.png')

		def lookup(self, CTX):
			# either use the extents or render and check the alpha of the image...
			# we always have to render to consider clipping!  so either render as solid rect or image with the alpha...
			pass # TODO

		def _assign(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):

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
					engine_format = Qt5.QImage.Format_ARGB32
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
			numpy_to_qimage(existing_pixels['data'], self['__engine_data__'])

			#out('pixels set', w,h, byte_count, ctypes.sizeof(existing_pixels), len(existing_pixels), len(existing_pixels.value))

			# TODO call emit with each arg set?
			self.changed(image=self, size=[WIDTH,HEIGHT], width=WIDTH, height=HEIGHT, format=FORMAT, pixels=BYTES)


		def __init__(self, **SETTINGS):
			SnapImage.__init__(self, **SETTINGS)

			#if not self._snap_engine_data_:
			#	snap_warning('no engine data', type(self._pixels_))

			# TODO so use a QPixmap for the image engine data, use QImage for manipulations?

		def __delete__(self):
			''

	ENGINE.SnapQt5Image = SnapQt5Image
	return SnapQt5Image

def main(ENV):

	#from snap.core import SNAP_GLOBAL_ENV as ENV
	#from snap import extern, graphics
	#extern.build(ENV)
	#graphics.build(ENV)
	#build(ENV)

	img = ENV.SnapQt5Image(width=100, height=100)

	print(img.data()['__engine_data__'], img.data()['__engine_data__'].width(), img.data()['__engine_data__'].height())

	img.data()['__engine_data__'].save('/home/user/Downloads/test.png')

	img.open('/media/user/CRUCIAL1TB/MyComputer/MEDIA/IMAGES/Funny/0bo3u55w27iz.png')
	img.save('/home/user/Downloads/SnapImage_test2.png')


	import numpy as np
	arr = np.ndarray((480,640,4), dtype=np.uint8)
	arr[:] = 255
	img = ENV.Qt5.QImage(arr, arr.shape[1], arr.shape[0], ENV.Qt5.QImage.Format_ARGB32)
	img.save('/home/user/Downloads/test1.png')
	arr[16:20] = 0
	img.save('/home/user/Downloads/test2.png')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(graphics='QT5'))

