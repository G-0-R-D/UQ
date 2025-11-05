
def build(ENV):

	SnapContainer = ENV.SnapContainer
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX
	snap_matrix_t = ENV.snap_matrix_t
	snap_matrix_invert = ENV.snap_matrix_invert
	snap_matrix_multiply = ENV.snap_matrix_multiply

	snap_extents_diffmatrix = ENV.snap_extents_diffmatrix
	snap_matrix_transform = ENV.snap_matrix_transform
	snap_extents_are_null = ENV.snap_extents_are_null

	class SnapCamera(SnapContainer):

		__slots__ = []
		#__slots__ = ['_render_matrix_', '_perspective_matrix_', '_rootpath_']

		"""
		def __getitem__(self, KEY):

			if KEY == 'uses_perspective':
				return self['perspective_matrix'] is not None

			elif KEY == 'render_matrix':
				# TODO


				""
				double* m = (double*)snap_getattr_at(self, "_matrix_", IDX_SnapMatrix__matrix_);
				if (!m){
					snap_error("no matrix on camera!");
					snap_memcpy(value, SNAP_IDENTITY_MATRIX, 16 * sizeof (double));
					continue;
				}
				// use value as working matrix
				snap_matrix_invert(m, (double*)value);

				double* persp = (double*)snap_getattr_at(self, "_perspective_matrix_", IDX_SnapCamera__perspective_matrix_);
				if (persp){
					snap_matrix_multiply(persp, (double*)value, (double*)value);
				}
				""

				m = self['matrix']
				rm = snap_matrix_t()

				snap_matrix_invert(m, rm)

				rootpath = self['rootpath']
				if rootpath is not None:
					raise NotImplementedError('rootpath')

					""
					// init rm for use XXX this is all wrong... we need to multiply into matrix, inverting each as we go...
					snap_memcpy(rm, SNAP_IDENTITY_MATRIX, 16 * sizeof (double));

					double* pm;
					for_item_in_SnapList(&rootpath)
						pm = (double*)snap_event_noargs((SnapNode*)&item, "render_matrix");
						if (!pm){
							snap_warning("no matrix on camera parent(%p)", item);
							continue;
						}
						snap_matrix_multiply(rm, pm, rm);
					}
					//snap_matrix_invert(rm, rm);
					""

				perspective = self['perspective_matrix']
				if perspective is not None:
					snap_matrix_multiply(perspective, rm, rm)

				return rm # ctypes


			elif KEY == 'shader':
				raise KeyError('camera does not implement a shader')

			# rootpath as is

			value = SnapContainer.__getitem__(self, KEY)

			if value is None:
				if KEY == 'render_matrix':
					value = snap_matrix_t(*SNAP_IDENTITY_MATRIX)

			return value
		"""

		@ENV.SnapProperty
		class extents:

			def set(self, MSG):
				"(snap_extents_t!)"

				current = self['extents']

				SnapContainer.extents.set(self, MSG)

				# TODO this isn't quite right, especially if camera matrix is already scaled...

				new = self['extents']

				if current is None or snap_extents_are_null(current) or new is None or snap_extents_are_null(new):
					return

				mat = snap_matrix_t()
				lock_scale = True
				uniform = True
				align = 0.5
				if snap_extents_diffmatrix(current, new, lock_scale, uniform, align, align, align, mat) != 0:
					raise ValueError("snap_extents_fit() unable to calculate diffmatrix")

				into = snap_matrix_t(*self['matrix'])
				#snap_matrix_invert(into, into)
				
				snap_matrix_transform(into, mat, into, into)
				self['matrix'] = into


				# TODO update scene visibility, map extents into self['render_matrix']['inverted']

		@ENV.SnapProperty
		class children:

			def get(self, MSG):
				return SnapContainer.children.get(self, MSG)

			def set(self, MSG):
				return SnapContainer.children.set(self, MSG)


		@ENV.SnapProperty
		class render_matrix:
			def get(self, MSG):
				"""()->snap_matrix_t"""
				
				"""
				double* m = (double*)snap_getattr_at(self, "_matrix_", IDX_SnapMatrix__matrix_);
				if (!m){
					snap_error("no matrix on camera!");
					snap_memcpy(value, SNAP_IDENTITY_MATRIX, 16 * sizeof (double));
					continue;
				}
				// use value as working matrix
				snap_matrix_invert(m, (double*)value);

				double* persp = (double*)snap_getattr_at(self, "_perspective_matrix_", IDX_SnapCamera__perspective_matrix_);
				if (persp){
					snap_matrix_multiply(persp, (double*)value, (double*)value);
				}
				"""

				m = self['matrix']
				rm = snap_matrix_t()

				snap_matrix_invert(m, rm)

				rootpath = self['rootpath']
				if rootpath is not None:
					raise NotImplementedError('rootpath')

					"""
					// init rm for use XXX this is all wrong... we need to multiply into matrix, inverting each as we go...
					snap_memcpy(rm, SNAP_IDENTITY_MATRIX, 16 * sizeof (double));

					double* pm;
					for_item_in_SnapList(&rootpath)
						pm = (double*)snap_event_noargs((SnapNode*)&item, "render_matrix");
						if (!pm){
							snap_warning("no matrix on camera parent(%p)", item);
							continue;
						}
						snap_matrix_multiply(rm, pm, rm);
					}
					//snap_matrix_invert(rm, rm);
					"""

				perspective = self['perspective_matrix']
				if perspective is not None:
					snap_matrix_multiply(perspective, rm, rm)

				return rm # ctypes


		@ENV.SnapProperty
		class uses_perspective:
			def get(self, MSG):
				"""()->bool"""
				return self['perspective_matrix'] is not None

		@ENV.SnapProperty
		class use_perspective:
			def set(self, MSG):
				"""(bool)"""
				value = MSG.args[0]
				if value:
					raise NotImplementedError() # ? assign default perspective matrix?
				else:
					self['perspective_matrix'] = None

		@ENV.SnapProperty
		class shader: pass # denied

		@ENV.SnapProperty
		class rootpath:
			def set(self, MSG):
				"""(path=list(*SnapContainer))"""
				path = MSG.unpack('path', None)
				if path:
					raise NotImplementedError()

		@ENV.SnapProperty
		class parent:
			def set(self, MSG):
				"""(parent=SnapNode!)"""
				value = MSG.unpack('parent',None)
				if value:
					self['parents'] = [value]
				else:
					raise NotImplementedError() # or set parents to None?

		@ENV.SnapProperty
		class parents:
			def set(self, MSG):
				"""()"""
				raise NotImplementedError() # TODO

		"""
		def __setitem__(self, KEY, VALUE):

			if KEY == 'use_perspective':
				if VALUE:
					raise NotImplementedError(KEY)
				else:
					self['perspective_matrix'] = None

			elif KEY == 'shader':
				raise KeyError('cannot assign shader on camera')

			elif KEY == 'rootpath':
				if VALUE:
					raise NotImplementedError(KEY)

			elif KEY == 'parent':
				self['parents'] = [VALUE]

			elif KEY == 'parents':
				ENV.snap_warning(KEY, 'not implemented') # TODO

			return SnapContainer.__setitem__(self, KEY, VALUE)
		"""

		@ENV.SnapChannel
		def fit_to_contents(self, MSG):
			'' # TODO set extents to encompass content extents, and set matrix to show them all too


		@ENV.SnapChannel
		def allocateXXX(self, MSG):
			"""(extents=snap_extents_t)"""

			"""
			if (ext){
				// TODO update perspective matrix?  aspect?
				// TODO only consider w,h ignore z of incoming?
				snap_assignattr_at(self, "_extents_", ext, 6 * sizeof (double), IDX_SnapMetrics__extents_);
				snap_emit(self, "CHANGED");
			}
			"""
			raise NotImplementedError()


		def draw(self, CTX):
			return SnapContainer.draw(self, CTX)


		"""
		def set(self, MSG):

			for attr,value in MSG.kwargs.items():

				if attr == 'parent':
					self.set(parents=[value])

				elif attr in ('rootpath', 'parents'):
					''

				elif attr == 'use_perspective':
					if value:
						raise NotImplementedError(attr)
					else:
						self.data()['perspective_matrix'] = None

				elif attr == 'shader':
					ENV.snap_warning("cannot set shader on camera")

				else:
					SnapContainer.set(self, SnapMessage(**{attr:value}))
		"""

		def __init__(self, *ITEMS):
			SnapContainer.__init__(self, *ITEMS)

			#self['render_matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
			self['perspective_matrix'] = None
			self['rootpath'] = None # how we create a parent for the camera...  store the list of parents from the scene on down...


	ENV.SnapCamera = SnapCamera

