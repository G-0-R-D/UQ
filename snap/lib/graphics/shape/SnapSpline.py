

def build(ENV):

	SnapShape = ENV.SnapShape
	snap_extents_t = ENV.snap_extents_t

	def SnapPath_iter_segmentsXXX(DESCRIPTION, START_INDEX):

		# yield each command and point data, while validating it first XXX we won't validate here, validate when the data is used?  or in caller...

		# NOTE: a description is a list containing a letter instruction followed by the list of points (as a flat list)
		# like: ['S', 0,0, 'B', 1,2, 3,4, 5,6, 'C']

		if not DESCRIPTION:
			raise StopIteration()

		len_DESCRIPTION = len(DESCRIPTION)

		INDEX = START_INDEX or 0

		while INDEX < len_DESCRIPTION:

			c = DESCRIPTION[INDEX].upper()
			INDEX += 1
			#if c in (' ','\t','\n'): # XXX these don't apply anymore
			#	continue

			if c in (
				'L', # linear point (straight from last point)
				'S', # new segment (break in point connections if previous; left open)
				'B', # bezier segment (curved from last point, with handles) # TODO degrees (from number of points?)
				):
				# TODO NOTE: we can interpret extra points as just more of the same, like if 'L', and more than the num axes, just assume it's another L point?
				i = INDEX
				while i < len_DESCRIPTION and isinstance(DESCRIPTION[i], (int, float)):
					i += 1
				yield c, DESCRIPTION[INDEX:i]
				INDEX = i

			elif c == 'C': # close segment (connects last point and first point)
				yield c, None

			else:
				raise ValueError('unknown symbol', repr(c))

	"""
	def SnapPath_next_segment(char** description, double** pts, int axes){

		if (!description){
			return (any)"ERROR";
		}

		while (1){

			switch (**description){

				case '\0':
					return (any)"ERROR"; // EOF

				case ' ':
				case '\t':
				case '\n':
					(*description)++;
					continue;

				case 'L': # linear segment (straight from last point)
				case 'S': # new segment (break in point connections)
					(*description)++;
					*pts += axes;
					return NULL;

				case 'B': # bezier segment (curved from last point, with handles) TODO degrees
					# three points, degrees?  lookahead from description for number of degrees?
					(*description)++; // TODO subsequent nums
					# TODO while *description is a digit: advance?  get point count from degree
					*pts += 3 * axes;
					return NULL;

				case 'C':			
					(*description)++;
					return NULL;

				default:
					snap_error("invalid description symbol! \'%c\'", **description);
					return (any)"ERROR";
			}
		}

		return None
	"""
	def SnapSpline_recalc_extentsXXX(self):

		axes = self.axes()
		description = self.description()
		if not description or axes < 1:
			return

		assert len(axes) < 3, 'axes > 3 currently unsupported'

		ext = self._extents_
		if not ext:
			ext = self._extents_ = snap_extents_t()
		ext[:] = [0,0,0, 0,0,0]
		for c,points in SnapPath_iter_segments(description, 0):
			i = 0
			while i < axes:
				ext[i] = min(ext[i], min(points[i::axes]))
				ext[i+3] = max(ext[i+3], max(points[i::axes]))
				i += 1

	"""
	def SnapPath_recalc_extents(self, points, point_count, axes):

		if axes > 3 or axes < 1:
			self._extents_[:] = (0,0,0, 0,0,0)
			raise ValueError("axes out of range! %d" % axes)

		if point_count < 1:
			#snap_debug("no points for extents calc");
			self._extents_[:] = (0,0,0, 0,0,0)
			return

		point_size = axes * sizeof (double);//(bits_per_axis / 8);

		double ext[] = {0.,0.,0., 0.,0.,0.};
		// use first point as starting extents (origin might not be 0)
		snap_memcpy(ext, points, point_size);
		snap_memcpy(ext + 3, points, point_size);

		double* pt_axis = points;
		int end = point_count * axes;

		int axis;
		int i = -1;
		while (++i < end){

			axis = i % axes;

			if (ext[axis] > pt_axis[0]){
				ext[axis] = pt_axis[0];
			}
			if (ext[axis + 3] < pt_axis[0]){
				ext[axis + 3] = pt_axis[0];
			}

			pt_axis++; // next axis (not next point)
		}

		snap_assignattr_at(self, "_extents_", ext, 6 * sizeof (double), IDX_SnapMetrics__extents_);

		return NULL;
		

	}
	"""
	"""
	any _SnapPath_add_points(SnapNode* self, any MODE, int point_count, double* points){
		// TODO all data types should basically support insert or overwrite operations, so index and bool overwrite

		int* axes = (int*)snap_getattr_chain(self, "ENV", "axes");
		if (!axes) axes = (int*)snap_getattr(self, "_axes_");
		// try to get from description header?
		if (!axes){
			snap_error("axes not defined!");
			return (any)"ERROR";
		}

		if (MODE == (any)"LINEAR"){
			
		}

		else if (MODE == (any)"BEZIER"){

		}

		else if (MODE == (any)"START"){

		}
		else if (MODE == (any)"RECT" || MODE == (any)"RECTANGLE"){
			// x y w h + new or continue optional?
		}
		else if (MODE == (any)"CIRCLE"){
			// points define center x,y,z? depending on axes, and radius
		}
		else if (MODE == (any)"ARC"){
			
		}
		else if (MODE == (any)"CLOSE"){
			// close if not already closed (last is C)
			// ie. if last description is not C, add a C, no points!
		}
		else {
			snap_error("unknown MODE \"%s\"", (char*)MODE);
			return (any)"ERROR";
		}

		snap_emit(self, "CHANGED");

		return NULL;
	}
	"""

	class SnapSpline(SnapShape):

		__slots__ = []

		#__slots__ = ['_description_', '_axes_']

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				# TODO recalc if None

				ext = self.__snap_data__['extents']
				if ext is not None:	
					return ext

				axes = self['axes']
				description = self['description']
				if not description or axes < 1:
					return snap_extents_t(0,0,0, 0,0,0)

				assert axes <= 3, 'axes > 3 currently unsupported'

				ext = [None] * 6
				for seg in self._iter_segments(description):
					#ENV.snap_warning('seg', seg)
					points = seg[1:]
					if not points:
						continue
					i = 0
					while i < axes:

						pts = points[i::axes]
						if ext[i] is None:
							ext[i] = min(pts)
						else:
							ext[i] = min(ext[i], min(pts))

						idx = i+3
						if ext[idx] is None:
							ext[idx] = max(pts)
						else:
							ext[idx] = max(ext[idx], max(pts))

						i += 1

				return snap_extents_t(*[x if x is not None else 0 for x in ext])


			#set = None # TODO use something like set = ENV.SnapProperty.FORBIDDEN?
			def set(self, MSG):
				""
				raise ValueError('setting extents of {} not allowed'.format(self.__class__.__name__))

		@ENV.SnapProperty
		class description:
			def get(self, MSG):
				"""()->list(*str|float|int)"""
				# NOTE: a description is a list containing a letter instruction followed by the list of points (as a flat list)
				# like: ['S', 0,0, 'B', 1,2, 3,4, 5,6, 'C']
				return self.__snap_data__['description'] or []

			def set(self, MSG):
				"""(
				(list(*str|float|int)!),
				(*str|float|int),
				)"""
				if not MSG.args:
					d = []
				elif isinstance(MSG.args[0], (list, tuple)):
					d = MSG.args[0]
				else:
					d = list(MSG.args)

				axes = self['axes']

				for seg in self._iter_segments(d):
					if (len(seg)-1) % axes:
						raise ValueError('incorrect number of points for axes!', seg, axes)

				self.__snap_data__['description'] = d

				self.__snap_data__['extents'] = None # for recalc when accessed
				self.changed(description=d)

		@ENV.SnapProperty
		class axes:
	
			def get(self, MSG):
				"""()->int"""
				return self.__snap_data__['axes'] or 2

			def set(self, MSG):
				"""(int)"""
				value = MSG.args[0]
				if value is None:
					value = 2
				else:
					assert isinstance(value, int), 'must provide int'
				existing = self['axes']
				if value != existing:
					assert not self['description'], 'cannot change axes with active description (clear first)'
				self.__snap_data__['axes'] = value

				self.changed(axes=value)

		# TODO points()?

		#def extents(self, MSG):
		#	return self.data().get('extents', snap_extents_t())


		@ENV.SnapProperty
		class fill:

			def get(self, MSG):
				"()->SnapPaint"
				d = self.__snap_data__['fill']
				if d:
					return d.copy()
				return d

			def set(self, MSG):
				"(SnapPaint!)" # Color, Texture, Gradient, Pattern... TODO accept dict as well?  even though it's just one arg, we can use the keyname...
				arg = MSG.args[0]
				if arg is None:
					del self.__snap_data__['fill']
				else:
					if not isinstance(arg, dict):
						assert isinstance(arg, ENV.SnapPaint), 'shape fill must be SnapPaint type, not: {}'.format(type(arg))
						self.__snap_data__['fill'] = {'paint':arg}
					else:
						valid = {}
						for attr,value in arg.items():
							if attr in ('color', 'paint', 'texture', 'gradient', 'pattern'):
								assert 'paint' not in valid, 'duplicate values for paint element!'
								valid['paint'] = value
							else:
								ENV.snap_warning('unknown fill attr:', repr(attr))

						self.__snap_data__['fill'] = valid

				self.changed(fill=self.__snap_data__['fill'])

		@ENV.SnapProperty
		class stroke:

			def get(self, MSG):
				"()->SnapPaint"
				d = self.__snap_data__['stroke']
				if d:
					return d.copy()
				return d

			def set(self, MSG):
				"(SnapPaint!)" # TODO
				arg = MSG.args[0]
				if arg is None:
					del self.__snap_data__['stroke']
				else:
					# assign from dict
					if not isinstance(arg, dict):
						assert isinstance(arg, ENV.SnapPaint)
						# TODO clear previous settings, this is JUST the paint assign...
						self.__snap_data__['stroke'] = {'paint':arg}
					else:
						valid = {}

						for attr,value in arg.items():

							if value is None:
								continue

							if attr in ('color','paint','texture','gradient','pattern'):
								assert 'paint' not in valid, 'duplicate values for paint element!'
								valid['paint'] = value
							elif attr in ('thick', 'thickness','width'):
								valid['width'] = float(value)
							elif attr in ('dash','dashes'):
								'[offset, on/off pattern]'
								valid['dash'] = list(value)
							elif attr == 'under':
								valid['under'] = bool(value)

							# TODO miter, cap, join, miter_limit
							else:
								ENV.snap_warning('unknown stroke attr:', repr(attr))

						self.__snap_data__['stroke'] = valid

				self.changed(stroke=self.__snap_data__['stroke'])

					# TODO if no paint assigned then there is no render!  or use fill?

				# TODO then the context is obtained from the engine and we queue the calls using the base class...?

		# TODO interactive and lookup?  interactive should assign threshold value?

		@stroke.shared
		class line: pass

		@stroke.shared
		class outline: pass

		@stroke.shared
		class border: pass

		@ENV.SnapChannel
		def clear(self, MSG):
			"""()"""
			self['description'] = None
			#data['axes'] = 2 # XXX keep it as it is

		def draw(self, CTX):

			stroke_data = self.__snap_data__['stroke']
			if stroke_data:
				paint = stroke_data['paint']
				CTX.cmd_stroke_spline(paint, self)

			fill_data = self.__snap_data__['fill']
			if fill_data:
				paint = fill_data['paint']
				#ENV.snap_out('fill', paint, paint['__engine_data__'], self['description'])
				CTX.cmd_fill_spline(paint, self)

		def lookup(self, CTX):
			'' # TODO just draw with black, and register self as sub-element of result...


		def _recalc_extentsXXX(self):
			# XXX moved to extents get()

			axes = self['axes']
			description = self['description']
			if not description or axes < 1:
				return

			assert axes <= 3, 'axes > 3 currently unsupported'

			ext = self['extents']

			ext[:] = [0,0,0, 0,0,0] # TODO don't start with 0's, until actually assigned...
			for seg in self._iter_segments(description):
				#ENV.snap_warning('seg', seg)
				points = seg[1:]
				if not points:
					continue
				i = 0
				while i < axes:
					ext[i] = min(ext[i], min(points[i::axes]))
					ext[i+3] = max(ext[i+3], max(points[i::axes]))

					i += 1


		#def _iter_segments(self, DESCRIPTION, START_INDEX):
		def _iter_segments(self, DESCRIPTION):
			# TODO use segments property?  and then just assign the description locally before iterating it?

			# yield each command and point data, while validating it first XXX we won't validate here, validate when the data is used?  or in caller...

			# NOTE: a description is a list containing a letter instruction followed by the list of points (as a flat list)
			# like: ['S', 0,0, 'B', 1,2, 3,4, 5,6, 'C']

			# TODO should this just be on the editor?  editor.next()?
			# generalize to str followed by int/float (or nothing)

			if not DESCRIPTION:
				return

			len_DESCRIPTION = len(DESCRIPTION)

			START_INDEX = INDEX = 0

			while INDEX < len_DESCRIPTION:

				while INDEX < len_DESCRIPTION and not isinstance(DESCRIPTION[INDEX], str):
					INDEX += 1

				if INDEX > START_INDEX:
					ENV.snap_warning('read description: skipped non-string at expected string entry', START_INDEX)
					START_INDEX = INDEX

				INDEX += 1

				while INDEX < len_DESCRIPTION and isinstance(DESCRIPTION[INDEX], (int,float)):
					INDEX += 1

				#if INDEX == START_INDEX:
				#	break

				yield DESCRIPTION[START_INDEX:INDEX]

				START_INDEX = INDEX
				

				"""
				cmd = DESCRIPTION[INDEX].upper()
				INDEX += 1
				#if cmd in (' ','\t','\n'): # XXX these don't apply anymore
				#	continue

				if cmd in (
					'L', # linear point (straight from last point)
					'S', # new segment (break in point connections if previous; left open)
					'B', # bezier segment (curved from last point, with handles) # TODO degrees (from number of points?)
					):
					# TODO NOTE: we can interpret extra points as just more of the same, like if 'L', and more than the num axes, just assume it's another L point?
					i = INDEX
					while i < len_DESCRIPTION and isinstance(DESCRIPTION[i], (int, float)):
						i += 1
					yield cmd, DESCRIPTION[INDEX:i]
					INDEX = i

				elif cmd == 'C': # close segment (connects last point and first point)
					yield cmd, None

				else:
					raise ValueError('unknown symbol', repr(cmd))
				"""


		def _assign(self, DESCRIPTION):

			self['description'] = DESCRIPTION
			#self._axes_ = axes



			"""
			char* desc = description;
			double* pts = points;

			int command_count = 0;
			while (SnapPath_next_segment(&desc, &pts, axes) != (any)"ERROR"){
				command_count++;
			}
			int point_count = (pts - points) / axes;

			__SnapPath_assign(self, description, command_count, points, point_count, axes);

			_SnapPath_recalc_extents(self, points, point_count, axes);
			"""


			#snap_emit(self, "CHANGED",
				#description=DESCRIPTION,
				#points=points,
				#axes=self._axes_ # TODO put the axes into the description?
				#)


		def __init__(self, **SETTINGS):
			SnapShape.__init__(self, **SETTINGS)


	ENV.SnapSpline = SnapSpline


def main(ENV):

	spline = ENV.SnapSpline(description=['s',1,2, 3,4, 'B',5,6, 7,8, 9,10, 'L', 11,12,13,14, 'C'], axes=2)

	ENV.snap_out('description', spline['description'])
	for seg in spline._iter_segments(spline['description']):
		ENV.snap_out(seg)

	ENV.snap_out('extents', spline['extents'][:])


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

