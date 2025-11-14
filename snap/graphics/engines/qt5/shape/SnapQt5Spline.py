
def build(ENV):

	Qt5 = ENV.extern.Qt5

	SnapSpline = ENV.SnapSpline

	#snap_emit = ENV.snap_emit
	snap_raw = ENV.snap_raw

	ENGINE = ENV.graphics.__current_graphics_build__

	CMD_TYPES = {getattr(Qt5.QPainterPath, attr):attr for attr in dir(Qt5.QPainterPath) if attr.endswith('Element') and attr != 'Element'}

	MoveToElement = Qt5.QPainterPath.MoveToElement
	LineToElement = Qt5.QPainterPath.LineToElement
	CurveToElement = Qt5.QPainterPath.CurveToElement
	CurveToDataElement = Qt5.QPainterPath.CurveToDataElement

	def iter_qt5_description(QPATH):

		M = MoveToElement
		L = LineToElement
		B = CurveToElement

		start_point = None
		previous_point = None

		total = QPATH.elementCount()

		idx = 0
		while idx < total:

			e = QPATH.elementAt(idx)
			#idx += 1

			etype = e.type
			#ENV.snap_out('etype', etype, dir(e), e.__class__.__name__, e.isMoveTo(), e.isLineTo(), e.isCurveTo())
			if etype == M: # MoveToElement

				if previous_point is not None:

					if start_point is not None and previous_point[1:] == start_point[1:]:
						# TODO if we yield close then we don't want to yield the last point!
						# TODO if move else: and then check for last point and emit it, 
						yield ('C',)
					else:
						#for p in previous_point:
						#	yield p
						yield previous_point
					previous_point = None

				start_point = ('S', e.x, e.y)
				yield start_point
				previous_point = None

			else:

				if previous_point:
					#for p in previous_point:
					#	yield p
					yield previous_point
					previous_point = None

				if etype == L:
					#yield 'L'
					#yield e.x
					#yield e.y
					previous_point = ('L', e.x, e.y)

				elif etype == B:
					e2 = QPATH.elementAt(idx+1)
					e3 = QPATH.elementAt(idx+2)
					yield ('B', e.x,e.y, e2.x,e2.y, e3.x,e3.y)
					previous_point = None # a curve cannot close a path, so meh
					idx += 3 # 3 in total
					continue

				elif etype == CurveToDataElement:
					raise IndexError("curve data should have been consumed with the base curve element")

				else:
					raise TypeError("unknown Qt5 QPainterPath element type:", [attr for attr in dir(Qt5.QPainterPath) if getattr(Qt5.QPainterPath, attr) == etype], etype)
						#attr for attr in dir(Qt5.QPainterPath) if attr.endswith('Element') and \
						#attr != 'Element' and getattr(Qt5.QPainterPath, attr) == etype], etype)

			idx += 1

		if previous_point:
			if previous_point[1:] == start_point[1:]:
				yield ('C',) # TODO maybe make implicit close optional?
			else:
				yield previous_point

			previous_point = None


	class SnapQt5Spline(SnapSpline):

		# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainterPath.html

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE

		@ENV.SnapProperty
		class description:

			def get(self, MSG):
				"""()->list(*str|float|int)"""

				# TODO QPainterPath.elementCount(), elementAt(index)
				# https://doc.qt.io/qtforpython-5/PySide2/QtGui/Element.html#PySide2.QtGui.PySide2.QtGui.QPainterPath.Element
				# element: x,y, type, isCurveTo(), isLineTo(), isMoveTo()
				# types: CurveToElement, LineToElement, MoveToElement

				qpath = self.__snap_data__['__engine_data__']

				if qpath is None or qpath.isEmpty():
					#ENV.snap_out('empty descripton')
					return []

				return [e for seg in iter_qt5_description(qpath) for e in seg]

			def set(self, MSG):
				"""(
				(list|tuple(*str|int|float)),
				(*str|int|float),
				)"""

				if len(MSG.args) == 1:
					DESCRIPTION = MSG.args[0]
				else:
					DESCRIPTION = MSG.args

				axes = self['axes']
				assert axes == 2, 'incorrect axes for qt5: {} != 2'.format(axes) # TODO or just take x and y of presumably x,y,z...?

				qpath = Qt5.QPainterPath()

				#char *desc = description, *curr_desc = description;
				#double *pts = points, *curr_pts = points;

				#command_count = 0

				for seg in self._iter_segments(DESCRIPTION):
					cmd,points = seg[0],seg[1:]

					if cmd == 'L':
						start = 0
						end = 2
						while start < len(points):
							#cairo_line_to(cr, x, y)
							qpath.lineTo(*points[start:end])
							start = end
							end += 2
					elif cmd == 'B':
						# TODO degrees
						assert len(points) == 6, 'bezier != 6 currently unsupported'
						start = 0
						end = 6
						while start < len(points):
							#cairo_curve_to(cr, x1,y1, x2,y2, x3,y3)
							qpath.cubicTo(*points[start:end])
							start = end
							end += 6

					elif cmd == 'S':
						# NOTE: cairo_new_sub_path() is called by cairo_move_to()
						#cairo_move_to(cr, x, y)
						qpath.moveTo(*points[:2])

						start = 2
						end = 4
						# the rest as lines?  (otherwise we would just be drawing an invisible line lol)
						while start < len(points):
							qpath.lineTo(*points[start:end])
							start = end
							end += 2

					elif cmd == 'C':
						#cairo_close_path(cr)
						qpath.closeSubpath() # same as lineTo(start)

					else:
						#cairo_new_path(cr)
						qpath.moveTo(0,0) # ?
						raise TypeError('invalid description symbol', cmd)

				#ENV.snap_out('qpath set', DESCRIPTION)
				self.__snap_data__['__engine_data__'] = qpath

				#SnapNode_set(self, 'description', None) # DESCRIPTION XXX have to get back from qt

				#self._recalc_extents()
				self.__snap_data__['extents'] = None

				self.changed(description=DESCRIPTION, axes=axes)
				# TODO changed_data.emit()?

				return None

		def __init__(self, **SETTINGS):
			SnapSpline.__init__(self, **SETTINGS)

	ENGINE.SnapQt5Spline = SnapQt5Spline
	return SnapQt5Spline

def main(ENV):

	ENV.graphics.load('QT5')

	Qt5 = ENV.extern.Qt5

	qpath = Qt5.QPainterPath()

	#qpath.addText(0,0, ENV.Qt5.QFont(), 'hello world')
	qpath.cubicTo(1,1,2,2,3,3)
	qpath.closeSubpath()
	qpath.lineTo(20,20)
	#qpath.moveTo(10,10)
	strtypes = {getattr(Qt5.QPainterPath, attr):attr for attr in dir(Qt5.QPainterPath) if attr.endswith('Element') and attr != 'Element'}
	print(strtypes)
	print(qpath.elementCount())
	for idx in range(qpath.elementCount()):
		element = qpath.elementAt(idx)
		#if element.type == ENV.Qt5.QPainterPath.CurveToElement:
		#if element.type == ENV.Qt5.QPainterPath.CurveToDataElement:
		#	print(element.type, dir(element), element.x, element.y)
		#	break
		print(strtypes[element.type], element.x, element.y)


	
	p = ENV.graphics.QT5.SnapQt5Spline()

	ENV.snap_out('ok')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

