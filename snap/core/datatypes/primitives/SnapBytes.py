
import numpy

def build(ENV):

	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage


	class SnapBytes(SnapPrimitive):

		__slots__ = []

		@ENV.SnapProperty
		class data:

			def get(self, MSG):
				"""()->bytes"""
				return SnapPrimitive.data.get(self, MSG)

			def set(self, MSG):
				"""(bytes|SnapBytes)"""
				data = MSG.args[0]

				if data is not None:
					if isinstance(data, bytes):
						data = numpy.frombuffer(data, dtype=numpy.uint8)#, count=-1, offset=0, *, like=None)
					elif isinstance(data, str):
						data = numpy.frombuffer(data.encode(), dtype=numpy.uint8)
					elif isinstance(data, SnapBytes):
						if data['data'] is not None:
							#data = numpy.copy(data['data'])
							data = data['data'] # share
						else:
							data = None
					elif isinstance(data, numpy.ndarray):
						pass # share it
						#existing = SnapNode_get(self, 'data')
						#if existing is not data:
						#	data = data.copy()
					else:
						raise TypeError(type(data))

				return SnapPrimitive.data.set(self, SnapMessage(data))

		def __compare__(self, OTHER):

			raise NotImplementedError('__compare__')

			self_array = self['data']

			if other is None:
				if self_array is None:
					return 0
				return 1

			other_array = other['data']
			if other_array is None:
				if self_array is None:
					return 0
				return 1

			#raise NotImplementedError() # XXX TODO just write a c function to do the byte comparison ourselves (or use strcmp from ctypes?)

			"""
			# https://numpy.org/doc/2.1/reference/generated/numpy.char.compare_chararrays.html
			cmp = numpy.char.compare_chararrays
			if cmp(self_array, other_array, '==', False):
				return 0
			elif cmp(self_array, other_array, '>', False):
				return 1
			else:
				return -1
			"""

			self_bytes = self_array.tobytes()
			other_bytes = other_array.tobytes()

			# python bytes:
			if self_bytes == other_bytes:
				return 0
			elif self_bytes > other_bytes:
				return 1
			else:
				return -1
			

		@ENV.SnapChannel
		def realloc(self, MSG):
			"""(size=int)"""

			SIZE = MSG.unpack('size', -1)

			if SIZE < 1:
				if self['data'] is not None:
					self['data'] = None
					self.changed(size=SIZE)
				return None

			int_size = int(SIZE)
			assert SIZE - int_size == 0, 'float with extra value?  size must be interpretable as int {}'.format(repr(SIZE))

			SIZE = int_size

			existing = self['data']
			if existing is None or existing.nbytes != SIZE:
				new = numpy.ndarray((SIZE), dtype=numpy.uint8)
				if existing is not None:
					copy_count = min(new.nbytes, existing.nbytes)
					new[:copy_count] = existing[:copy_count]
				self['data'] = new

			return None

		"""
		def __setitem__(self, KEY, VALUE):
			if isinstance(KEY, str):
				assert KEY == 'data', 'only "data" allowed in SnapBytes'
				if VALUE is not None:
			
					# verify it here
					if isinstance(VALUE, bytes):
						VALUE = numpy.frombuffer(VALUE, dtype=numpy.uint8)#, count=-1, offset=0, *, like=None)
					elif isinstance(VALUE, str):
						VALUE = VALUE.encode()
					elif isinstance(VALUE, SnapBytes):
						if VALUE['data'] is not None:
							VALUE = numpy.copy(VALUE['data'])
						else:
							VALUE = None
					else:
						raise TypeError(type(VALUE))

				# don't do full comparison, just assume that a change occurred if not the same id()
				if VALUE is not self['data']:
					return SnapNode.__setitem__(self, KEY, VALUE)

			else:
				current = self['data']
				if current is None:
					#raise NotImplementedError() # assign the segment?
					self['data'] = VALUE # ?
				else:
					current.__setitem__(KEY, VALUE)

			raise KeyError(KEY)



		# TODO __getitem__, __setitem__, __delitem__
		#	-- return as new SnapBytes object (access to __value__ must be explicit)
		def __getitem__(self, KEY):
			# TODO wrap the returned result in SnapBytes?
			return SnapPrimitive.__getitem__(self, KEY)
		"""

		#def __setitem__(self, KEY, VALUE):
		#	if isinstance(VALUE, SnapBytes):
		#		VALUE = VALUE.data
		#	# TODO if self.__snap_data__ is not None?
		#	return self.__snap_data__['__data__'].__setitem__(KEY, VALUE)

		#def __delitem__(self, KEY):
		#	raise NotImplementedError() # delete and realloc

		def __len__(self):
			data = self['data']
			if data is None:
				return 0
			else:
				return data.nbytes

		def __bool__(self):
			data = self['data']
			return data is not None and data.nbytes > 0

		def __init__(self, data=None, **SETTINGS):
			SnapPrimitive.__init__(self, data=data)


	ENV.SnapBytes = ENV.SnapByte = SnapBytes

