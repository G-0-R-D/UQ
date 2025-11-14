
def build(ENV):

	SnapContext = ENV.SnapContext

	Qt5 = ENV.extern.Qt5
	QPainter = Qt5.QPainter
	QTransform = Qt5.QTransform
	QImage = Qt5.QImage
	QBrush = Qt5.QBrush
	QPen = Qt5.QPen
	QRect = Qt5.QRect
	QRectF = Qt5.QRectF
	QPoint = Qt5.QPoint
	QPointF = Qt5.QPointF

	IntersectClip = Qt5.Qt.IntersectClip # ReplaceClip, IntersectClip, NoClip

	snap_matrix_t = ENV.snap_matrix_t
	snap_matrix_multiply = ENV.snap_matrix_multiply
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX
	snap_raw = ENV.snap_raw
	snap_extents_t = ENV.snap_extents_t

	ENGINE = ENV.graphics.__current_graphics_build__

	def set_antialias(PAINTER, BOOL):
		return PAINTER.setRenderHint(QPainter.Antialias, BOOL)

	class SnapQt5Context(SnapContext):

		BLENDMODES = {
			'Clear':QPainter.CompositionMode_Clear,
			'ColorBurn':QPainter.CompositionMode_ColorBurn,
			'ColorDodge':QPainter.CompositionMode_ColorDodge,
			'Darken':QPainter.CompositionMode_Darken,
			'Destination':QPainter.CompositionMode_Destination,
			'DestinationAtop':QPainter.CompositionMode_DestinationAtop,
			'DestinationIn':QPainter.CompositionMode_DestinationIn,
			'DestinationOut':QPainter.CompositionMode_DestinationOut,
			'DestinationOver':QPainter.CompositionMode_DestinationOver,
			'Difference':QPainter.CompositionMode_Difference,
			'Exclusion':QPainter.CompositionMode_Exclusion,
			'HardLight':QPainter.CompositionMode_HardLight,
			'Lighten':QPainter.CompositionMode_Lighten,
			'Multiply':QPainter.CompositionMode_Multiply,
			'Overlay':QPainter.CompositionMode_Overlay,
			'Plus':QPainter.CompositionMode_Plus,
			'Screen':QPainter.CompositionMode_Screen,
			'SoftLight':QPainter.CompositionMode_SoftLight,
			'Source':QPainter.CompositionMode_Source,
			'SourceAtop':QPainter.CompositionMode_SourceAtop,
			'SourceIn':QPainter.CompositionMode_SourceIn,
			'SourceOut':QPainter.CompositionMode_SourceOut,
			'SourceOver':QPainter.CompositionMode_SourceOver,
			'Xor':QPainter.CompositionMode_Xor,
			'ClearDestination':QPainter.RasterOp_ClearDestination,
			'NotDestination':QPainter.RasterOp_NotDestination,
			'NotSource':QPainter.RasterOp_NotSource,
			'NotSourceAndDestination':QPainter.RasterOp_NotSourceAndDestination,
			'NotSourceAndNotDestination':QPainter.RasterOp_NotSourceAndNotDestination,
			'NotSourceOrDestination':QPainter.RasterOp_NotSourceOrDestination,
			'NotSourceOrNotDestination':QPainter.RasterOp_NotSourceOrNotDestination,
			'NotSourceXorDestination':QPainter.RasterOp_NotSourceXorDestination,
			'SetDestination':QPainter.RasterOp_SetDestination,
			'SourceAndDestination':QPainter.RasterOp_SourceAndDestination,
			'SourceAndNotDestination':QPainter.RasterOp_SourceAndNotDestination,
			'SourceOrDestination':QPainter.RasterOp_SourceOrDestination,
			'SourceOrNotDestination':QPainter.RasterOp_SourceOrNotDestination,
			'SourceXorDestination':QPainter.RasterOp_SourceXorDestination,
		}

		__slots__ = []#'__pen__', '__brush__', '__needs_update__']

		@ENV.SnapProperty
		class imageXXX:
			def set(self, MSG):
				"""(SnapQt5Image!)"""
				image = MSG.args[0]

				ENV.snap_out('image assign')
				raise NotImplementedError('cannot change image of active render context')

				self.finish()

				current_image = self['image']
				if current_image is not None:
					current_image.changed.ignore(self.changed)

				ptr = self.__snap_data__['engine_context'] = None

				if image is not None:
					assert isinstance(image, ENGINE.Image), 'wrong image type: {}'.format(type(image))

					#ENV.snap_out('engine data', value.__engine_data__())
					# NOTE: being a bit careful here because init of QPainter(None) will segfault once used!
					qimage = image['__engine_data__']
					assert isinstance(qimage, QImage), 'not a QImage: {}'.format(type(qimage))
					ptr = self.__snap_data__['engine_context'] = QPainter(qimage)
					image.changed.listen(self.changed)

					#cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE)
					ptr.setRenderHint(QPainter.Antialiasing, False)
					
				self.__snap_data__['image'] = image
				#self.changed(image=image)
				ENV.snap_out('image assign complete')

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE

		#def cmd_append_path(self, PATH):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-append-path
		#	cairo_append_path(self._engine_context_, PATH._engine_data_)

		#def cmd_arc(self, xc,yc, radius, angle1, angle2):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-arc
		#	cairo_arc(self._engine_context_, xc,yc, radius, angle1, angle2)

		#def cmd_arc_negative(self, xc,yc, radius, angle1, angle2):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-arc-negative
		#	cairo_arc_negative(self._engine_context_, xc,yc, radius, angle1, angle2)

		@ENV.SnapChannel
		def changed(self, MSG):
			""
			#if MSG.source is self['image']:
			#	ENV.snap_warning('image changed recieved in SnapContext')
			#else:
			#	ENV.snap_warning('image changed', MSG, MSG.source)

			return SnapContext.changed(self, MSG)
			

		def qt5_setClipPath(self, QT_PATH, QT_OP):
			#cairo_clip(self._engine_context_)
			self['engine_context'].setClipPath(QT_PATH, QT_OP)
			#Qt.ReplaceClip
			#Qt.IntersectClip

		#def cmd_clip_extents(self):

		#def cmd_clip_preserve(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-clip-preserve
		#	cairo_clip_preserve(self._engine_context_)

		#def cmd_close_path(self):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-close-path
		#	cairo_close_path(self._engine_context_)


		#def cmd_curve_to(self, x1,y1, x2,y2, x3,y3):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-curve-to
		#	cairo_curve_to(self._engine_context_, x1,y1, x2,y2, x3,y3)


		#def cmd_fill(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-fill
		#	cairo_fill(self._engine_context_)

		# def cmd_fill_extents(self):

		#def cmd_fill_preserve(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-fill-preserve
		#	cairo_fill_preserve(self._engine_context_)

		#def cmd_glyph_path(self, ARGS):

		#def cmd_layout_line_path(self, LINE_LAYOUT):
		#	# https://gtk.developpez.com/doc/en/pango/pango-Layout-Objects.html#pango-layout-get-line-readonly
		#	# https://gtk.developpez.com/doc/en/pango/pango-Layout-Objects.html#pango-layout-get-line-readonly
		#	# LINE_LAYOUT = pango_layout_get_line_readonly(TEXT._engine_data_, 0)
		#	pango_cairo_layout_line_path(self._engine_context_, LINE_LAYOUT)

		#def cmd_layout_path(self, TEXT):
		#	# https://gtk.developpez.com/doc/en/pango/pango-Cairo-Rendering.html#pango-cairo-layout-path
		#	pango_cairo_layout_path(self._engine_context_, TEXT._engine_data_)

		#def cmd_line_to(self, X, Y):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-line-to
		#	cairo_line_to(self._engine_context_, X, Y)

		#def cmd_mask(self, TEXTURE):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-mask
		#	cairo_mask(self._engine_context_, TEXTURE._engine_data_)
		# TODO must go through QPixmap.setMask() ?
		# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPixmap.html#PySide2.QtGui.PySide2.QtGui.QPixmap.setMask

		#def cmd_mask_surface(self, TEXTURE, X, Y):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-mask-surface
		#	cairo_mask_surface(self._engine_context_, TEXTURE._engine_data_, X, Y)

		#def cmd_move_to(self, X, Y):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-move-to
		#	cairo_move_to(self._engine_context_, X, Y)

		#def cmd_new_path(self):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-new-path
		#	cairo_new_path(self._engine_context_)

		#def cmd_new_sub_path(self):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-new-sub-path
		#	cairo_new_sub_path(self._engine_context_)

		#def cmd_paint(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-paint
		#	cairo_paint(self._engine_context_)

		#def cmd_paint_with_alpha(self, ALPHA):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-paint-with-alpha
		#	cairo_paint_with_alpha(self._engine_context_, ALPHA) # alpha = 0.0 -> 1.0
		# XXX this is path with pen now right?

		#def cmd_pop_group_to_source(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-pop-group-to-source
		#	cairo_pop_group_to_source(self._engine_context_)

		#def cmd_push_group(self):
		#	# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-push-group
		#	cairo_push_group(self._engine_context_)

		#def cmd_rectangle(self, X, Y, W, H):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-rectangle
		#	cairo_rectangle(self._engine_context_, X, Y, W, H)

		#def cmd_rel_curve_to(self, x1,y1, x2,y2, x3,y3):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-rel-curve-to
		#	cairo_rel_curve_to(self._engine_context_, x1,y1, x2,y2, x3,y3)

		#def cmd_rel_line_to(self, X, Y):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-rel-line-to
		#	cairo_rel_line_to(self._engine_context_, X, Y)

		#def cmd_rel_move_to(self, X, Y):
		#	# https://www.cairographics.org/manual/cairo-Paths.html#cairo-rel-move-to
		#	cairo_rel_move_to(self._engine_context_, X, Y)

		def qt5_resetClip(self):
			# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainter.html#PySide2.QtGui.PySide2.QtGui.QPainter.setClipping
			self['engine_context'].setClipping(False)


		#def cmd_show_layout_line(self, TEXT):
		#	# https://www.manpagez.com/html/pango/pango-1.42.0/pango-Layout-Objects.php#pango-layout-get-line
		#	#pango_cairo_show_layout_line(self._engine_context_, pango_layout_get_line_readonly(TEXT._engine_data_))
		#	raise NotImplementedError(SNAP_FUNCNAME())

		#def cmd_drawPath(self, PATH):
		#	# same as strokePath, but uses current brush and pen
		#	self._engine_context_.drawPath(PATH)

		def qt5_fillPath(self, PATH, BRUSH):
			self['engine_context'].fillPath(PATH, BRUSH)

		def qt5_strokePath(self, PATH, PEN):
			#cairo_stroke(self._engine_context_)
			self['engine_context'].strokePath(PATH, PEN)

		def qt5_setClipping(self, BOOL):
			self['engine_context'].setClipping(BOOL)


		# --- CMD ----------------------------------------------------------------------------------------------------

		def cmd_set_transform(self, MATRIX):
			raise NotImplementedError()


		def cmd_set_matrix(self, MATRIX):
			# NOTE: this is user api in local coordinates, set relative to current offset!
			m = snap_matrix_t()
			# NOTE: that self._matrix_ stays what it is...
			snap_matrix_multiply(self['matrix'], MATRIX['matrix'], m)
			self['engine_context'].setWorldTransform(QTransform(m[0], m[4], m[1], m[5], m[3], m[7]))

		def cmd_transform(self, MATRIX):
			# MATRIX is the change to apply to self._matrix_
			m = snap_matrix_t()
			snap_matrix_multiply(MATRIX['matrix'], self['matrix'], m) # TODO local?
			self['engine_context'].setWorldTransform(QTransform(m[0], m[4], m[1], m[5], m[3], m[7]))

		def cmd_apply_matrix(self):
			# because engine context matrix doesn't actually have to be set until we use it
			# this is always the first call of a shader...

			m = self['matrix']
			#ENV.snap_out("apply matrix", m[:])
			self['engine_context'].setWorldTransform(QTransform(
				m[0], m[4],
				m[1], m[5],
				m[3], m[7],
				))

		#def cmd_stroke_extentsXXX(self):
		#	#cairo_stroke_extents(self._engine_context_, x1, y1, x2, y2) -> min and max point (by reference though...)
		#	raise NotImplementedError(SNAP_FUNCNAME())

		#def cmd_stroke_preserve(self):
		#	cairo_stroke_preserve(self._engine_context_)

		#def cmd_text_path(self, STRING):
		#	# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainterPath.html#PySide2.QtGui.PySide2.QtGui.QPainterPath.addText
		#	# TODO QPainterPath can be set using text (but isn't itself a path?)
		#	# XXX go with adding text into the path itself...  that makes sense!
		#	#cairo_text_path(self._engine_context_, STRING)
		#	raise NotImplementedError()


		def cmd_clip(self, SHAPE):
			self['engine_context'].setClipPath(SHAPE['__engine_data__'], IntersectClip)

		def cmd_clip_extents(self, EXTENTS):
			# to be able to clip to a rect quick and easy
			E = EXTENTS
			self['engine_context'].setClipRect(QRectF(E[0], E[1], E[3]-E[0], E[4]-E[1]), IntersectClip)



		# TODO other primitives?  arc?  triangle?  rect?


		def cmd_draw_text(self, TEXT):
			# this is full text rendering (as a document, with markups etc...),
			# otherwise convert the text to a path and use it as a path
			TEXT['__engine_data__'].render(self['engine_context'])


		def cmd_fill_spline(self, PAINT, PATH):
			self['engine_context'].fillPath(PATH['__engine_data__'], QBrush(PAINT['__engine_data__']))

		cmd_fill_shape = cmd_fill_spline

		def cmd_fill_mesh(self, PAINT, MESH):
			raise NotImplementedError()

		# cmd_fill_rect just use this:
		def cmd_fill_extents(self, PAINT, EXTENTS):
			# NOTE: image as a shape can be done here...  draws a rectangle using extents() parameter
			E = EXTENTS
			self['engine_context'].fillRect(QRectF(E[0], E[1], E[3]-E[0], E[4]-E[1]), QBrush(PAINT['__engine_data__']))

		def cmd_fill_circle(self, PAINT, x,y, radius):
			# https://stackoverflow.com/questions/61034583/drawing-a-circle-on-a-qwidget-python-gui
			# POS_RADIUS is (x,y,radius)
			# other shapes use path, this one is supported just because a perfect/smooth circle requires a lot of points...!
			# drawEllipse after ptr.setBrush()?
			ptr = self['engine_context']
			#ptr.qp.setPen(QPen(Qt.black, 3, Qt.DashLine))
			ptr.setBrush(QBrush(PAINT['__engine_data__']))
			ptr.drawEllipse(QPointF(x,y), radius, radius)

		def cmd_fill_ellipse(self, PAINT, x,y, w,h):
			raise NotImplementedError()


		def cmd_stroke_spline(self, PAINT, PATH):
			self['engine_context'].strokePath(PATH['__engine_data__'], QPen(PAINT['__engine_data__']))

		cmd_stroke_shape = cmd_stroke_spline

		def cmd_stroke_mesh(self, PAINT, MESH):
			raise NotImplementedError()

		def cmd_stroke_extents(self, PAINT, EXTENTS):
			# NOTE: to do a simple rectangle render you can make a Metrics(...) instance just for the rect...
			E = EXTENTS
			CTX = self['engine_context']
			CTX.setPen(PAINT['__engine_data__'])
			#self['engine_context'].drawRect(QRectF(E[0], E[1], E[3]-E[0], E[4]-E[1]), QBrush(PAINT['__engine_data__']))
			#CTX.drawRect(int(E[0]), int(E[1]), int(E[3]-E[0]), int(E[4]-E[1]))
			CTX.drawRect(QRectF(E[0], E[1], E[3]-E[0], E[4]-E[1]))

		def cmd_stroke_circle(self, PAINT, x,y, radius):
			# drawArc()?
			raise NotImplementedError()

		def cmd_stroke_ellipse(self, PAINT, x,y, w,h):
			raise NotImplementedError()


		def cmd_set_blendmode(self, MODE):
			raise NotImplementedError()



		# TODO primitives?  draw_rect, draw_circle, ...?  or just stick to path representations of those forms?  maybe circle/arc is useful cause it costs a lot of points...


		def cmd_save(self):
			# TODO self._config_['cmd_save'] = self._config_ ?  self._config_ = self._config_.copy()?
			self['engine_context'].save()

		def cmd_restore(self):
			# TODO restore config
			self['engine_context'].restore()




		#def cmd_set_stroke_after(self, BOOL):
		#	'' # XXX this is just the order of operations of draw/stroke calls, put in operator!

		# NOTE: Qt puts these onto the pen, but I don't want to have a different 'paint' for line/fill, paint is paint!

		def cmd_set_line_width(self, UNITS):
			# 0.0->1.0?
			SnapNode_get(self, 'config')['cmd_set_line_width'] = UNITS
			raise NotImplementedError()

		def cmd_set_line_miter(self, MODE):
			SnapNode_get(self, 'config')['cmd_set_line_miter'] = MODE
			raise NotImplementedError()

		def cmd_set_line_miter_limit(self, LIMIT):
			SnapNode_get(self, 'config')['cmd_set_line_miter_limit'] = LIMIT
			raise NotImplementedError()

		def cmd_set_line_join(self, MODE):
			SnapNode_get(self, 'config')['cmd_set_line_join'] = MODE
			raise NotImplementedError()

		def cmd_set_line_cap(self, MODE):
			SnapNode_get(self, 'config')['cmd_set_line_cap'] = MODE
			raise NotImplementedError()

		#def cmd_set_fill_rule(self, MODE) XXX make this engine specific only...

		def cmd_set_dash(self, POINTS):
			# points are (offset, on, off, on, off, ...)
			SnapNode_get(self, 'config')['cmd_set_dash'] = POINTS
			raise NotImplementedError()




		def cmd_restore(self):
			# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainter.html#PySide2.QtGui.PySide2.QtGui.QPainter.restore
			self['engine_context'].restore()

		def cmd_save(self):
			# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainter.html#PySide2.QtGui.PySide2.QtGui.QPainter.save
			# TODO we need to save the config too so we can reload it!  (just put the current config dict into conf['cmd_save'])?
			self['engine_context'].save()

		def cmd_draw_text(self, *TEXT):
			#pango_cairo_show_layout(self._engine_context_, TEXT._engine_data_)
			# TEXT._engine_data_ is QTextEdit widget
			ctx = self['engine_context']
			for text in TEXT:
				text['__engine_data__'].render(ctx)

		# CONFIG:

		def cmd_set_antialias(self, PERCENTAGE):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-antialias
			#self._register_deconfig(cairo_set_antialias, cairo_get_antialias(self._engine_context_))
			#cairo_set_antialias(self._engine_context_, CAIRO_ANTIALIAS_VALUE)
			#ptr = self._engine_context_
			#self._register_deconfig(set_antialias, ptr.testRenderHint(QPainter.Antialiasing))
			self['engine_context'].setRenderHint(QPainter.Antialiasing, PERCENTAGE >= .5)

		def cmd_set_dash(self, DASH_INFO):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-dash
			#cairo_set_dash(self._engine_context_, *DASH_INFO)#DASHES['array'], len(DASHES['array']), DASHES['offset'])
			# TODO dash is on pen now
			# DASH_INFO is array of (offset, on, off, on, off, ...) all floats
			raise NotImplementedError()

		def cmd_set_fill_rule(self, CAIRO_FILL_RULE):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-fill-rule
			#self._register_deconfig(cairo_set_fill_rule, cairo_get_fill_rule(self._engine_context_))
			#cairo_set_fill_rule(self._engine_context_, CAIRO_FILL_RULE)
			raise NotImplementedError()
			# TODO fill rule is now on the path...  put it on the shader by setting it on the path before use?

		def cmd_set_line_capXXX(self, CAIRO_LINE_CAP):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-line-cap
			#self._register_deconfig(cairo_set_line_cap, cairo_get_line_cap(self._engine_context_))
			#cairo_set_line_cap(self._engine_context_, CAIRO_LINE_CAP)
			raise NotImplementedError()

		def cmd_set_line_joinXXX(self, CAIRO_LINE_JOIN):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-line-join
			#self._register_deconfig(cairo_set_line_join, cairo_get_line_join(self._engine_context_))
			#cairo_set_line_join(self._engine_context_, CAIRO_LINE_JOIN)
			raise NotImplementedError()

		def cmd_set_line_widthXXX(self, LINE_WIDTH):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-line-width
			#self._register_deconfig(cairo_set_line_width, cairo_get_line_width(self._engine_context_))
			#cairo_set_line_width(self._engine_context_, LINE_WIDTH)
			raise NotImplementedError()

		def cmd_set_miter_limitXXXX(self, MITER_LIMIT):
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-miter-limit
			#ptr = self._engine_context_
			self._register_deconfig(cairo_set_miter_limit, cairo_get_miter_limit(self._engine_context_))
			#cairo_set_miter_limit(self._engine_context_, MITER_LIMIT)
			# TODO these options are now in the QPen
			raise NotImplementedError()

		def qt_setPen(self, PEN):
			# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPen.html#PySide2.QtGui.PySide2.QtGui.QPen
			# NOTE: miter,join,cap,width, and all line settings are in the pen config
			# painter.setPen(QPen(QColor(79, 106, 25), 1, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))
			#ptr = self._engine_context_
			#self._register_deconfig(QPainter.setPen, ptr.pen())
			self['engine_context'].setPen(PEN)

		def qt_setCompositionMode(self, MODE):
			# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPainter.html#PySide2.QtGui.PySide2.QtGui.QPainter.CompositionMode
			#ptr = self._engine_context_
			#self._register_deconfig(QPainter.setCompositionMode, ptr.compositionMode())
			self['engine_context'].setCompositionMode(MODE)

		# TODO cmd_set_fill and cmd_set_stroke and fill can accept a texture?
		def cmd_set_source(self, SOURCE): # TODO deconfig for this one?
			# https://www.cairographics.org/manual/cairo-cairo-t.html#cairo-set-source
			#cairo_set_source(self._engine_context_, SOURCE._engine_data_)
			# TODO is this pen, brush, image?
			# TODO this was fill_color, so QBrush?
			raise NotImplementedError()



		# CUSTOM:

		def cmd_fill_extents(self, PAINT, EXTENTS):
			ext = EXTENTS#METRICS['extents']
			#cairo_rectangle(self._engine_context_, ext[0], ext[1], ext[3]-ext[0], ext[4]-ext[1])
			# TODO assign the brush
			ctx = self['engine_context']
			#ctx.setBrush(PAINT['__engine_data__'])
			#ctx.drawRect(int(ext[0]), int(ext[1]), int(ext[3]-ext[0]), int(ext[4]-ext[1]))
			ctx.fillRect(QRect(int(ext[0]), int(ext[1]), int(ext[3]-ext[0]), int(ext[4]-ext[1])), PAINT['__engine_data__'])

		def cmd_draw_meshXXX(self, MESH):
			# TODO?  series of triangles in path?  bunch of move_to?  and calculate points for current matrix?  within reason...
			# if mesh is really large then maybe summarize it?
			# TODO get extents from mesh/shape?
			snap_raw("""
			double* ext = (double*)snap_getattr_at((SnapNode*)&args_list->data[(*args_idx)++], "_extents_", IDX_SnapMetrics__extents_);
			cairo_rectangle((cairo_t*)renderinfo->context, ext[0], ext[1], ext[3]-ext[0], ext[4]-ext[1]);
			//SnapCairoShader_ins_rectangle(_SnapCairo_ins_args_use_);
			""")
			raise NotImplementedError()


		def cmd_set_blendmode(self, STRING):
			self['engine_context'].setCompositionMode(self.BLENDMODES[STRING])
			self['config']['cmd_set_blendmode'] = STRING


		def cmd_check_interact(self, threshold=255, **EXTRAS):
			# NOTE: threshold is 0->255, if 0 then it will always be true...
			# by default any amount of transparency (< 255) is considered a 'miss')

			if self['only_first_lookup'] and self['lookup_results']:
				return

			# to pixel check for interact collision
			#unsigned char* pixel = (unsigned char*)snap_getattr_at(&renderinfo->image, "_pixels_", IDX_SnapImage__pixels_);

			qimage = self['image']['__engine_data__']

			#ENV.snap_out('pixel', list(qimage.pixel(0,0).to_bytes(4, 'little')))

			#pixel = self['image']['pixels']
			#snap_out("pixel values %01x %01x %01x %01x", pixel[0], pixel[1], pixel[2], pixel[3]);
			#snap_out("pixel values %u %u %u %u", pixel[0], pixel[1], pixel[2], pixel[3]);
			#if ord(pixel[3]) > threshold: # TODO > make threshold of alpha user assignable (assign to self / shader?  or renderinfo?)
			#ENV.snap_out('lookup pixel', pixel['data'])
			if (qimage.pixel(0,0) >> 24 & 255) >= threshold:
			#if pixel['data'][3] >= threshold:
				#self['lookup_results'].extend([self['current_container'], snap_matrix_t(*self['matrix'])])
				self['lookup_results'].append(dict(graphic=self['current_container'], offset=snap_matrix_t(*self['matrix']), **EXTRAS))
			qimage.setPixel(0,0, 0) # always set to neutral just in case a different threshold is used later...
			#self['image']['pixels']['data'][:] = 0
			#self['image'].clear()
			#pixel['data'][:] = 0


		@ENV.SnapChannel
		def activate(self, MSG):
			# TODO?  self._engine_context_ = QPainter(self._image_.__engine_data__())?
			#self._engine_context_.begin(self._image_.__engine_data__())
			#ENV.snap_out("<SnapQt5Context activate()>", self._engine_context_)
			#ptr = self._engine_context_ = QPainter(self._image_.__engine_data__())
			data = self.__snap_data__

			image = data['image']
			assert isinstance(image, ENGINE.Image), 'wrong image type: {}'.format(type(image))
			#ENV.snap_error('GOT HERE')
			engine_context = data['engine_context']
			assert engine_context is None, 'already activated'
			ptr = data['engine_context'] = QPainter(image['__engine_data__'])
			ptr.setClipping(True)
			#ENV.snap_out("</SnapQt5Context activate()>")

		@ENV.SnapChannel
		def reset(self, MSG):
			# TODO back to defaults?  just call finish and activate()?  or set back to defaults explicitly?
			ptr = self.__snap_data__['engine_context']
			assert ptr is not None, 'no engine_context for reset'

			ptr.setWorldTransform(QTransform())
			#ptr.setClipping(False)
			#ptr.moveTo(0,0) # new path

			ptr.setClipping(True)

			ptr.setRenderHint(QPainter.Antialiasing, False)

			# TODO use ENGINE default color?
			#ptr.setBrush(...)
			#ptr.setPen(...) ?

			# TODO clear config (and re-apply defaults?)

		@ENV.SnapChannel
		def finish(self, MSG):
			engine_context = self['engine_context']
			if engine_context is not None:
				engine_context.end()
				self.__snap_data__['engine_context'] = None

			#self.reset()

		@ENV.SnapChannel
		def clear(self, MSG):
			"()"
			image = self['image']
			if image is not None:
				ctx = self['engine_context']
				mode = ctx.compositionMode()
				ctx.setCompositionMode(QPainter.CompositionMode_Clear)
				self['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX) # for the draw coordinates
				w,h = image['size']
				#self.cmd_fill_extents(ENGINE.Color(1.,1.,1.,0.), snap_extents_t(0,0,0, w,h,1))
				ctx.eraseRect(0,0,w,h) # NOTE: image size is always int
				ctx.setCompositionMode(mode)

		@ENV.SnapChannel
		def set(self, MSG):
			"""(image=SnapQt5Image|SnapImage?)"""
			return SnapContext.set(self, MSG)

			"""
			for attr,value in SETTINGS.items():

				if attr == 'image':

					# verify image ENGINE == self ENGINE?

					self._image_ = value

					ptr = self._engine_context_ = None

					if value is not None:
						#ENV.snap_out('engine data', value.__engine_data__())
						# NOTE: being a bit careful here because init of QPainter(None) will segfault once used!
						qimage = value.__engine_data__()
						assert isinstance(qimage, QImage), 'not a QImage: {}'.format(type(value))
						ptr = self._engine_context_ = Qt5.QPainter(qimage)
						# TODO listen for image changed?

						#cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE)
						ptr.setRenderHint(QPainter.Antialiasing, False)

					#cairo_set_source_rgb(cr, 0,1,1);
					#cairo_rectangle(cr, 0,0, 100, 100);
					#cairo_fill(cr);

					#snap_event((SnapNode*)&value, "SAVE", "path", "/home/user/Desktop/MyComputer/PROGRAMMING/c/PROJECTS/snap/src/internal_rendered.png");

				else:
					SnapContext.set(self, **{attr:value})
			"""

		def __init__(self, **SETTINGS):
			SnapContext.__init__(self, **SETTINGS)

			#self.__needs_update__ = False # when pen and brush are changed this indicates we need to re-set them to the context (best solution I could think of)
			#self.__pen__ = Qt5.QPen()
			#self.__brush__ = Qt5.QBrush()

			#if self._engine_context_:
			#	self.update()

			self['__qimage__'] = self['image']['__engine_data__'] # keep a local reference so it stays alive


	ENGINE.SnapQt5Context = SnapQt5Context
	return SnapQt5Context



