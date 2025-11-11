
def build(ENV):

	SnapTextMetrics = ENV.SnapTextMetrics

	Qt5 = ENV.extern.Qt5

	ENGINE = ENV.graphics.__current_graphics_build__

	snap_extents_t = ENV.snap_extents_t

	"""
	def get_glyph_metrics_with_markup(html_text):
		doc = QTextDocument()
		doc.setHtml(html_text)
		
		# QTextDocument performs the rich text parsing
		# We then iterate through the document structure to access layout details

		# The document is composed of blocks (paragraphs)
		block = doc.begin()
		while block.isValid():
		    # Get the layout for the block
		    layout = block.layout()
		    if layout is None:
		        block = block.next()
		        continue

		    layout.createLine() # Ensure lines are created if not already
		    
		    # Iterate through the lines in the block
		    line = layout.createLine()
		    while line.isValid():
		        # Iterate through the glyphs/characters in the line
		        for i in range(line.textLength()):
		            char_index_in_block = line.textStart() + i
		            # Get the format at this character position to know the applied font
		            char_format = block.charFormat(char_index_in_block)
		            font = char_format.font()
		            
		            # Get character/glyph position relative to the line's start
		            char_pos = line.cursorToX(i)
		            # Get horizontal advance (width) of the character/glyph
		            advance = line.horizontalAdvance(i, 1) # width of 1 character from index i

		            # Bounding rectangle for the glyph
		            # Note: line.naturalTextRect covers the line's bounding box
		            # Calculating the exact glyph bounding box is complex due to bearings,
		            # but horizontalAdvance gives the layout width.
		            
		            # For practical purposes, the advance is often what is needed for layout
		            print(f"Char: '{line.text()[i]}', Font: {font.family()}, Size: {font.pointSize()}, Width: {advance}")
		            
		        line = layout.createLine() # Move to the next line
		    block = block.next()
	"""

	def glyph_extents_qt6(BLOCK, LINE, local_start, local_end):

		if not LINE.isValid():
			return

		i = 0
		while i < LINE.textLength():

			font = BLOCK.charFormat(LINE.textStart() + i).font()
			pos = LINE.cursorToX(i)
			advance = LINE.horizontalAdvance(i, 1)

			print('advance', advance, font.pointSize())

			i += 1

	def glyph_extents_qt5(DOCUMENT, TEXT, LINE, start, end):

		i = start
		x_offset = 0
		while i < end:

			font = DOCUMENT.characterAt(i).charFormat().font()
			metrics = Qt5.QFontMetrics(font)
			char = TEXT[i]
			if char != '\n':
				width = metrics.horizontalAdvance(char)
				rect = [x_offset+LINE.position().x(), y_offset + LINE.position().y(), width, metrics.height()]
				x_offset += width
			else:
				'use full line size'

			i += 1

		"""
		glyph_data = []
		y_offset = 0
		for line in lines:
			x_offset = 0
			for i in range(line.textLength()):
				char_index = line.textStart() + i
				char_format = doc.characterAt(char_index).charFormat()
				font = char_format.font()
				fm = QFontMetrics(font)
				char = line.text()[i]
				if char != '\n':
					width = fm.horizontalAdvance(char)
					# The position relative to the whole document
					rect = QRectF(QPointF(x_offset + line.position().x(), y_offset + line.position().y()), QSizeF(width, fm.height()))
					glyph_data.append({'char': char, 'rect': rect, 'font': font})
					x_offset += width # This is a simplified advance, ignores kerning/ligatures
			y_offset += fm.height() # Simplified line height

		# The most accurate method involves using line.glyphRuns() and run.boundingRects()
		# This requires a QPainter context

		return glyph_data
		"""

	def text_extents_using_glyphruns(self, start=None, end=None):
		

		text = self.__parent__['text']
		qtext = self.__parent__['__engine_data__']

		font_metrics = Qt5.QFontMetricsF(qtext.font())
		space_width = font_metrics.horizontalAdvance(' ')
		tab_width = qtext.tabStopDistance()
		print('tab_width', tab_width, 'space', space_width)

		#print(dir(qtext))

		#qtext.setFixedWidth(300)
		#qtext.adjustSize()
		#qtext.document().documentLayout()

		#widget = Qt5.QWidget()
		
		#window = Qt5.QWidget()
		#layout = Qt5.QVBoxLayout()

		#text_edit.setFixedWidth(200) # Set a fixed width to force wrapping
		#text_edit.append("This is a very long line of text that will definitely wrap multiple times within the fixed width widget.")
		#text_edit.append("Here is another paragraph.")

		#layout.addWidget(qtext)
		#window.setLayout(layout)
		#window.show()
		#layout.removeWidget(qtext)

		#print('begin', dir(qtext))
		#qtext.adjustSize()
		#return snap_extents_t(0,0,0,0,0,0)

		# TODO do word wrap by just getting metrics of unwrapped text and then generating another text with newlines assigned?

		# TODO start and end can be negative, meaning from the end...
		if start is None:
			start = 0
		elif start < 0:
			start = len(text) + start

		assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

		# https://stackoverflow.com/questions/47038001/get-wrapped-lines-of-qtextedit

		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextBlock.html
		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextLine.html
		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html

		ext = snap_extents_t(0,0,0, 0,0,0)

		if start >= end:
			return ext

		#ENV.snap_warning('start', start, 'end', end)

		xs = []
		ys = []

		y_offset = 0

		text_block = qtext.document().begin()
		while 1:
			if not text_block.isValid():
				break
			
			layout = text_block.layout()
			if not layout:
				text_block = text_block.next()
				continue

			block_start, block_end = text_block.position(), text_block.position() + text_block.length()-1 # ignore the next newline character
			block_text = text_block.text()#[line.textStart():line.textStart()+line.textLength()]

			#print('block text', repr(block_text))

			#if block_start > end:
			#	break

			#if start >= (block_start-1) and block_start < end:
			#	rect = layout.boundingRect()
			#	print(repr(block_text), rect.height())
				#return snap_extents_t(rect.x(), y_offset + rect.y(), 0, rect.x() + rect.width(), y_offset + rect.y() + rect.height(), 0)
			#	xs.append(rect.x())
			#	xs.append(rect.x() + rect.width())
			#	#ys.append(y_offset + rect.y())
			#	ys.append(y_offset + rect.y() + rect.height())

			#y_offset += layout.boundingRect().height()
			#print('y_offset', y_offset)

			num_lines = layout.lineCount()
			idx = 0
			while idx < num_lines:
				
				line = layout.lineAt(idx)
				line_text = text_block.text()[line.textStart():line.textStart()+line.textLength()]

				#print('line', idx, repr(line_text), layout.boundingRect(), line.naturalTextWidth(), line.height())

				line_start, line_end = block_start+line.textStart(), block_start+line.textStart()+line.textLength()

				if start > line_end:
					y_offset += line.height()

				elif line_start > end:
					break

				elif start >= (line_start-1) and line_start < end:
					print('in range?', line_start, line_end, line_end-line_start, repr(line_text))

					#print(dir(qtext.document()))
					

					local_start = max(0, start - line_start)
					local_end = end - line_start
					print('local start', local_start, 'local end', local_end, repr(line_text))

					if 0:
						positions = [p for run in (line.glyphRuns(-1,-1) or []) for p in run.positions()]
						print('positions', positions)

						x_offset = 0
						positions_idx = glyph_idx = 0
						for glyph in line_text:
							if glyph_idx < local_start or glyph_idx >= local_end:
								if glyph != '\t':
									positions_idx += 1
							else:
								if glyph == '\t':
									'add tab size'
									# TODO where to get position?  has to be from previous glyph or line start...
									
								else:
									'add position size'
									pt = positions[positions_idx]
									print(pt.x(), pt.y())
									xs.append(pt.x())
									ys.append(pt.y())
									#ys.append(line.height())
									positions_idx += 1
								print('check', repr(line_text[glyph_idx]))
							glyph_idx += 1
					elif 1:

						ys.append(y_offset)
						ys.append(y_offset+line.height())

						sizes = []
						runs = line.glyphRuns(-1, -1)
						if runs:
							for run in runs:
								rawfont = run.rawFont()
								sizes.extend([rawfont.boundingRect(i) for i in run.glyphIndexes()])

						x_offset = 0
						sizes_idx = glyph_idx = 0
						for glyph in line_text:

							if glyph == '\t':
								width = tab_width
							elif glyph == ' ':
								width = space_width
							else:
								rect = sizes[sizes_idx]
								width = rect.width()
								if width == 0:
									ENV.snap_error('0 width', repr(glyph), glyph_idx, rect, repr(line_text))
								sizes_idx += 1

							if glyph_idx < local_start or glyph_idx >= local_end:
								pass
							else:
								xs.append(x_offset)
								xs.append(x_offset+width)

							x_offset += width
							glyph_idx += 1
								


					"""
					#runs = line.glyphRuns(local_start,local_end)
					runs = line.glyphRuns(-1, -1)
					if runs:
						for run in runs:
							rect = run.boundingRect()
							# TODO runs are just visible, tabs are not included...  so we'll have to manage that...
							print('run', rect, run.positions())
							#print('run', dir(run))
							xs.append(rect.x())
							xs.append(rect.x() + rect.width())
							#ys.append(y_offset + rect.y())
							ys.append(y_offset + rect.y() + rect.height())
							#print('rect', rect, xs, ys)
					else:
						# TODO if tabs then get the full bounds and divide it by the chars in the line...
						#rect = line.rect()
						rect = layout.boundingRect()
						xs.append(rect.x())
						xs.append(rect.x() + rect.width())
						ys.append(y_offset + rect.y() + rect.height())
						#print('rect', rect)
					"""

				idx += 1

			text_block = text_block.next()

		if not xs:
			xs = [0]
		if not ys:
			ys = [0]

		return snap_extents_t(min(xs), y_offset, 0, max(xs), max(ys), 0)




	class SnapQt5TextMetrics(SnapTextMetrics):

		__slots__ = []

		def text_extents(self, start=None, end=None):
			'' # TODO return lookup by line start for binary search, with text_block
			# XXX instead of cache just return what is needed for the requested range

			return text_extents_using_glyphruns(self, start, end)

			text = self.__parent__['text']
			qtext = self.__parent__['__engine_data__']

			# TODO start and end can be negative, meaning from the end...
			if start is None:
				start = 0
			elif start < 0:
				start = len(text) + start

			assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

			# https://stackoverflow.com/questions/47038001/get-wrapped-lines-of-qtextedit

			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextBlock.html
			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextLine.html
			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html

			ext = snap_extents_t(0,0,0, 0,0,0)

			if start >= end:
				return ext

			print('start', start, 'end', end)

			xs = []
			ys = []

			y_offset = 0

			ENV.snap_warning('begin')

			font_metrics = qtext.fontMetrics()
			#line_height = font_metrics.size(0, text).height() # TODO get this per line section...? line.height()!
			text_block = qtext.document().begin()
			total_line_idx = 0
			while 1:
				if not text_block.isValid():
					break

				s,e = text_block.position(),text_block.position()+text_block.length()-1 # ignore the next newline character
				layout = text_block.layout()
				if not layout:
					text_block = text_block.next()
					continue

				#ENV.snap_out('text block', s,e, repr(text[s:e]))#, layout.maximumWidth(), layout.minimumWidth(), layout.boundingRect(), dir(layout))

				num_lines = layout.lineCount()
				idx = 0
				while idx < num_lines:
					line = layout.lineAt(idx)
					line_start,line_end = s+line.textStart(), s+line.textStart()+line.textLength()
					line_text = text_block.text()[line.textStart():line.textStart()+line.textLength()]
					#print('\nline', idx, [line_start, line_end], repr(line_text), line.rect(), line.height())

					if start >= (line_start-1) and end <= line_end:
						# size is within the line, return glyph size
						local_start = start - line_start
						local_end = end - line_start
						#print('local start', local_start, 'local_end', local_end, line.textStart(), line.textLength())
						#xs = []
						#ys = []
						#print('select before', xs, ys)
						for run in line.glyphRuns(local_start, local_end):
							rect = run.boundingRect()
							print('bounding rect', y_offset, rect)#, dir(run))
							xs.append(rect.x())
							xs.append(rect.x() + rect.width())
							ys.append(y_offset + rect.y())
							ys.append(y_offset + rect.y() + rect.height())

						if not xs:
							xs = [0]
						if not ys:
							ys = [0]
						#assert len(glyphs) == 1, 'incorrect?'
						#rect = glyphs[0].boundingRect()
						#print('select', xs, ys)
						return snap_extents_t(min(xs), min(ys), 0, max(xs), max(ys), 0)
						
					elif start >= (line_start-1) and line_start < end:
						'include line metrics'
						rect = line.rect()
						#xs.append(rect.x())
						#xs.append(rect.x() + rect.width())
						#ys.append(y_offset + rect.y())
						#ys.append(y_offset + rect.y() + rect.height())
						#print('include', rect, xs, ys, repr(line_text))
						for run in line.glyphRuns(-1,-1):
							''#print(run.boundingRect())

					elif line_start >= end:
						break
						'collect line size in list, then find min/max after?'
						# break if line_start > end
						# if start >= (line_start-1) and line_start < end: include line, add to xs

					y_offset += line.height()
					#print('y_offset', y_offset)

					# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html
					#glyphs = line.glyphRuns(-1, -1) # local start and end
					#for run in glyphs:
					#	''#print('glyphs', run, run.boundingRect())

					#ENV.snap_out('line', font_metrics.size(0, line_text), line.height(), span, repr(line_text))
					idx += 1
					total_line_idx += 1
				#ENV.snap_out('text block', num_lines, text_block.text())#, text_block.size())
				text_block = text_block.next()

			if not xs:
				xs = [0]
			if not ys:
				ys = [0]

			return snap_extents_t(min(xs), min(ys), 0, max(xs), max(ys), 0)

		def __get_data__(self, START, END):
			'return the engine data ready to analyze internally'
			# newlines (textblock), sublines (lines), glyph sizes?

			# TODO just calculate the text size ourselves referring to markups?

			parent = self.__parent__
			if not parent:
				return None

			if parent['__needs_update__']:
				parent.update()
			qtext = parent['__engine_data__']
			if not qtext:
				return None

		def __init__(self, *a, **k):
			SnapTextMetrics.__init__(self, *a, **k)

	ENGINE.SnapQt5TextMetrics = SnapQt5TextMetrics




def main(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	GFX = ENV.GRAPHICS

	class Test(SnapContainer):

		# TODO update extents to resize the graphic and metric display...

		# TODO use the metrics to make some words interactive like SPLAT?  and make an animated explosion graphic?

		#def draw(self, CTX):
		#	''
		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['text']

			def set(self, MSG):
				"(SnapText|str)"
				text = MSG.args[0]
				if isinstance(text, str):
					text = ENV.GRAPHICS.Text(text=text)
				if text is not None:
					assert isinstance(text, ENV.GRAPHICS.Text), 'must be engine text type'
				self.__snap_data__['text'] = text
				self.changed(text=text)

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"

			action,device,source = MSG.unpack('action', None, 'device', None, 'source', None)
			if isinstance(device, ENV.SnapDevicePointer):
				if action == 'press':
					local_position = MSG.kwargs['local_position']
					buttons = device.get('buttons')
					if source == buttons.get('left'):
						ENV.snap_out('left click')
						# set max extents corner of text (or set to min if below)
						#text = self['text']
						#ext = text['extents']
						x,y = local_position
						self['text']['extents'] = snap_extents_t(0,0,0, max(0, x), max(0, y),0)
					elif source == buttons.get('right'):
						ENV.snap_out('right click')
						# set wrap width (and draw line above)
						self['text']['word_wrap_width'] = local_position[0]
					elif source == buttons.get('middle'):
						ENV.snap_out('middle click')
						# clear extents and word wrap
						self['text']['word_wrap_width'] = self['text']['extents'] = None
			

		def draw(self, CTX):
			ext = self['text']['extents']
			if ext:
				CTX.cmd_stroke_extents(GFX.Color(0,0,0,1.), ext)
			return SnapContainer.draw(self, CTX) # text is rendered after


		def animated_outlines(self):

			#ENV.snap_out("called iter begin")

			GFX = ENV.GRAPHICS

			line_outline = GFX.Spline(stroke=GFX.Color(.5,.5,.5,1.))
			glyph_outline = GFX.Spline(stroke=GFX.Color(0., .8, .3, 1.))

			text = self['text']
			m = text['metrics']

			self['children'] = [text, line_outline, glyph_outline]


			def animate_newlines():

				#ENV.snap_out('loop')

				while 1:

					for start,end in m.newlines():
						#ext = m.text_extents(max(0, start-1),end)
						ext = m.text_extents(max(0, start-1),end)
						x1,y1 = ext[0],ext[1]
						x2,y2 = ext[3],ext[4]
						line_outline['description'] = ['S',x1,y1, x2,y1, x2,y2, x1,y2, 'C']
						yield

			def animate_glyphs():

				while 1:

					idx = 0
					while idx < len(text['text']):
						ENV.snap_out(idx, repr(text['text'][idx:idx+1]))
						ext = m.text_extents(idx, idx+1)
						x1,y1 = ext[0],ext[1]
						x2,y2 = ext[3],ext[4]
						glyph_outline['description'] = ['S',x1,y1, x2,y1, x2,y2, x1,y2, 'C']
						idx += 1
						yield

			animations = [animate_newlines(), animate_glyphs()]

			while 1:
				for anim in animations:
					next(anim)
				yield
				

		def __init__(self, *a, **k):
			SnapContainer.__init__(self, *a, **k)

			ENV.snap_out('begin extents', self['extents'][:])

			GFX = ENV.GRAPHICS

			text = """
					one day
					I looked up at the sky
					and...
							*SPLAT*!
					
left
			"""
			#text = "\t\thello\t\tthere"
			#text = 'abc'

			self['text'] = GFX.Text(text=text)#, extents=snap_extents_t(0,0,0, 100,480,0))

			#ENV.snap_out('text extents', self['text']['extents'][:])

			self['children'] = [self['text']]

			self['timer'] = ENV.SnapTimer(self.animated_outlines, seconds=.5)#, repeat=True)

			

	ENV.__run_gui__(Test)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	#SnapEnv().__run__(__file__)
	#SnapEnv().__run__('snap.lib.graphics.engines.qt5.shape.text.SnapQt5TextMetrics')
	main(SnapEnv(graphics='QT5'))

