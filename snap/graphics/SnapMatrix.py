
def build(ENV):

	SnapNode = ENV.SnapNode
	#snap_raw = ENV.snap_raw
	#snap_debug = ENV.snap_debug

	SnapMessage = ENV.SnapMessage
	unpack_msg_from_key = ENV.unpack_msg_from_key

	ctypes = ENV.extern.ctypes
	os = ENV.extern.os # TODO or localize what is needed...?

	#if ENV.__SNAP_IS_PYTHON__:
	#import ctypes # https://docs.python.org/3/library/ctypes.html
	# https://stackoverflow.com/questions/44685080/python-ctypes-pointer-arithmetic
	#THISDIR = os.path.realpath(os.path.dirname(__file__))
		
	SnapMatrixExt = ctypes.snap_recompile_support_library(__file__)


	# int snap_matrix_scale(double* self, double x, double y, double z, double* PARENT, double* ANSWER){
	snap_matrix_scale = SnapMatrixExt.snap_matrix_scale
	snap_matrix_scale.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_scale.restype = ctypes.c_int
	ENV.snap_matrix_scale = snap_matrix_scale


	# int snap_matrix_rotate(double* self, double angle, double x, double y, double z, double* PARENT, double* ANSWER){
	snap_matrix_rotate = SnapMatrixExt.snap_matrix_rotate
	snap_matrix_rotate.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_rotate.restype = ctypes.c_int
	ENV.snap_matrix_rotate = snap_matrix_rotate

	# int snap_matrix_translate(double* self, double x, double y, double z, double* PARENT, double* ANSWER){
	snap_matrix_translate = SnapMatrixExt.snap_matrix_translate
	snap_matrix_translate.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_translate.restype = ctypes.c_int
	ENV.snap_matrix_translate = snap_matrix_translate

	# int snap_matrix_transform(double* self, double* TRANSFORM, double* PARENT, double* ANSWER){
	snap_matrix_transform = SnapMatrixExt.snap_matrix_transform
	snap_matrix_transform.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_transform.restype = ctypes.c_int
	ENV.snap_matrix_transform = snap_matrix_transform

	# void snap_matrix_transpose(double* self, double* ANSWER){
	snap_matrix_transpose = SnapMatrixExt.snap_matrix_transpose
	snap_matrix_transpose.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_transpose.restype = None
	ENV.snap_matrix_transpose = snap_matrix_transpose

	# int snap_matrix_invert(double* m, double* ANSWER){
	snap_matrix_invert = SnapMatrixExt.snap_matrix_invert
	snap_matrix_invert.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_invert.restype = ctypes.c_int
	ENV.snap_matrix_invert = snap_matrix_invert

	# void snap_matrix_transform_point(double* matrix, double* point, double delta, double* ANSWER){
	snap_matrix_transform_point = SnapMatrixExt.snap_matrix_transform_point
	snap_matrix_transform_point.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
	snap_matrix_transform_point.restype = None
	ENV.snap_matrix_transform_point = snap_matrix_transform_point

	# void snap_matrix_multiply(double* A, double* B, double* ANSWER){
	snap_matrix_multiply = SnapMatrixExt.snap_matrix_multiply
	snap_matrix_multiply.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_multiply.restype = None
	ENV.snap_matrix_multiply = snap_matrix_multiply

	# int snap_matrix_decompose(double* self, double* POS_XYZ, double* QUAT_XYZW, double* SCALE_4x4){
	snap_matrix_decompose = SnapMatrixExt.snap_matrix_decompose
	snap_matrix_decompose.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_matrix_decompose.restype = ctypes.c_int
	ENV.snap_matrix_decompose = snap_matrix_decompose

	snap_matrix_t = (ctypes.c_double * 16)
	ENV.snap_matrix_t = snap_matrix_t

	# https://gamedev.stackexchange.com/questions/14115/do-i-need-the-w-component-in-my-vector-class
	snap_vector_t = (ctypes.c_double * 4) # w == 0 is vector, w == 1 is point?
	ENV.snap_vector_t = snap_vector_t



	# TODO does this name collide with c?  is it needed?
	SNAP_IDENTITY_MATRIX = [
		1.0, 0.0, 0.0, 0.0,
		0.0, 1.0, 0.0, 0.0,
		0.0, 0.0, 1.0, 0.0,
		0.0, 0.0, 0.0, 1.0
	]


	#snap_matrix_t = (ctypes.c_double * 16)
	SNAP_IDENTITY_MATRIX = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
	ENV.SNAP_IDENTITY_MATRIX = SNAP_IDENTITY_MATRIX
	#arr[:] = SNAP_IDENTITY_MATRIX
	#print(arr[:])
	#SNAP_IDENTITY_MATRIX[5] = 22.
	#print(SNAP_IDENTITY_MATRIX[:])
	#print('second', (ctypes.c_double * 16)(*SNAP_IDENTITY_MATRIX)[:])

	class SnapMatrix(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class matrix:
			def get(self, MSG):
				"""()->snap_matrix_t"""
				m = self.__snap_data__['matrix']
				if m is None:
					# we assign a local copy so we can change it in-place
					m = self.__snap_data__['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
				return m

			def set(self, MSG):
				"(snap_matrix_t|SnapMatrix!)"
				value = MSG.args[0]
				if isinstance(value, SnapMatrix):
					value = value['matrix']

				m = self.__snap_data__['matrix']
				if value is not None:
					if m is None:
						m = snap_matrix_t(*value)
					else:
						m[:] = value
				else:
					if m is None:
						m = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
					else:
						m[:] = SNAP_IDENTITY_MATRIX

				self.__snap_data__['matrix'] = m
				self.changed(matrix=m)

		# sometimes render_matrix needs to be different (like for SnapCamera)
		@matrix.alias
		class render_matrix: pass

		@ENV.SnapProperty
		class position:

			def get(self, MSG):
				"""()->list(float,float,float)"""
				m = self['matrix']
				return [m[3],m[7],m[11]]

			def set(self, MSG):
				"""(
				(list(float,float),
				(list(float,float,float),
				)"""

				position = MSG.args[0]

				m = self['matrix']
				if m is None:
					m = snap_matrix_t(*SNAP_IDENTITY_MATRIX)					
				current = [m[3],m[7],m[11]]

				if not position:
					current = [0.,0.,0.]
				else:
					if len(position) > 3:
						ENV.snap_warning('too many arguments for position', len(position))

					end = min(len(position),3)
					idx = 0
					while idx < end:
						current[idx] = position[idx]
						idx += 1

				m[3] = current[0]
				m[7] = current[1]
				m[11] = current[2]

				self['matrix'] = m

				# TODO emit to position?

		@position.shared
		class origin: pass

		# TODO decompose scale and rotation?


		@ENV.SnapProperty
		class inverted:

			def get(self, MSG):
				"""()->SnapMatrix"""
				M = SnapMatrix()
				r = M['matrix']
				s = self['matrix']
				snap_matrix_invert(s,r)
				return M

		@inverted.shared
		class inverse: pass

		@ENV.SnapProperty
		class transposed:

			def get(self, MSG):
				"""()->SnapMatrix"""
				M = SnapMatrix()
				r = M['matrix']
				s = self['matrix']
				snap_matrix_transpose(s,r)
				return M

		@ENV.SnapProperty
		class multiplied:
			
			def get(self, MSG):
				"""(SnapMatrix?)->SnapMatrix"""
				OTHER = MSG.args[0] if MSG.args else self
				o = OTHER['matrix']
				s = self['matrix']
				M = SnapMatrix()
				r = M['matrix']
				snap_matrix_multiply(s,o,r)
				return M

		@ENV.SnapProperty
		class identity:

			def get(self, MSG):
				"""()->SnapMatrix"""
				return SnapMatrix()

		@ENV.SnapProperty
		class transformed:

			def get(self, MSG):
				"""(transform=SnapMatrix!, parent=SnapMatrix?)->SnapMatrix"""
				TRANSFORM, parent = MSG.unpack('transform', None, 'parent', None)
				assert TRANSFORM is not None, 'transform arg required'

				t = TRANSFORM['matrix']
				s = self['matrix']
				p = parent['matrix'] if parent else None
				M = SnapMatrix()
				r = M['matrix']
				snap_matrix_transform(s, t, p, r)
				return M


		@ENV.SnapProperty
		class translated:

			def get(self, MSG):
				"""(x=int|float?, y=int|float?, z=int|float?, parent=SnapMatrix?)->SnapMatrix"""
				x,y,z,parent = MSG.unpack('x',0, 'y',0, 'z',0, 'parent',None)

				M = SnapMatrix()
				r = M['matrix']
				s = self['matrix']
				p = parent['matrix'] if p else None
				
				snap_matrix_translate(s, x, y, z, p, r)
				return M

		@ENV.SnapProperty
		class rotated:

			def get(self, MSG):
				"""(angle=int|float?, x=int|float?, y=int|float?, z=int|float?, parent=SnapMatrix?)->SnapMatrix"""
				
				angle,x,y,z,parent = MSG.unpack('angle',0, 'x',0, 'y',0, 'z',0, 'parent',None)

				M = SnapMatrix()
				r = M['matrix']
				s = self['matrix']
				p = parent['matrix'] if parent else None
				
				snap_matrix_rotate(s, angle, x, y, z, p, r)
				return M

		@ENV.SnapProperty
		class scaled:

			def get(self, MSG):
				"""(x=int|float?, y=int|float?, z=int|float?, parent=SnapMatrix?)->SnapMatrix"""

				x,y,z,parent = MSG.unpack('x',1, 'y',1, 'z',1, 'parent',None)

				s = self['matrix']
				M = SnapMatrix()
				r = M['matrix']
				p = parent['matrix'] if parent else None
				snap_matrix_scale(s, x, y, z, p, r)
				return M




		@ENV.SnapChannel
		def invert(self, MSG):
			"""()"""
			s = self['matrix']
			snap_matrix_invert(s,s)
			return None

		@ENV.SnapChannel
		def transform_point(self, MSG):
			"""(x=float|int?, y=float|int?, z=float|int?, w=float|int?, delta=bool?)->list(float,float,float)"""

			x,y,z,w,delta = MSG.unpack('x',0, 'y',0, 'z',0, 'w',1, 'delta',False)

			if w != 1:
				raise NotImplementedError('w in transform_point')
			s = self['matrix']
			pt = snap_vector_t(x or 0,y or 0,z or 0, w)
			snap_matrix_transform_point(s, pt, 1.0 if delta else 0.0, pt)
			return pt[:3]

		@ENV.SnapChannel
		def transpose(self, MSG):
			"""()"""
			s = self['matrix']
			snap_matrix_transpose(s,s)
			return None

		@ENV.SnapChannel
		def multiply(self, MSG):
			"""(matrix=SnapMatrix|snap_matrix_t!)"""
			# in-place
			OTHER = MSG.unpack('matrix',None) # SnapMatrix
			assert OTHER is not None, 'requires matrix'

			if isinstance(OTHER, SnapMatrix):
				OTHER = OTHER['matrix']
			s = self['matrix']
			snap_matrix_multiply(s,OTHER,s)
			return None


		#def __mul__(self, OTHER): XXX too ambiguous, just use calls directly
		#	return self.multiplied(OTHER)

		@ENV.SnapChannel
		def reset(self, MSG):
			"""()"""
			self.to_identity()

		@ENV.SnapChannel
		def to_identity(self, MSG):
			"""()"""
			self['matrix'] = SNAP_IDENTITY_MATRIX


		@ENV.SnapChannel
		def transform(self, MSG):
			"""(transform=SnapMatrix!, parent=SnapMatrix?)"""

			TRANSFORM, parent = MSG.unpack('transform', None, 'parent', None)
			assert TRANSFORM is not None, 'transform arg required'

			t = TRANSFORM['matrix']
			s = self['matrix']
			p = parent['matrix'] if parent else None
			snap_matrix_transform(s, t, p, s)
			return None

		@ENV.SnapChannel
		def translate(self, MSG):
			"""(x=float|int?, y=float|int?, z=float|int?, parent=SnapMatrix?)"""

			x,y,z,parent = MSG.unpack('x',0, 'y',0, 'z',0, 'parent',None)
			
			s = self['matrix']
			p = parent['matrix'] if parent else None

			snap_matrix_translate(s, x, y, z, p, s)
			return None

		@ENV.SnapChannel
		def rotate(self, MSG):
			"""(angle=float|int?, x=float|int?, y=float|int?, z=float|int?, parent=SnapMatrix?)"""

			# NOTE: angle is in degrees # TODO support keywords for degrees and radians?
			# degrees = radians * (180/pi)
			# radians = degrees * (pi/180)

			angle,x,y,z,parent = MSG.unpack('angle',0, 'x',0, 'y',0, 'z',0, 'parent',None)

			#ENV.snap_debug('rotate', angle, x,y,z, parent)
			if not (x or y or z):
				z = 1 # 2D user friendly, so just calling rotate(angle) will do something...

			s = self['matrix']
			p = parent['matrix'] if parent else None
			snap_matrix_rotate(s, angle, x, y, z, p, s)
			return None

		@ENV.SnapChannel
		def scale(self, MSG):
			"""(x=float|int?, y=float|int?, z=float|int?, parent=SnapMatrix?)"""

			x,y,z,parent = MSG.unpack('x',1, 'y',1, 'z',1, 'parent',None)

			s = self['matrix']
			p = parent['matrix'] if parent else None
			snap_matrix_scale(s, x, y, z, p, s)
			return None

		"""
		def set(self, MSG):
			for attr,value in MSG.kwargs.items():

				if attr in ('matrix', 'SnapMatrix'):
					if value is None:
						self.data()['matrix'][:] = SNAP_IDENTITY_MATRIX
					else:
						if attr == 'SnapMatrix':
							value = value.matrix()
						self.data()['matrix'][:] = value
				#else:
					#SnapNode.set(self, **{attr:value})
		"""



		def __repr__(self):
			s = SnapNode.__repr__(self)
			#return s + '('+str(self['matrix'][:])+')'
			return s

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			# bypassing set() call for speed

			#if matrix is not None:
			#	self['matrix'] = snap_matrix_t(*matrix)
			#else:
			#	self['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
				#ctypes.memmove(self._matrix_, SNAP_IDENTITY_MATRIX, ctypes.sizeof(ctypes.c_double) * 16)

			# TODO dynamic property access into python array?

		#def __snap_description__(self):
		#	return {} # TODO


	ENV.SnapMatrix = SnapMatrix

def main(ENV):

	M = ENV.SnapMatrix()

	M.rotate(25, x=1)

	print(M['matrix'][:])

	

