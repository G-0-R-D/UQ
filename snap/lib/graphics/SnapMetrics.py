
def build(ENV):

	#recompile_support_library = ENV.recompile_support_library

	snap_matrix_transform = ENV.snap_matrix_transform

	SnapMatrix = ENV.SnapMatrix

	ctypes = ENV.extern.ctypes

	#snap_send = ENV.snap_send
	#snap_emit = ENV.snap_emit

	snap_warning = ENV.snap_warning

	#if ENV.__SNAP_IS_PYTHON__:

	SnapMetricsExt = ctypes.snap_recompile_support_library(__file__)

	# int snap_extents_are_null(double* EXTENTS){
	snap_extents_are_null = SnapMetricsExt.snap_extents_are_null
	snap_extents_are_null.argtypes = [ctypes.POINTER(ctypes.c_double)]
	snap_extents_are_null.restype = ctypes.c_int
	ENV.snap_extents_are_null = snap_extents_are_null

	# void snap_matrix_map_extents(double *matrix, double *extents, int is_delta, double *ANSWER){
	snap_matrix_map_extents = SnapMetricsExt.snap_matrix_map_extents
	snap_matrix_map_extents.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
	snap_matrix_map_extents.restype = None
	ENV.snap_matrix_map_extents = snap_matrix_map_extents

	# int snap_extents_contain_point(double* EXTENTS, double* POINT){
	snap_extents_contain_point = SnapMetricsExt.snap_extents_contain_point
	snap_extents_contain_point.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_extents_contain_point.restype = ctypes.c_int
	ENV.snap_extents_contain_point = snap_extents_contain_point

	# int snap_extents_diffmatrix(double* BASE_ext, double* ITEM_ext, int uniform, double align_x, double align_y, double align_z, double* MATRIX_ANSWER){
	snap_extents_diffmatrix = SnapMetricsExt.snap_extents_diffmatrix
	snap_extents_diffmatrix.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
	snap_extents_diffmatrix.restype = ctypes.c_int
	ENV.snap_extents_diffmatrix = snap_extents_diffmatrix

	# void snap_extents_mix(double* A, double* B, double* ANSWER){
	snap_extents_mix = SnapMetricsExt.snap_extents_mix
	snap_extents_mix.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
	snap_extents_mix.restype = None
	ENV.snap_extents_mix = snap_extents_mix

	# void snap_extents_ensure_correct(double* EXTENTS){
	snap_extents_ensure_correct = SnapMetricsExt.snap_extents_ensure_correct
	snap_extents_ensure_correct.argtypes = [ctypes.POINTER(ctypes.c_double)]
	snap_extents_ensure_correct.restype = None
	ENV.snap_extents_ensure_correct = snap_extents_ensure_correct

	snap_extents_t = (ctypes.c_double * 6)
	ENV.snap_extents_t = snap_extents_t

	snap_matrix_map_extents = ENV.snap_matrix_map_extents
	snap_matrix_t = ENV.snap_matrix_t
	snap_matrix_invert = ENV.snap_matrix_invert


	# TODO make child_fit and parent_fit methods?  along with fit()?
	def snap_extents_fit(BASE_ext, ITEM, **SETTINGS):
		# fits ITEM inside of BASE_ext by translating and scaling ITEM's matrix by the difference

		ITEM_ext = ITEM['extents']

		# TODO make scaling optional!  
		
		# XXX TODO use snap_event(self, "GET", "extents", ext);
		#double* BASE_extents_src = (double*)snap_getattr_at(self, "_extents_", IDX_SnapMetrics__extents_);
		#double* ITEM_extents_src = (double*)snap_getattr_at(&ITEM, "_extents_", IDX_SnapMetrics__extents_);

		assert not (snap_extents_are_null(BASE_ext) or snap_extents_are_null(ITEM_ext)), "invalid extents for fit operation"

		# localized for assign below
		ITEM_matrix = ITEM['matrix']
		assert ITEM_matrix is not None, 'no item matrix?'

		# extents are local to item, we want them in item parent space (the two are compared as peers)
		snap_matrix_map_extents(ITEM_matrix, ITEM_ext, 0, ITEM_ext)

		tm = snap_matrix_t()
		align_x = SETTINGS.get('align_x', 0.5)
		align_y = SETTINGS.get('align_y')
		if align_y is None:
			align_y = align_x
		align_z = SETTINGS.get('align_z')
		if align_z is None:
			align_z = align_x
		lock_scale = SETTINGS.get('lock_scale', False)
		uniform = SETTINGS.get('uniform', True)
		if snap_extents_diffmatrix(BASE_ext, ITEM_ext, lock_scale, uniform, align_x, align_y, align_z, tm) != 0:
			raise ValueError("snap_extents_fit() unable to calculate diffmatrix")

		snap_matrix_transform(ITEM_matrix, tm, None, ITEM_matrix)

		return None

	ENV.snap_extents_fit = snap_extents_fit

	# TODO merge_extents() -> into one area?  (basically just take the biggest and smallest point)

	class SnapMetrics(SnapMatrix):

		__slots__ = []
		#__slots__ = ['_extents_']

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"""()->snap_extents_t"""
				e = self.__snap_data__['extents']
				if e is None:
					e = snap_extents_t(0,0,0, 0,0,0)
				#	e = self.__snap_data__['extents'] = snap_extents_t(0,0,0, 1,1,1)
				#return e
				return e

			def set(self, MSG):
				"""(snap_extents_t!)""" # TODO list|tuple or *values...
				ext = MSG.args[0]
				if ext is not None:
					assert isinstance(ext, snap_extents_t)
					if ext[3] <= ext[0]: ext[3] = ext[0]
					if ext[4] <= ext[1]: ext[4] = ext[1]
					if ext[5] <= ext[2]: ext[5] = ext[2]
					self.__snap_data__['extents'] = ext
				else:
					del self.__snap_data__['extents']
				self.changed(extents=ext)

		@ENV.SnapProperty
		class mapped_extents:
			# the reverse of this is to multiply extents by inverted self['matrix']

			def get(self, MSG):
				"""()->snap_extents_t"""
				ext = snap_extents_t(*self['extents'])
				snap_matrix_map_extents(self['matrix'], ext, 0, ext)
				return ext

		@ENV.SnapProperty
		class width:

			def get(self, MSG):
				"""()->float"""
				e = self['extents']
				return float(e[3]-e[0])

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				e = self['extents']
				if value is None:
					value = 0
				e[3] = e[0] + value
				self['extents'] = e
				self.changed(width=value)
				

		@ENV.SnapProperty
		class height:

			def get(self, MSG):
				"""()->float"""
				e = self['extents']
				return float(e[4]-e[1])

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				e = self['extents']
				if value is None:
					value = 0
				e[4] = e[1] + value
				self['extents'] = e
				self.changed(height=value)

		@ENV.SnapProperty
		class depth:

			def get(self, MSG):
				"""()->float"""
				e = self['extents']
				return float(e[5]-e[2])

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				e = self['extents']
				if value is None:
					value = 0
				e[5] = e[2] + value
				self['extents'] = e
				self.changed(depth=value)

		@ENV.SnapProperty
		class size:

			def get(self, MSG):
				"""()->tuple(float,float)"""
				e = self['extents']
				return e[3]-e[0], e[4]-e[1] # w,h

			def set(self, MSG):
				"""(
				(int|float!, int|float!),
				(tuple(int|float, int|float)!),
				(width=int|float?, height=int|float?),
				)"""
				if MSG.args:
					if len(MSG.args) == 2:
						w,h = MSG.args
					elif len(MSG.args) == 1:
						w,h = MSG.args[0]
					else:
						raise IOError('invalid args', MSG.args)
				elif MSG.kwargs:
					w,h = MSG.kwargs.get('width', self['width']), MSG.kwargs.get('height',self['height'])
				else:
					raise IOError('invalid arguments', MSG)
				e = self['extents']
				e[3] = e[0] + float(w)
				e[4] = e[1] + float(h)
				self['extents'] = e
				self.changed(size=(w,h))

		@ENV.SnapProperty
		class dimensions:

			def get(self, MSG):
				"""()->tuple(float,float,float)"""
				e = self['extents']
				return e[3]-e[0], e[4]-e[1], e[5]-e[2] # w,h,d

			def set(self, MSG):
				"""(
				(int|float!, int|float!, int|float!),
				(tuple(3 * int|float)!),
				(width=int|float?, height=int|float?, depth=int|float?),
				)"""
				if MSG.args:
					w,h,d = MSG.args[:3]
				elif MSG.kwargs:
					w,h,d = MSG.kwargs.get('width', self['width']), MSG.kwargs.get('height', self['height']), MSG.kwargs.get('depth', self['depth'])
				else:
					raise IOError('invalid arguments', MSG)
				e = self['extents']
				e[3] = e[0] + float(w)
				e[4] = e[1] + float(h)
				e[5] = e[3] + float(d)
				self['extents'] = e
				self.changed(dimensions=(w,h,d))
				

		@ENV.SnapProperty
		class bounds:
			def get(self, MSG):
				"""()->tuple(4 * float)"""
				e = self.extents()
				return e[0], e[1], e[3]-e[0], e[4]-e[1] # x,y,w,h

		# XXX TODO x,y,z should refer to matrix origin?
		@ENV.SnapProperty
		class x:
			def get(self, MSG):
				"""()->float"""
				return self['extents'][0]

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				ext = self['extents']
				if value:
					ext[0] = value
				else:
					ext[0] = 0
				self['extents'] = ext # which will clamp and emit
				self.changed(x=value)

		@ENV.SnapProperty
		class y:
			def get(self, MSG):
				"""()->float"""
				return self['extents'][1]

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				ext = self['extents']
				if value:
					ext[1] = value
				else:
					ext[1] = 0
				self['extents'] = ext # which will clamp and emit
				self.changed(x=value)

		@ENV.SnapProperty
		class z:
			def get(self, MSG):
				"""()->float"""
				return self['extents'][2]

			def set(self, MSG):
				"""(int|float!)"""
				value = MSG.args[0]
				ext = self['extents']
				if value:
					ext[2] = value
				else:
					ext[2] = 0
				self['extents'] = ext # which will clamp and emit
				self.changed(x=value)

		#def origin(self, MSG): # XXX this is ambiguous? use min_point() max_point()?  origin() is really center()?
		#	return self.extents()[:3]

		@ENV.SnapProperty
		class min_point:
			def get(self, MSG):
				"""()->tuple(3 * float)"""
				return self['extents'][:3]

		@ENV.SnapProperty
		class max_point:
			def get(self, MSG):
				"""()->tuple(3 * float)"""
				return self['extents'][3:]

		@ENV.SnapProperty
		class radius:

			def get(self, MSG):
				"""()->float"""
				# https://www.engineeringtoolbox.com/distance-relationship-between-two-points-d_1854.html
				# distance from center to largest extents (considered as a circular bounds)
				# TODO consider the angle?  technically it should be ray from center to furthest corner...

				# extents is min and max point, so just calculate .5 * vector/ray between them!
				e = self['extents']
				return float( (((e[3]-e[0])**2 + (e[4]-e[1])**2 + (e[5]-e[2])**2)**.5) * .5 )

		@ENV.SnapProperty
		class diameter:

			def get(self, MSG):
				"""()->float"""
				e = self['extents']
				return float( ((e[3]-e[0])**2 + (e[4]-e[1])**2 + (e[5]-e[2])**2)**.5 )

		@ENV.SnapProperty
		class center:

			def get(self, MSG):
				"""()->tuple(3 * float)""" # TODO use snap_vector_t?
				#SnapMetrics_proportion(self, .5, .5, .5, (double*)value);
				e = self['extents']
				return e[0] + (e[3]-e[0]) * .5, e[1] + (e[4]-e[1]) * .5, e[2] + (e[5]-e[2]) * .5

		# TODO 'left', 'right', 'top', 'bottom', also compass (north, west, east, south, ...)?


		@ENV.SnapChannel
		def fit(self, MSG):
			"""(SnapMetrics!)->snap_extents_t"""
			return snap_extents_fit(self['extents'], MSG.args[0], **MSG.kwargs)

		#def crop(self, MSG):
		#	ENV.snap_warning("crop() deprecated; use allocate()")
		#	return self.allocate.__direct__(MSG)

		@ENV.SnapChannel
		def allocateXXX(self, MSG): # XXX deprecated; use extents.set()!
			"""(extents=snap_extents_t)"""
			extents = MSG.unpack('extents', None)
			if extents is None:
				'assign to 0...?'
				return None
			
			# TODO resize the local extents to the given extents (fit)
			#raise NotImplementedError()


		@ENV.SnapChannel
		def set(self, MSG):
			"""(
			width=int|float?, height=int|float?, depth=int|float,
			size=tuple|list(2 * int|float)?, dimensions=tuple|list(3 * int|float)?,
			x=int|float?, y=int|float?, z=int|float?,
			position=list|tuple(2 * int|float)?, origin=list|tuple(3 * int|float)?,
			extents=snap_extents_t?,
			)"""
			return SnapMatrix.set(self, MSG)

			# TODO use with to turn off changed emissions?  make that standard on SnapNode?

			"""
			ext = self['extents'] or snap_extents_t()
			changed = False

			for attr,value in MSG.kwargs.items():

				if attr in ('width', 'height', 'depth'):
					axis = ['width','height','depth'].index(attr)
					if not value:
						value = 0
					ext[axis+3] = ext[axis] + value
					changed = True

				elif attr in ('size', 'dimensions'):
					axes = [0,1,2] if attr == 'dimensions' else [0,1]
					if not value:
						value = [0,0,0]
					for axis in axes:
						ext[axis+3] = ext[axis] + value[axis]
					changed = True

				elif attr in ('x','y','z'):
					axis = ['x','y','z'].index(attr)
					if not value:
						value = 0
					# this behaves like a translation, moving the whole rect
					diff = ext[axis+3]-ext[axis]
					ext[axis] = value
					ext[axis+3] = value + diff
					changed = True

				elif attr in ('position', 'origin'):
					axes = [0,1,2] if attr == 'origin' else [0,1]
					if not value:
						value = [0,0,0]
					for axis in axes:
						diff = ext[axis+3] - ext[axis]
						ext[axis] = value[axis]
						ext[axis+3] = value[axis] + diff
					changed=True

				elif attr in ('extents', '_extents_'):
					ext[:] = value
					changed = True

				else:
					ENV.snap_warning("unsupported setting", attr)
					#SnapMatrix.set(self, **{attr:value})

			if changed:
				data['extents'] = ext
				if ext[3] <= ext[0]: ext[3] = ext[0]+1
				if ext[4] <= ext[1]: ext[4] = ext[1]+1
				if ext[5] <= ext[2]: ext[5] = ext[2]+1
				#snap_send(self.changed, extents=ext) XXX TODO
				#snap_emit(self, "CHANGED", extents=ext)
				self.changed(extents=ext)
			"""

		def __repr__(self):
			return SnapMatrix.__repr__(self) # TODO

		def __init__(self, **SETTINGS):
			SnapMatrix.__init__(self, **SETTINGS)

			#if extents is not None:
			#	self['extents'] = snap_extents_t(*extents)
			#else:
			#	self['extents'] = None # assigned means it is known for this object; cached; ie don't need to do a full walk to determine the extents...  #snap_extents_t(0,0,0, 0,0,0)



	ENV.SnapMetrics = SnapMetrics


def main(ENV):

	ENV.SnapMetrics()

	ENV.snap_out('ok')

