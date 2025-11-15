
def build(ENV):

	Qt5 = ENV.extern.Qt5

	QSizeF = Qt5.QSizeF

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

		#@ENV.SnapProperty
		#class metrics:
		#	def get(self, MSG):
		#		"()->SnapQt5TextMetrics"
		#		return ENGINE.SnapQt5TextMetrics(self)

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
				qtext.setPlainText(text)
				if markups:

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


			document = qtext.document()

			# first find the actual text size
			qtext.setLineWrapMode(Qt5.QTextEdit.NoWrap)
			full_size = document.size()
			
			# word wrap is set separately from extents
			# (extents represent bounds of document, and can crop)
			word_wrap_width = self['word_wrap_width']
			if word_wrap_width is not None:
				WRAP_WIDTH = max(0, word_wrap_width)
			else:
				WRAP_WIDTH = document.size().width()

			qtext.setLineWrapMode(Qt5.QTextEdit.FixedPixelWidth)
			qtext.setLineWrapColumnOrWidth(int(WRAP_WIDTH))
			document.setTextWidth(WRAP_WIDTH)

			ext = self['extents']
			if ext is None:
				DOC_WIDTH = WRAP_WIDTH # TODO also get from cursor?  but that would mean widest line, would have to check all!
				#DOC_HEIGHT = document.size().height()
				cursor = qtext.textCursor()
				cursor.setPosition(len(text))
				rect = qtext.cursorRect(cursor)
				DOC_HEIGHT = rect.y() + rect.height() + 10 # +10 because if we set to exactly the height the last line is wrong...
			else:
				DOC_WIDTH = ext[3]-ext[0]
				DOC_HEIGHT = ext[4]-ext[1]

			document.setPageSize(QSizeF(WRAP_WIDTH, DOC_HEIGHT))

			qtext.setGeometry(0, 0, int(DOC_WIDTH), int(DOC_HEIGHT))


			return None



		#def lookup(self, CTX):
		#	''#ENV.snap_out('TODO: text lookup')


####### Metrics

		def glyph_at_position(self, X, Y):

			# using binary search algorithm

			string = self['text']
			qtext = self['__engine_data__']

			cursor = qtext.textCursor()

			L = 0
			R = len(string)-1

			while R >= L:
				C = (L + R) // 2

				cursor.setPosition(C)
				rect = qtext.cursorRect(cursor)

				x,y,h = rect.x(),rect.y(),rect.height()

				# compare line/y first, once it succeeds, then proceed to comparing glyph/x
				if Y < y:
					R = C - 1
				elif Y > y + h:
					L = C + 1

				# then compare glyph/x, once Y is in line range...
				elif X < x:
					R = C - 1
				elif X > x:
					# now we need to verify we are within the glyph, not just > min
					# (or it will advance to the next position!)
					cursor.setPosition(C + 1)
					next_rect = qtext.cursorRect(cursor)
					if next_rect.y() > y:
						# if the next glyph/x would be on the next line/y,
						# then this glyph/x is the best match possible, return it
						return C
					if X < next_rect.x():
						# X < next x; this is the glyph/x
						return C
					else:
						# glyph is still to the right (but in this line/y)
						L = C + 1
				else:
					R = C - 1
					continue # run to end / closest match

			return L # run to end / closest match

		def line_at_position(self, X, Y):

			glyph_idx = self.glyph_at_position(X,Y)

			qtext = self['__engine_data__']

			cursor = qtext.textCursor()

			cursor.setPosition(glyph_idx)
			block = cursor.block()

			# NOTE: this is between newlines (QTextBlock does not contain newlines)
			s = block.position()
			e = s + block.length()-1 # -1 to exclude the newline

			return s,e

		def subline_at_position(self, X, Y):

			line_span = self.line_at_position(X,Y)

			# TODO then we want to find each wrapped line, but from the cursor...

			raise NotImplementedError()

		def glyph_extents(self, INDEX):

			qtext = self['__engine_data__']
			text = self['text']

			text_length = len(text)

			if INDEX >= text_length:
				INDEX = text_length

			cursor = qtext.textCursor()
			cursor.setPosition(INDEX)
			#cursor.setPosition(INDEX+1, QTextCursor.KeepAnchor)

			first_rect = qtext.cursorRect(cursor)

			cursor.setPosition(min(text_length, INDEX+1))

			second_rect = qtext.cursorRect(cursor)

			return snap_extents_t(first_rect.x(), first_rect.y(), 0, second_rect.x(), first_rect.y() + second_rect.height(), 0)


		def text_extents(self, start=None, end=None):

			qtext = self['__engine_data__']
			text = self['text']
			text_length = len(text)

			# TODO start and end can be negative, meaning from the end...
			if start is None:
				start = 0
			elif start < 0:
				start = max(0, text_length - abs(start))

			# TODO end < 0 from end as well?
			if end is None:
				end = text_length
			if end < start:
				end = start
			if end > text_length:
				end = text_length

			#assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

			cursor = qtext.textCursor()

			cursor.setPosition(start)
			block = cursor.block()
			cursor.setPosition(block.position())
			rect = qtext.cursorRect(cursor)

			first_rect = rect

			#ENV.snap_out('text_extents', [start,end], [block.position(), min(text_length, block.position()+block.length()-1)], repr(text[start:end]), rect)

			minpoint = [rect.x(), rect.y()]

			if 0:
				cursor.setPosition(end)
				block = cursor.block()
				cursor.setPosition(block.position() + block.length()-1)
				rect = qtext.cursorRect(cursor)
			else:
				# if multi-subline, rather than check the size of each subline,
				# just set the width to the wrap width to be more efficient...
				# since multi-subline guarantees we're > word_wrap_width
				cursor.setPosition(end, Qt5.QTextCursor.KeepAnchor)
				block = cursor.block()
				cursor.setPosition(block.position() + block.length()-1)
				rect = qtext.cursorRect(cursor)

				if rect.y() == minpoint[1]:
					#print('inline', repr(text[start:end]))
					WIDTH = rect.x()+rect.width()
				else:
					#print('not inline', repr(text[start:end]), self['word_wrap_width'])
					WIDTH = self['word_wrap_width']

			#ENV.snap_out('text_extents', [start,end], repr(text[start:end]), first_rect.y(), rect.y()+rect.height(), (minpoint[0], minpoint[1], 0, rect.x(), rect.y()+rect.height(),0))

			#return snap_extents_t(minpoint[0], minpoint[1], 0, rect.x()+rect.width(), rect.y()+rect.height(), 0)
			return snap_extents_t(minpoint[0], minpoint[1], 0, WIDTH, rect.y()+rect.height(),0)



		def newlines(self):
			# returns list of spans representing the body of each newline (ignoring word wrap, use sublines for all lines)

			text = self['text']

			# we need to backup the start to newline if it isn't at the start of one...
			# XXX just get list of all newline indices, and then check if one after <= start?  or next newline < end?
			#while start > 0 and text[start] != '\n':
			#	start -= 1

			# spans are returned without the newline character included
			indices = [0] + [idx+1 for idx,val in enumerate(text) if val == '\n'] + [len(text)]
			return [(indices[idx], indices[idx+1]-1) for idx in range(len(indices)-1)]

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

