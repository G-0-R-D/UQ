
# https://pillow.readthedocs.io/en/stable/reference/Image.html
from PIL import Image as PILImage # XXX temporary, replace with ffmpeg loader when ready?

def build(ENV):

	SnapShape = ENV.SnapShape
	SnapBytes = ENV.SnapBytes
	SnapString = ENV.SnapString
	SnapMetrics = ENV.SnapMetrics
	snap_extents_t = ENV.snap_extents_t

	#SnapArgSpec = ENV.SnapArgSpec
	SnapMessage = ENV.SnapMessage

	#SNAP_INIT = ENV.SNAP_INIT

	import numpy as np # XXX TODO move elsewhere, extern?
	import os # XXX

	#ENV.SnapImage_MAX_BYTE_SIZE = 25000 # TODO

	#ENV.SnapImage_FORMATS = {
	{	"RGBA":32,
		"RGBA8":32,
		"32":32,

		"RGB":24,
		"RGB8":24,
		"24":24,

		"BYTE":8,
		"GREY":8,
		# indexed?
		"8":8,

		"BIT":1,
		"1":1,
	}

	class SnapImage(SnapShape):

		__slots__ = []

		MAX_BYTE_SIZE = 25000 # TODO

		FORMATS = {
			"RGBA":32,
			"RGBA8":32,
			"32":32,

			"RGB":24,
			"RGB8":24,
			"24":24,

			"BYTE":8,
			"GREY":8,
			# indexed?
			"8":8,

			"BIT":1,
			"1":1,
		}

		#__slots__ = [
		#	#'_pixels_',
		#	'_ndarray_', # will be pixels eventually...
		#	'_format_',
		#	'_byte_count_', # ?
		#	'_extents_',
		#]

		# XXX don't need changed, self now has __snap_output__!
		"""
		def changed(self, **MSG):
			""@SnapEvent
			() -> (image=SnapImage)
			""
			# XXX no args?  this is just a notifier?  events always have no args?  or just accept the arg of the source?
			if 'image' not in MSG:
				'pull new instance from self'
			else:
				'get it and send it'
			# image configuration changed (requires re-config of textures and some things referencing the image...)

			raise NotImplementedError()
		"""

		#def changed_data() # XXX we don't need changed_data, just send new SnapImage to changed (and reciever can check if it is a change in size, and copy the pixels (like it would do anyway!)

		@ENV.SnapProperty
		class width:
			def get(self, MSG):
				"""()->int"""
				return int(SnapMetrics.width.get(self, MSG))

		@ENV.SnapProperty
		class height:
			def get(self, MSG):
				"""()->int"""
				return int(SnapMetrics.height.get(self, MSG))

		@ENV.SnapProperty
		class size:
			def get(self, MSG):
				"""()->list(int, int)"""
				return [self['width'], self['height']]

		# TODO stride?

		@ENV.SnapProperty
		class pixels:
			def get(self, MSG):
				"""()->SnapBytes"""
				return self.__snap_data__['pixels']

			#def set(self, MSG):
			#	"""(SnapBytes)"""
			#	# TODO as SnapBytes
			#	raise NotImplementedError()

		@ENV.SnapProperty
		class format:
			def get(self, MSG):
				"""()->str"""
				fmt = self.__snap_data__['format']
				if fmt is None:
					fmt = 'RGBA'
				return fmt.upper()

			#def set(self, MSG):
			#	raise NotImplementedError('format cannot be assigned directly')

		@ENV.SnapProperty
		class bits_per_pixel:
			def get(self, MSG):
				"""()->int"""
				return int(self['format_pixel_size'])

		@ENV.SnapProperty
		class format_pixel_size:
			def get(self, MSG):
				"""()->int"""
				FORMAT = self['format']
				try:
					return self.FORMATS[FORMAT]
				except KeyError:
					raise KeyError('SnapImage format not found {}'.format(repr(FORMAT)))


		@ENV.SnapChannel
		def set(self, MSG):
			"""(
			(image=SnapImage!),
			(width=int|float!, height=int|float!, format=str!, pixels=bytes!),
			(size=list(int|float, int|float)!, format=str!, pixels=bytes!),
			(filepath=str!, size=list(int|float, int|float)!, format=str!),
			(filepath=str!, width=int|float!, height=int|float!, format=str!),
			)"""

			validate = [None, None, None, None] # width, height, format, pixels
			
			IMAGE = None
			FILEPATH = None

			pass_along = {}

			for attr,value in MSG.kwargs.items():
				if attr == 'image': IMAGE = value
				elif attr == 'width': validate[0] = value
				elif attr == 'height': validate[1] = value
				elif attr == 'size': validate[:2] = value
				elif attr == 'format': validate[2] = value
				elif attr == 'filepath': FILEPATH = value
				elif attr == 'pixels':
					if value is not None:
						assert isinstance(value, SnapBytes), 'pixels must be SnapBytes type'
					validate[3] = value
				else: pass_along[attr] = value

			if FILEPATH is not None:
				extras = {attr:validate[idx] for idx,attr in enumerate(('width', 'height', 'format')) if validate[idx] is not None}
				self.open(filepath=FILEPATH, **extras)

			else:
				#validate = None

				if IMAGE is not None:
					assert isinstance(IMAGE, SnapImage), 'not a SnapImage type: {}'.format(repr(type(IMAGE)))
					validate = [IMAGE.__getitem__(attr) for attr in ('width', 'height', 'format', 'pixels')]

				#elif PIXELS is not None:
				#	if SIZE != [None, None]:
				#		assert None not in SIZE, 'must provide size or both of width and height'
				#		validate = [SIZE[0], SIZE[1], FORMAT, PIXELS]

			if any([v for v in validate if v is not None]):

				WIDTH, HEIGHT, bits_per, FORMAT, BYTES = self._validate(*validate)
				self._assign(WIDTH, HEIGHT, bits_per, FORMAT, BYTES)

				# XXX TODO move changed to assign
				#self.changed(image=self, size=[WIDTH, HEIGHT], width=WIDTH, height=HEIGHT, format=FORMAT, pixels=BYTES)

			"""
			settings = MSG.kwargs

			if 'filepath' in settings:
				self.open(**settings)

			elif not settings:
				self.changed()

			else:

				validate = None
	
				if 'image' in settings:
					image = settings['image']
					assert isinstance(image, SnapImage), 'not a SnapImage type'
					validate = [getattr(image, attr)() for attr in ('width', 'height', 'format', 'pixels')]

				elif 'pixels' in settings:
					width,height,size, format, pixels = MSG.unpack(
						'width', None, 'height', None, 'size', None, 'format', None, 'pixels', None)

					if size is not None:
						validate = [size[0], size[1], format, pixels]
					elif width is not None and height is not None:
						validate = [width, height, format, pixels]
					else:
						raise Exception('invalid args', settings.keys())

				else:	
					return SnapShape.set(self, MSG)

				self._assign(*self._validate(*validate))

				self.changed()
			"""

			SUBMSG = SnapMessage()
			SUBMSG.args = MSG.args
			SUBMSG.kwargs = pass_along
			SUBMSG.source = MSG.source
			SUBMSG.channel = MSG.channel

			return SnapShape.set(self, SUBMSG)

		@ENV.SnapChannel(output="""(
		(image=SnapImage),
		(pixels=bytes, width=int, height=int, format=str),
		(pixels=bytes, size=list|tuple(int,int), format=str),
		)""")
		def changed(self, MSG):
			pass

		# TODO resized returns new image at requested size

		@ENV.SnapChannel
		def resize(self, MSG):
			"""(
			(int|float!, mode=str?, interpolation=str?, uniform=bool?),
			(width=int|float!, height=int|float?, mode=str?, interpolation=str?, uniform=bool?),
			(width=int|float?, height=int|float!, mode=str?, interpolation=str?, uniform=bool?),
			(size=list(int|float, int|float)!, mode=str?, interpolation=str?, uniform=bool?),
			)->None
			"""
			# TODO single positional arg as uniform scalar?
			#raise NotImplementedError() # TODO


			width,height,size,mode,interp,uniform = MSG.unpack('width', None, 'height', None, 'size', None, 'mode', None, 'interpolation', None, 'uniform', True)

			if MSG.args:
				assert isinstance(MSG.args[0], (int, float)), 'scalar value must be number'
				width = height = MSG.args[0]

			elif size is not None:
				width,height = size

			elif width is None:
				width = self['width']

			elif height is None:
				height = self['height']

			width = int(max(1, width))
			height = int(max(1, height))

			# TODO use engine to render so we can preserve the image?

			self.set(width=width, height=height, format=self['format'], pixels=None)

			"""
			# TODO if width is not None or height is not None:
			if len(ARGS) == 2:
				width = ARGS[0]
				height = ARGS[1]
				new_width = width if width and width > 0 else 1
				new_height = height if height and height > 0 else 1
				# TODO preserve image info by using rendering engine to draw the image to new size?
				self.set(width=new_width, height=new_height, format=self.format() or "RGBA", pixels=None)
			elif len(ARGS) == 1:
				# scalar
				raise NotImplementedError() # TODO
			elif len(KWARGS) == 2:
				raise NotImplementedError() # TODO
			elif len(KWARGS) == 1:
				raise NotImplementedError() # TODO
			else:
				raise Exception('invalid args')
			"""

			"""
			mode = SETTINGS.get('mode', None)
			interp = SETTINGS.get('interp', SETTINGS.get('interpolation', None))
			uniform = SETTINGS.get('uniform', True)

			if mode == 'CROP': # XXX just use self.crop(extents=...)?
				# TODO x,y,w,h clip to size?  or if bigger then fill with empty pixels?  or continue the frame?
				snap_warning("TODO image resize crop")
			elif mode == 'SCALE':
				'' # TODO resize / scale (by drawing with the image using a context...)
				snap_warning("TODO image resize scale")
			else:
				if mode:
					snap_warning("unknown image resize mode", mode)

			if width is None or width < 1:
				width = self.width()
			if height is None or height < 1:
				height = self.height()

			new_width = width if width and width > 0 else 1
			new_height = height if height and height > 0 else 1

			self.set(width=new_width, height=new_height, format=self.format() or "RGBA", pixels=None)
			"""

		@ENV.SnapChannel
		def crop(self, MSG):
			raise NotImplementedError() # crop the image (cut it off at allocation) TODO

		@ENV.SnapChannel
		def clear(self, MSG):
			w,h = self['size']
			#if w == 1 and h == 1:
			#	ENV.snap_out('clear', self)
			self.set(width=max(w, 1), height=max(h, 1), format=self['format'], pixels=None)


		@ENV.SnapChannel
		def open(self, MSG):
			"""(
			(filepath=str!, width=int|float?, height=int|float?, format=str?),
			(filepath=str!, size=list(int|float, int|float)?, format=str?),
			)
			"""

			# TODO make it possible to open and load as separate operations AND load in parts...

			filepath = MSG.unpack('filepath', None) # TODO other args to open at a size or format...

			if filepath is None:
				self.clear()
				return #True

			assert os.path.isfile(filepath), 'invalid filepath: "{}"'.format(filepath)

			# just using PIL to open images for now...  (will use ffmpeg once available)

			# TODO use ffmpeg for media IO once it's working... (or opencv?)
			im = PILImage.open(filepath).convert('RGBA')
			w,h = im.size
			#b = im.tobytes()

			# TODO if size or format provided, transform to request
			#	-- also, just one width or height is scalar?

			#bp = ctypes.cast(b, ctypes.c_char_p)
			bp = np.array(im).reshape(w * h * 4)
			B = SnapBytes(data=bp)

			#bp = ctypes.create_string_buffer(len(b))
			#bp[:] = b[:]
			#bp = (ctypes.c_char_p * len(b))(b) #bp = ctypes.cast(b, ctypes.c_char_p)

			#print('open format', im.format, im.format_description, im.mode)

			self._assign(*self._validate(w, h, "RGBA", B))

			self.changed(image=self, width=w, height=h, size=[w,h], format=self['format'], pixels=B)
			self.changed_data.emit()

			#snap_warning("open not yet implemented")

			"""
			MEDIA = self.ENV().media()

			reader = MEDIA.MediaReader(path=path)

			snap_debug('opening image', path)


			video_stream = reader.video_stream() # TODO accept index as arg as well...  no arg means get 'best video'

			video_stream.set(format="BGRA") # TODO formats correct and width,height?

			timeout = snap_time() + .5
			while snap_time() < timeout and reader.running():
				frame = reader.next()
				if frame:
					stream = frame.stream()
					if not frame.decoded_data_size():
						continue
					if stream == video_stream and frame.decoded_data_size() > 0:
						# found usable frame
						break
				frame = None

			if frame:

				fmt = "RGBA" # TODO get preferred engine format from engine?  or just always default to RGBA?

				w,h = frame.size()
				pixels = frame.data()
				data_size = frame.data_size()
				if w * h * 4 != data_size:
					snap_warning('size mismatch!', w*h*4, data_size)
				else:
					self.set(width=w, height=h, pixels=pixels, format=fmt)

			return None
			"""

		@ENV.SnapChannel
		def save(self, MSG):
			"""(filepath=str!)"""

			filepath = MSG.unpack('filepath', None)

			if filepath is None:
				raise Exception("save requires path!")

			#print('save', self.size(), type(self.pixels()), ctypes.sizeof(self.pixels()), len(bytes(self.pixels())))

			pixels = self['pixels']
			pixeldata = pixels['data'] if pixels is not None else None

			#bytes = pixeldata.bytes()
			#extents = pixeldata.extents()
			fmt = self['format']

			w,h = self['size'] # TODO aspect?  returns SnapList(SnapInt(), SnapInt()) ?
			# TODO aspect handles input and output?  XXX set() and get() and can only set one element?


			if w < 1 or h < 1 or not fmt: #sum(pixels.shape) < 1:
				raise TypeError('undefined image, cannot save', w,h, type(pixels), fmt, filepath)

			if fmt not in ("RGBA", "RGBA8"):
				raise TypeError('saving image format not yet supported', fmt)

			if 1:
				#im = PILImage.frombytes("RGBA", (w,h), bytes(bytes.__bytes__))
				if pixeldata is not None:
					im = PILImage.fromarray(pixeldata.reshape(h, w, 4))
				else:
					im = PILImage.fromarray(np.ndarray((1 * 1 * 4), dtype=np.uint8))
				im.save(filepath)#, format="JPEG")

			else:

				raise NotImplementedError("cairo image save()")

				"""
				#out('saving', type(pixels))

				stride = cairo_format_stride_for_width(CAIRO_FORMAT_ARGB32, w)
				if stride < 0:
					raise Exception("cairo_format_stride_for_width() unable to create stride for image data")
				
				#out('pixels', type(pixels))
				surface = cairo_image_surface_create_for_data(
					ctypes.cast(pixels, ctypes.POINTER(ctypes.c_ubyte)), CAIRO_FORMAT_ARGB32, w, h, stride)


				res = cairo_surface_write_to_png(surface, path.encode('utf8'))
				if res != 0:
					ENV.error('cairo unable to write png', res, cairo_status_to_string(res))
				cairo_surface_destroy(surface)

				#cairo_surface_t* surface = cairo_image_surface_create_for_data(
				#	(unsigned char*)pixels, CAIRO_FORMAT_ARGB32, w_h_bits[0], w_h_bits[1], stride);
				#cairo_surface_write_to_png(surface, (const char*)path);
				#cairo_surface_destroy(surface);

				"""

			ENV.snap_debug('image saved to', filepath)

		@ENV.SnapChannel
		def close(self, MSG):
			"""()"""
			self.clear()


		@ENV.SnapChannel
		def replace(self, MSG):
			# substitution
			raise NotImplementedError()

		@ENV.SnapChannel
		def sample(self, MSG):
			# get subsection (copy)
			raise NotImplementedError()


		@ENV.SnapChannel
		def premultiply(self, MSG):

			# keep track of state in flag
			# accept state arg

			# premultiply TODO
			"""
			unsigned char* pixels = (unsigned char*)snap_getattr(&image, "_pixels_");
			int* byte_count = (int*)snap_getattr(&image, "_byte_count_");
			if (pixels && byte_count){
				int idx;
				unsigned char* ptr;
				for (idx = 0; idx < *byte_count; idx += 4){
					ptr = pixels + idx;
					ptr[0] = (unsigned char)((ptr[0] / 255.) * (ptr[3] / 255.) * 255);
					ptr[1] = (unsigned char)((ptr[1] / 255.) * (ptr[3] / 255.) * 255);
					ptr[2] = (unsigned char)((ptr[2] / 255.) * (ptr[3] / 255.) * 255);
				}
			}
			"""
			raise NotImplementedError()




		"""
		def get_format_pixel_size(self, MSG):
			FORMAT = MSG.unpack('format', None, error_if_missing=True)
			try:
				return self.FORMATS[FORMAT]
			except:
				raise KeyError('SnapImage format not found {}'.format(repr(FORMAT)))
		"""

		def _calc_bytes(self, WIDTH, HEIGHT, BITS):

			# TODO consider format for pixel size?

			# if format is not byte aligned or smaller than a byte then
			# some padding might be needed to achieve byte alignment
			count = WIDTH * HEIGHT * BITS
			if count % 8:
				count += 8 - (count % 8) # byte aligned
			count /= 8
			if count < 1:
				ENV.snap_warning('image allocation calculated to be < 1; assigning as 1 byte')
				count = 1 # this is an error situation, but should it be size of pixel?  what if pixel size is invalid?

			return count

		def _validate(self, WIDTH, HEIGHT, FORMAT, BYTES):

			# if arguments are invalid then sensible defaults are used, images must always have data that is >= 1 pixel!

			can_use_pixels = True

			if WIDTH is None or WIDTH < 1:
				#snap_warning('invalid width or None provided', repr(WIDTH))
				WIDTH = 1
				can_use_pixels = False

			if HEIGHT is None or HEIGHT < 1:
				#snap_warning('invalid height or None provided?', HEIGHT)
				HEIGHT = 1
				can_use_pixels = False

			
			try:
				bits_per = self.FORMATS[FORMAT]
			except:
				#snap_warning('invalid format or None provided?', repr(FORMAT))
				FORMAT = "RGBA"
				bits_per = self.FORMATS[FORMAT]
				can_use_pixels = False

			if not can_use_pixels or BYTES is None:
				BYTES = None

			return WIDTH, HEIGHT, bits_per, FORMAT, BYTES

		def _assign(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):#(self, WIDTH, HEIGHT, BITS_PER_PIXEL, FORMAT, BYTES):
			# internal api, check has already been done!

			existing_pixels = self['pixels']
			#existing_pixels = getattr(self, '_ndarray_', None)
			# TODO if existing_pixels is None

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

				#self._pixels_ = existing_pixels
				self.__snap_data__['format'] = FORMAT
				self.__snap_data__['extents'] = snap_extents_t(0,0,0, WIDTH,HEIGHT,1)

			#self.__snap_data__['byte_count'] = byte_count # XXX ?  this is pixel count?

			if BYTES is not None:
				# copy pixels
				#snap_memcpy(existing_pixels, PIXELS, byte_count);
				#ctypes.memmove(existing_pixels, PIXELS, byte_count)
				existing_pixels['data'] = BYTES['data']
			else:
				# assign as NULL
				#ctypes.memset(existing_pixels, 0, byte_count)
				data = existing_pixels['data']
				if data is not None:
					data[:] = 255

			#out('pixels set', w,h, byte_count, ctypes.sizeof(existing_pixels), len(existing_pixels), len(existing_pixels.value))

			self.changed(image=self, size=[WIDTH, HEIGHT], width=WIDTH, height=HEIGHT, format=FORMAT, pixels=BYTES)


		def __init__(self, **SETTINGS):
			SnapShape.__init__(self)

			# TODO optimize with lazy loading?  some parameters don't need to exist unless they are used...

			self.__snap_data__['pixels'] = None
			#data['ndarray'] = None # pixels for now
			self['extents'] = snap_extents_t(0,0,0, 1,1,1)

			self.__snap_data__['format'] = "RGBA"

			init = dict(
				width=1,
				height=1,
				pixels=None,
				format="RGBA"
			)

			for attr,value in SETTINGS.items():
				if attr in ('width', 'height', 'format'):
					init[attr] = value
				elif attr == 'pixels' and 'filepath' not in init:
					init['pixels'] = value
				elif attr == 'size':
					init['width'] = value[0]
					init['height'] = value[1]
				elif attr == 'filepath':
					del init['pixels']
					init['filepath'] = value

			self.set(**init)


	ENV.SnapImage = SnapImage


def main(ENV):

	img = ENV.SnapImage()
	img.resize(100,100)

	ENV.snap_out(img['width'], img['height'], img['bits_per_pixel'], img['width'] * img['height'] * 4)
	#ctypes.memset(img._pixels_, 220, img.width() * img.height() * 4)
	img.save('/home/user/Downloads/SnapImage_test.png')

	img.open('/media/user/CRUCIAL1TB/MyComputer/MEDIA/IMAGES/Funny/0bo3u55w27iz.png')
	img.save('/home/user/Downloads/SnapImage_test2.png')

	ENV.snap_out('ok')

