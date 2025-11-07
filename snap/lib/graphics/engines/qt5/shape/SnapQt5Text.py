
def build(ENV):

	Qt5 = ENV.extern.Qt5

	SnapText = ENV.SnapText

	snap_extents_are_null = ENV.snap_extents_are_null
	snap_debug_engine = snap_debug = ENV.snap_debug
	#snap_emit = ENV.snap_emit

	ENGINE = ENV.graphics.__current_graphics_build__

	snap_extents_t = ENV.snap_extents_t

	def markup_text(TEXT, MARKUPS):

		# TODO make this a function that returns the tags and segment, and calls again for subordinates...

		# https://doc.qt.io/qtforpython-6/overviews/richtext-html-subset.html

		raise NotImplementedError()

		previous_idx = 0

		yield '<html>'

		yield 'hello world!'

		# TODO underline_color, strikeout_color
		# https://doc.qt.io/qt-5/qtextcharformat.html#setUnderlineColor

		yield '</html>'

	class SnapQt5Text(SnapText):

		# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QTextDocument.html#PySide2.QtGui.PySide2.QtGui.QTextDocument.begin

		# https://doc.qt.io/qt-6/qtextedit.html

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE

		@ENV.SnapProperty
		class metrics:
			def get(self, MSG):
				"()->SnapQt5TextMetrics"
				return ENGINE.SnapQt5TextMetrics(self)

		@ENV.SnapChannel
		def update(self, MSG):

			qtext = self.__snap_data__['__engine_data__']
			if qtext is None:
				qtext = self.__snap_data__['__engine_data__'] = Qt5.QTextEdit()

				qtext.setFrameStyle(Qt5.QFrame.NoFrame)
				qtext.setVerticalScrollBarPolicy(Qt5.Qt.ScrollBarAlwaysOff)
				qtext.setHorizontalScrollBarPolicy(Qt5.Qt.ScrollBarAlwaysOff)
				qtext.setStyleSheet("background: rgba(0, 0, 0, 0%);")

			qtext.clear()

			text = self['text']
			markups = self['markups']
			if text is not None:
				if not markups:
					qtext.setPlainText(text)
				else:
					#qtext.setHtml(''.join(list(markup_text(text, markups))))
					# TODO how to set text?
					qtext.setPlainText(text)

					# https://doc.qt.io/qt-5/qtextformat.html#Property-enum

					cursor = qtext.textCursor()

					for name,channel in markups.items():

						for markup in channel:

							char_format = Qt5.QTextCharFormat()

							index,value = markup

							if name == 'bold':
								# https://doc.qt.io/qt-5/qfont.html#Weight-enum

								use = Qt5.QFont.Normal

								incr_high = 100. / 5.
								incr_low = 100. / 3.

								if value > 0.:
									if value <= incr_high * 1: use = Qt5.QFont.Medium
									elif value <= incr_high * 2: use = Qt5.QFont.DemiBold
									elif value <= incr_high * 3: use = Qt5.QFont.Bold
									elif value <= incr_high * 4: use = Qt5.QFont.ExtraBold
									else: use = Qt5.QFont.Black

								elif value < 0.:
									if value >= -1 * incr_low * 1: use = Qt5.QFont.Light
									elif value >= -1 * incr_low * 2: use = Qt5.QFont.ExtraLight
									else: use = Qt5.QFont.Thin

								char_format.setFontWeight(use)

							elif name == 'italic':

								#use = Qt5.QFont.Normal
								use = True if value > 0. else False

								#if value > 0.:
									#if value <= 50.: use = PANGO_STYLE_OBLIQUE
									#else: use = PANGO_STYLE_ITALIC

								#pango_attr = pango_attr_style_new(use)
								char_format.setProperty(Qt5.QTextCharFormat.FontItalic, use)

							elif name == 'size':
								char_format.setProperty(Qt5.QTextCharFormat.FontPointSize, value)

							elif name in ('color', 'foreground_color'):
								brush = Qt5.QBrush(value['__engine_data__'], Qt5.Qt.SolidPattern)
								char_format.setForeground(brush)

							elif name == 'background_color':
								brush = Qt5.QBrush(value['__engine_data__'], Qt5.Qt.SolidPattern)
								char_format.setBackground(brush)

							elif name == 'stretch':
								# https://doc.qt.io/qt-5/qfont.html#Stretch-enum

								use = Qt5.QFont.Unstretched

								if value > 0.:
									if value <= 25.: use = Qt5.QFont.SemiExpanded
									elif value <= 50.: use = Qt5.QFont.Expanded
									elif value <= 75.: use = Qt5.QFont.ExtraExpanded
									else: use = Qt5.QFont.UltraExpanded

								elif value < 0.:
									if value >= -25.: use = Qt5.QFont.SemiCondensed
									elif value >= -50.: use = Qt5.QFont.Condensed
									elif value >= -75.: use = Qt5.QFont.ExtraCondensed
									else: use = Qt5.QFont.UltraCondensed
								
								char_format.setProperty(Qt5.QTextCharFormat.FontStretch, use)

							elif name == 'underline':
								#char_format.setProperty(Qt5.QTextCharFormat.FontUnderline, bool(value))
								use = Qt5.QTextCharFormat.SingleUnderline if value > 0 else None
								char_format.setProperty(Qt5.QTextCharFormat.TextUnderlineStyle, use)

							elif name == 'underline_color':
								char_format.setProperty(Qt5.QTextCharFormat.TextUnderlineColor, value['__engine_data__'])

							elif name == 'strikeout':
								char_format.setProperty(Qt5.QTextCharFormat.FontStrikeOut, bool(value))

							#elif name == 'strikeout_color':
							#	''

							elif name == 'font':
								# just the face
								char_format.setProperty(Qt5.QTextCharFormat.FontFamily, value)

							else:
								snap_debug_engine('unsupported markup', repr(name))
								continue

							cursor.setPosition(index, Qt5.QTextCursor.MoveAnchor)
							if i + 1 < len(channel):
								# end is next markup start
								cursor.setPosition(channel[i+1][0], Qt5.QTextCursor.KeepAnchor)
							else:
								cursor.setPosition(len(text)+1, Qt5.QTextCursor.KeepAnchor)
							cursor.mergeCharFormat(char_format)

							#cursor.clearSelection()


			#qtext.selectAll()
			#cursor = qtext.textCursor()
			#block_format = cursor.blockFormat()
			#block_format.setLineHeight(80, Qt5.QTextBlockFormat.ProportionalHeight)
			#cursor.setBlockFormat(block_format)
			#cursor.clearSelection()
			#qtext.setTextCursor(cursor)

			ext = self['extents']
			if ext is None:
				qtext.document().adjustSize()
				size = qtext.document().size()
				ext = self.__snap_data__['extents'] = snap_extents_t(0,0,0, size.width(), size.height(), 0)

			if 0:#snap_extents_are_null(ext):
				# TODO set unbounded
				qtext.setLineWrapMode(Qt5.QTextEdit.NoWrap) # TODO always?  we'll do wrap ourself?
				#pango_layout_set_width(layout, -1)
				#pango_layout_set_height(layout, -1)

			else:
				#qtext.setLineWrapMode(Qt5.QTextEdit.WidgetWidth)
				ENV.snap_out('text extents for wrap', ext[:])
				qtext.setLineWrapColumnOrWidth(min(20, int(ext[3]-ext[0])))
				#pango_layout_set_width(layout, int(ext[3]-ext[0]))
				#pango_layout_set_height(layout, int(ext[4]-ext[1]))
				#qtext.setGeometry(int(ext[0]), int(ext[1]), int(ext[3]-ext[0]), int(ext[4]-ext[1]))
				geo = qtext.geometry()
				#qtext.setGeometry(geo.x(), geo.y(), max(300, geo.width()), geo.height())
				#ENV.snap_out('ext', qtext.geometry())

			# TODO use a cursor to find the text size?
				
			"""
			# TODO update matrix get_pixel_extents()

			# https://developer.gnome.org/pango/stable/pango-Layout-Objects.html#pango-layout-get-pixel-extents
			#pango_layout_get_pixel_extents(layout);
			# https://developer.gnome.org/pango/stable/pango-Layout-Objects.html#pango-layout-get-extents
			# "Logical extents are usually what you want for positioning things."
			inkext = PangoRectangle()
			textext = PangoRectangle()
			pango_layout_get_pixel_extents(layout, inkext, textext) # TODO this needs to be implemented as byref
			#pango_layout_get_extents(layout, &inkext, &textext);
			#pext.x /= PANGO_SCALE;
			#pext.y /= PANGO_SCALE;
			#pext.width /= PANGO_SCALE;
			#pext.height /= PANGO_SCALE;
			#double text_ext[] = {(double)textext.x, (double)textext.y, 0., (double)(textext.x + textext.width), (double)(textext.y + textext.height), 0.};
			self.text_extents = snap_extents_t(textext.x, textext.y, 0., textext.x + textext.width, textext.y + textext.height, 0.)
			#double ink_ext[] = {(double)inkext.x, (double)inkext.y, 0., (double)(inkext.x + inkext.width), (double)(inkext.y + inkext.height), 0.};
			self.ink_extents = snap_extents_t(inkext.x, inkext.y, 0., inkext.x + inkext.width, inkext.y + inkext.height, 0.)

			# TODO if extents is 0 then make it fit the text?  self._extents_ is designated by user, use ink_extents or text_extents for text metrics...
			# TODO make it easier by storing all the extents on the class and updating them all on each change... much easier
			# if self.text_extents or self.ink_extents are null, then use self.extents by default
			# TODO layout size will be set to self.extents, use "GET" to get ink and text extents, and update if dirty beforehand

			# TODO store text and ink extents as x,y,w,h bounds relative to extents, but return as proper extents when queried
			"""

			if 0:
				geo = qtext.geometry()
				#qtext.setMaximumWidth(50)
				qtext.document().adjustSize()
				size = qtext.document().size()

				#ENV.snap_out('doc size', geo, size.width(), size.height())

				# TODO better font metrics?  for now we're just going to set the full text visible...
				ext = self.__snap_data__['extents'] = self.__snap_data__['text_extents'] = self.__snap_data__['ink_extents'] = snap_extents_t(geo.x(), geo.y(), 0, geo.x() + size.width(), geo.y() + size.height(), 0)
				qtext.setGeometry(int(ext[0]), int(ext[1]), int(ext[3]-ext[0]), int(ext[4]-ext[1]))
			else:
				qtext.document().adjustSize()
				size = qtext.document().size()
				geo = qtext.geometry()

				#metrics = qtext.fontMetrics()
				#t = 'hello world'
				#print('rect', metrics.boundingRect(t), metrics.tightBoundingRect(t))

				#height = metrics.xHeight()
				#height = metrics.ascent() + metrics.descent()
				#width = metrics.lineWidth()
				#size = metrics.size(0, text)

				#bnd = metrics.boundingRect(text)

				#ENV.snap_out('leading', metrics.leading(), 'height', height, size, 'line', metrics.lineSpacing(), 'advance', metrics.horizontalAdvance(text))
				#ENV.snap_out('bound', bnd.width(), bnd.height(), 'size', size.width(), size.height())

				w = size.width()
				h = size.height() # this is the correct height of each line...

				#ENV.snap_out('geo', geo, geo.height() / h, len(text), 'x', metrics.xHeight())

				ENV.snap_out('size', w,h)
				#ENV.snap_out('geo', geo, geo.x(), geo.y(), geo.width(), geo.height())
				ext = self.__snap_data__['extents'] = self.__snap_data__['text_extents'] = self.__snap_data__['ink_extents'] = snap_extents_t(0, 0, 0, w, h, 0)
				#ENV.snap_out('ext', ext[:], h, 'size', size)
				#qtext.document().adjustSize()
				doc_size = qtext.document().size()
				ENV.snap_out('text geometry set', int(ext[0]), int(ext[1]), int(doc_size.width()), int(doc_size.height()))
				qtext.setGeometry(int(ext[0]), int(ext[1]), int(doc_size.width()), int(doc_size.height())) # TODO why is this size not correct?


			#self.changed() XXX changed should have gone out separate from update() call...  (what triggered the update?) # TODO args?

			#self['extents'] = self['text_extents'] # TODO nicer way?


			# https://stackoverflow.com/questions/47038001/get-wrapped-lines-of-qtextedit

			# TODO make a 'metrics' property of text, implement in engine, return lines block, lines have sublines (for wrap), you can get text_extents and ink_extents for each?
			"""
			font_metrics = qtext.fontMetrics()
			line_height = font_metrics.size(0, text).height() # TODO get this per line section...? line.height()!
			text_block = qtext.document().begin()
			while 1:
				layout = text_block.layout()
				if not layout:
					break
				num_lines = layout.lineCount()
				idx = 0
				while idx < num_lines:
					line = layout.lineAt(idx)
					span = [line.textStart(), line.textStart()+line.textLength()]
					line_text = text_block.text()[span[0]:span[1]]
					#print('line start', line.textStart(), repr(line_text))
					#ENV.snap_out('line', font_metrics.size(0, line_text), line.height(), span, repr(line_text))
					idx += 1
				#ENV.snap_out('text block', num_lines, text_block.text())#, text_block.size())
				text_block = text_block.next()
			"""

			#ENV.snap_out('updated')
			return None



		#def lookup(self, CTX):
		#	''#ENV.snap_out('TODO: text lookup')


		def __init__(self, text=None, **SETTINGS):
			SnapText.__init__(self, text=text, **SETTINGS)


	ENGINE.SnapQt5Text = SnapQt5Text
	return SnapQt5Text

if __name__ == '__main__':

	from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	from snap.lib import extern, graphics
	extern.build(ENV)
	graphics.build(ENV)
	build(ENV)

	Qt5 = ENV.Qt5

	class TestWidget(Qt5.QWidget):

		def paintEvent(self, *args, **kwargs):

			with Qt5.QPainter(self) as ptr:

				#ptr.drawText(100,100, "hello world")

				#ptr.drawStaticText(0,0, self.static_text)

				pth = Qt5.QPainterPath()
				pth.addRect(10,10,250,250)
				ptr.setClipPath(pth)

				ptr.save()

				pth2 = Qt5.QPainterPath()
				pth2.addRect(100,100,110,110)
				ptr.setClipPath(pth2)

				ptr.restore()

				#self.document.drawContents(ptr)#, rect=None)
				#self.textedit.document().drawContents(ptr) #, rect=None)
				self.textedit.render(ptr)

				doc = self.textedit.document()			
				#print('doc', self.textedit.geometry(), doc.size())
				ptr.drawRect(self.textedit.x(),self.textedit.y(), int(doc.size().width()), int(doc.size().height()))

				#self.textedit.selectAll()
				#cursor = self.textedit.textCursor()
				
				

		def resizeEvent(self, *args, **kwargs):
			geo = self.geometry()
			self.textedit.setGeometry(0,0, geo.width(), geo.height())

		def __init__(self):
			Qt5.QWidget.__init__(self)

			with open(__file__, 'r') as openfile:
				file_contents = openfile.read()

			self.static_text = Qt5.QStaticText()
			self.static_text.setText(file_contents)

			self.document = Qt5.QTextDocument()
			self.document.setPlainText(file_contents)
			#self.document.setHtml("<html><italic>hello everybody!</italic></html>")

			self.textedit = Qt5.QTextEdit()
			self.textedit.setPlainText(file_contents)
			#self.textedit.setPlainText('hello world')

			if 0:
				self.textedit.setHtml("""
					<font color='red' size='6'><red>Hello PyQt5!\nHello</font> and outside
					<font color='blue'><s>strikethrough</s></font>
					<u'>underlined</u>

					""")

			self.textedit.setTextBackgroundColor(Qt5.QColor(0,0,0,0))
			self.textedit.setHorizontalScrollBarPolicy(Qt5.Qt.ScrollBarAlwaysOff)
			self.textedit.setVerticalScrollBarPolicy(Qt5.Qt.ScrollBarAlwaysOff)
			#self.textedit.setAttribute(Qt5.Qt.WA_TranslucentBackground)
			self.textedit.setStyleSheet("background: rgba(0,0,0,0)")
			self.textedit.setGeometry(self.geometry())

			self.textedit.setLineWrapMode(Qt5.QTextEdit.NoWrap)

			cursor = Qt5.QTextCursor(self.textedit.textCursor())
			cursor.beginEditBlock()
			#cursor.movePosition(Qt5.QTextCursor.StartOfWord)
			#cursor.movePosition(Qt5.QTextCursor.EndOfWord, Qt5.QTextCursor.KeepAnchor)
			#cursor.insertText("blah blah blah")
			cursor.endEditBlock()

			#print(self.textedit.document())
			
			#print(self.document.toHtml())


			# formatting test
			# https://www.qtcentre.org/threads/71578-Apply-the-outline-of-a-QTextCharFormat-only-on-the-outside-of-the-text
			cursor = self.textedit.textCursor()
			#char_format = cursor.charFormat()

			char_format = Qt5.QTextCharFormat()

			#char_format.setTextOutline(Qt5.QPen(Qt5.Qt.GlobalColor.red, 5))
			brush = Qt5.QBrush(Qt5.QColor(255,0,0,255), Qt5.Qt.SolidPattern)
			char_format.setForeground(brush)
			char_format.setFontWeight(Qt5.QFont.Black)

			#char_format.setProperty(Qt5.QTextCharFormat.FontItalic, 1)
			#char_format.setProperty(Qt5.QTextCharFormat.FontFamily, "Bitstream Charter")

			#print(char_format.property(Qt5.QTextCharFormat.FontFamily))

			cursor.setPosition(10, Qt5.QTextCursor.MoveAnchor)
			cursor.setPosition(200, Qt5.QTextCursor.KeepAnchor)
			#cursor.select(Qt5.QTextCursor.SelectionType.Document)
			cursor.mergeCharFormat(char_format)

			cursor.clearSelection()


			char_format.setFontWeight(Qt5.QFont.Thin)
			#char_format.setProperty(Qt5.QTextCharFormat.FontPointSize, 32)
			#char_format.setProperty(Qt5.QTextCharFormat.FontPixelSize, 50)
			char_format.setBackground(Qt5.QBrush(Qt5.QColor(0,0,255,255), Qt5.Qt.SolidPattern))
			char_format.setBackground(Qt5.QBrush(Qt5.QColor(0,0,0,0), Qt5.Qt.SolidPattern))
			#char_format.setProperty(Qt5.QTextCharFormat.FontStretch, Qt5.QFont.UltraCondensed)
			#char_format.setProperty(Qt5.QTextCharFormat.FontItalic, -1)
			#char_format.setProperty(Qt5.QTextCharFormat.TextUnderlineStyle, Qt5.QTextCharFormat.SingleUnderline)

			cursor.setPosition(50, Qt5.QTextCursor.MoveAnchor)
			cursor.setPosition(150, Qt5.QTextCursor.KeepAnchor)
			cursor.mergeCharFormat(char_format)


			#print(Qt5.QFontDatabase().families(Qt5.QFontDatabase.Latin))

			print('metrics', self.textedit.fontMetrics())



	W = TestWidget()
	W.show()
	Qt5._app_.exec()

